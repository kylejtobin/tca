import json
from datetime import date

import httpx
import pytest
from pydantic import ValidationError

from type_construction.registrar import (
    Offer,
    RegistrarConfig,
    RegistrationRequest,
    check,
    check_sync,
    register,
    register_sync,
)
from type_construction.registrar.domain.registration.name import (
    AvailableName,
    PremiumName,
    RefusedName,
    RegisteredName,
    ReservedName,
    TakenName,
)
from type_construction.registrar.domain.registration.type import (
    Amount,
    Currency,
    ExpiryDate,
    Fqdn,
    Invariant,
    RefusalReason,
    RegistrantId,
    RegistrationId,
    StatedRefusal,
    Term,
    UnlistedRefusal,
)
from type_construction.registrar.domain.registration.value import (
    Cost,
    Grant,
    Holding,
    Quote,
)
from type_construction.registrar.integration.registrar.provider import Registrar

URL = "https://registrar.example"
KEY = "secret-key-value"
REQUEST = RegistrationRequest(
    registrant=RegistrantId("acct_42"),
    name=Fqdn("example.com"),
    term=Term(2),
)
OFFER = Offer(
    AvailableName(request=REQUEST, standing=Quote(price=1200, currency=Currency.USD))  # pyright: ignore[reportArgumentType]
)


@pytest.fixture
def config(monkeypatch: pytest.MonkeyPatch) -> RegistrarConfig:
    monkeypatch.setenv("REGISTRAR__URL", URL)
    monkeypatch.setenv("REGISTRAR__KEY", KEY)
    return RegistrarConfig()  # pyright: ignore[reportCallIssue]


def answering(monkeypatch: pytest.MonkeyPatch, body: str) -> list[httpx.Request]:
    """Make every registrar client answer with one body, and keep what was sent."""
    sent: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        sent.append(request)
        return httpx.Response(200, content=body)

    monkeypatch.setattr(
        Registrar,
        "client",
        property(
            lambda self: httpx.AsyncClient(  # pyright: ignore[reportUnknownLambdaType, reportUnknownMemberType]
                transport=httpx.MockTransport(handler),
                base_url=self.url.root,  # pyright: ignore[reportUnknownMemberType]
                auth=(self.key.root.get_secret_value(), ""),  # pyright: ignore[reportUnknownMemberType]
            )
        ),
    )
    return sent


def test_the_deployment_names_the_registrar_by_nested_name(config: RegistrarConfig) -> None:
    assert config.registrar.url.root == URL
    assert config.registrar.key.root.get_secret_value() == KEY
    assert KEY not in repr(config)
    assert KEY not in config.model_dump_json()


def test_the_registrar_is_absent_without_its_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("REGISTRAR__URL", URL)
    monkeypatch.delenv("REGISTRAR__KEY", raising=False)
    with pytest.raises(ValidationError):
        RegistrarConfig()  # pyright: ignore[reportCallIssue]


@pytest.mark.parametrize(
    ("body", "variant", "cost"),
    (
        (
            '{"status": "available", "price": 1200, "currency": "usd"}',
            AvailableName,
            Cost(amount=Amount(2400), currency=Currency.USD),
        ),
        (
            '{"status": "premium", "premium": 250000, "renewal": 1200, "currency": "usd"}',
            PremiumName,
            Cost(amount=Amount(251200), currency=Currency.USD),
        ),
    ),
)
def test_an_offered_name_costs_its_term(
    config: RegistrarConfig,
    monkeypatch: pytest.MonkeyPatch,
    body: str,
    variant: type[AvailableName | PremiumName],
    cost: Cost,
) -> None:
    sent = answering(monkeypatch, body)
    availability = check_sync(config, REQUEST)
    assert type(availability.root) is variant
    assert Offer.model_validate(availability.root).cost == cost
    assert [(r.method, str(r.url)) for r in sent] == [("GET", f"{URL}/availability/example.com")]
    assert sent[0].headers["authorization"] == "Basic c2VjcmV0LWtleS12YWx1ZTo="


@pytest.mark.parametrize(
    ("body", "variant"),
    (
        ('{"status": "taken", "expires": "2027-03-01"}', TakenName),
        ('{"status": "reserved", "policy": "icann-reserved"}', ReservedName),
    ),
)
def test_a_name_that_cannot_be_had_is_not_an_offer(
    config: RegistrarConfig,
    monkeypatch: pytest.MonkeyPatch,
    body: str,
    variant: type[TakenName | ReservedName],
) -> None:
    answering(monkeypatch, body)
    availability = check_sync(config, REQUEST)
    assert type(availability.root) is variant
    assert availability.request == REQUEST
    with pytest.raises(ValidationError):
        Offer.model_validate(availability.root)


def test_a_taken_name_is_not_an_offer_by_construction() -> None:
    taken = TakenName(request=REQUEST, standing=Holding(expires=ExpiryDate(date(2027, 3, 1))))
    with pytest.raises(ValidationError):
        Offer.model_validate(taken)


def test_a_registration_is_ordered_in_the_registrars_terms(
    config: RegistrarConfig, monkeypatch: pytest.MonkeyPatch
) -> None:
    sent = answering(monkeypatch, '{"id": "reg_9f1c", "expires": "2028-03-01"}')
    outcome = register_sync(config, OFFER)
    assert type(outcome.root) is RegisteredName
    assert outcome.answer == Grant(
        id=RegistrationId("reg_9f1c"), expires=ExpiryDate(date(2028, 3, 1))
    )
    assert outcome.offer == OFFER
    assert [(r.method, str(r.url)) for r in sent] == [("POST", f"{URL}/registrations")]
    assert json.loads(sent[0].content) == {
        "name": "example.com",
        "years": 2,
        "registrant": "acct_42",
        "amount": 2400,
        "currency": "usd",
    }


def test_a_refusal_keeps_every_reason_the_registrar_gave(
    config: RegistrarConfig, monkeypatch: pytest.MonkeyPatch
) -> None:
    answering(monkeypatch, '{"refusals": ["object_exists", "weird_reason"]}')
    outcome = register_sync(config, OFFER)
    assert type(outcome.root) is RefusedName
    assert tuple(reason.root for reason in outcome.root.answer.reasons.root) == (
        RefusalReason.OBJECT_EXISTS,
        UnlistedRefusal("weird_reason"),
    )


@pytest.mark.asyncio
async def test_the_crossings_run_in_one_loop(
    config: RegistrarConfig, monkeypatch: pytest.MonkeyPatch
) -> None:
    answering(monkeypatch, '{"status": "available", "price": 1200, "currency": "usd"}')
    availability = await check(config, REQUEST)
    answering(monkeypatch, '{"id": "reg_9f1c", "expires": "2028-03-01"}')
    outcome = await register(config, Offer.model_validate(availability.root))
    assert type(outcome.root) is RegisteredName


def test_a_name_is_its_written_form_and_only_a_writable_one() -> None:
    assert Fqdn("www.example.com").root == "www.example.com"
    for written in ("", "example", "-bad.com", "example.c", "a..b.com", "Example.com"):
        with pytest.raises(ValidationError):
            Fqdn(written)
    longest = ".".join(("a" * 63, "b" * 63, "c" * 63, "d" * 57, "com"))
    assert len(Fqdn(longest).root) == 253
    with pytest.raises(ValidationError, match="at most 253 characters"):
        Fqdn(".".join(("a" * 63, "b" * 63, "c" * 63, "d" * 57, "e", "com")))


def test_an_unlisted_refusal_is_one_this_program_has_no_word_for() -> None:
    assert StatedRefusal.model_validate_json('"object_exists"').root is RefusalReason.OBJECT_EXISTS
    assert StatedRefusal.model_validate_json('"introduced_later"').root == UnlistedRefusal(
        "introduced_later"
    )
    with pytest.raises(ValidationError, match=Invariant.UNLISTED_REFUSAL):
        UnlistedRefusal("object_exists")
    with pytest.raises(ValidationError):
        StatedRefusal.model_validate_json('""')
