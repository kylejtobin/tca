"""Decisions, and the effects that depend on them.

An applicant is admitted when the registrar allows it and the welcome desk has been pinged. The
registrar may allow or deny; the desk, when pinged, pings. Where the business means the ping to
wait for the allowance, it says so: the ping is demanded ``When`` the allowance is established.
Where it says nothing, both are demanded jointly. The other programs vary that one
relationship: a fallback outcome for the denial; two effects nothing declared decides between;
the same two decided by a rating; two effects both needed with nothing to decide; two decisions
at once; a consumer that wants the desk told after a denial, which the desk's own requirement
forbids; one operation demanded jointly and conditionally; a chain of conditions; a conditional
inside an alternative.

The conditional is a type, so it composes as types do: under a business name, as a generic
subclass, under ``Annotated`` metadata, with a premise of its own beside it. Each form is the
same relationship. A condition that may be established without the effect it governs, through
one member of an alternative, is a condition; a relation over two business constants is a
condition established from nothing, or refuted from nothing.
"""

from decimal import Decimal
from typing import Annotated, Self

from pydantic import Field, ValidationInfo, model_validator

from type_construction.program import Correlation, Interaction, Program, Source, When
from type_construction.world import AtMost, Beyond, Equal, Fact, Record, Scalar, Value


class Name(Scalar[str]):
    root: str = Field(min_length=1)


class Reason(Scalar[str]):
    root: str = Field(min_length=1)


class Applicant(Value):
    name: Name


class Admit(Value):
    """The command: admit this applicant."""

    applicant: Applicant


class CheckRequest(Value):
    """What the program sends the registrar: may this applicant be admitted?"""

    applicant: Applicant


class Allowed(Record):
    applicant: Name


class Denied(Record):
    applicant: Name
    reason: Reason


class PingRequest(Value):
    """What the program sends the welcome desk: an applicant is coming. It needs nothing but the
    applicant, so it could be sent at once."""

    applicant: Applicant


class Pinged(Record):
    applicant: Name


class Granted(Fact):
    """The outcome: allowed, and the desk pinged once allowed. The ping is demanded only when
    the registrar's allowance is established; a denial never pings."""

    allowed: Allowed
    pinged: When[Allowed, Pinged]


class Jointly(Fact):
    """Allowed and pinged, both demanded jointly: nothing here says the ping waits, so the desk
    is pinged while the registrar is asked, and a denial leaves the applicant pinged and not
    admitted."""

    allowed: Allowed
    pinged: Pinged


class Desk(Fact):
    """The desk's ping, wrapped in an ordinary fact with no validator: plain composition."""

    pinged: Pinged


class GrantedViaDesk(Fact):
    allowed: Allowed
    desk: When[Allowed, Desk]


class CheckedDesk(Fact):
    """The desk's ping behind an opaque identity validator: it changes nothing and the evaluator
    cannot know that."""

    pinged: Pinged

    @model_validator(mode="after")
    def _same(self) -> Self:
        return self


class GrantedViaCheckedDesk(Fact):
    allowed: Allowed
    desk: When[Allowed, CheckedDesk]


class Enclosed(Fact):
    """The conditional ping inside a plain fact: the wrapper around the ``When``."""

    pinged: When[Allowed, Pinged]


class GrantedViaEnclosed(Fact):
    allowed: Allowed
    enclosed: Enclosed


class Rejected(Fact):
    """The fallback outcome: denied."""

    denied: Denied


class Decision(Fact):
    outcome: Granted | Rejected


class MailRequest(Value):
    applicant: Applicant


class Mailed(Record):
    applicant: Name


class TextRequest(Value):
    applicant: Applicant


class Texted(Record):
    applicant: Name


class Welcomed(Fact):
    """Two effects, both needed, neither able to refuse."""

    pinged: Pinged
    mailed: Mailed


class ByMail(Fact):
    mailed: Mailed


class ByText(Fact):
    texted: Texted


class Notified(Fact):
    """Mailed or texted: two effects, and nothing declared says which."""

    how: ByMail | ByText


class Rating(Scalar[Decimal]):
    root: Decimal = Field(ge=0)


class Threshold(Scalar[Decimal]):
    root: Decimal = Decimal(10)


class RateRequest(Value):
    applicant: Applicant


class Rated(Record):
    applicant: Name
    rating: Rating


class Low(AtMost[Rating, Threshold]):
    """A rating at or under the threshold."""


class High(Beyond[Rating, Threshold]):
    """A rating over the threshold."""


class MailedLow(Fact):
    low: Low
    mailed: Mailed


class TextedHigh(Fact):
    high: High
    texted: Texted


class NotifiedByRating(Fact):
    """Mailed or texted, as the rating decides."""

    how: MailedLow | TextedHigh


class ScreenRequest(Value):
    applicant: Applicant


class Clear(Record):
    applicant: Name


class Flagged(Record):
    applicant: Name
    reason: Reason


class Cleared(Fact):
    """Two decisions, both needed."""

    allowed: Allowed
    clear: Clear


class Processed(Fact):
    """Two decisions inside one fact, and a mail sent once both are made."""

    cleared: Cleared
    mailed: When[Cleared, Mailed]


class NotifyRequest(Value):
    """What the program sends the desk about an allowed applicant: it requires the allowance."""

    allowed: Allowed


class Told(Record):
    applicant: Name


class Welcome(Fact):
    allowed: Allowed
    told: Told


class Consoled(Fact):
    """A consumer that wants the desk told after a denial: it demands ``Told``, and cannot weaken
    what ``NotifyRequest`` requires."""

    denied: Denied
    told: Told


class Handled(Fact):
    outcome: Welcome | Consoled


class VettedCheckRequest(Value):
    """A registrar check that needs the desk pinged first: the decision depends on another
    result."""

    pinged: Pinged


class VettedGranted(Fact):
    allowed: Allowed
    pinged: Pinged


class Approved(Record):
    applicant: Name


class Refused(Record):
    applicant: Name
    reason: Reason


class Endorsed(Fact):
    """A decision nothing is sent for: the committee approves or refuses on its own, and the
    desk is pinged once it approves."""

    approved: Approved
    pinged: When[Approved, Pinged]


class Withdrawal(Record):
    applicant: Name


class Withdrawn(Fact):
    """The applicant withdrew: a passive alternative nothing can refuse."""

    withdrawal: Withdrawal


class Resolved(Fact):
    """Granted or withdrawn, and the applicant mailed either way."""

    outcome: Granted | Withdrawn
    mailed: Mailed


class Shared(Fact):
    """One ping demanded twice: jointly, and again once the allowance is established."""

    direct: Pinged
    later: When[Allowed, Pinged]


class SharedReversed(Fact):
    """The same as ``Shared``, with the conditional declared first."""

    later: When[Allowed, Pinged]
    direct: Pinged


class Twice(Fact):
    """One conditional ping held at two places: one construction, demanded twice."""

    one: Enclosed
    two: Enclosed


class Chained(Fact):
    """The mail demanded once the ping is there, and the ping once the allowance is."""

    mailed: When[Allowed, When[Pinged, Mailed]]


class Either(Fact):
    """The desk pinged once allowed, or the applicant rejected: a conditional as one member of
    an alternative."""

    outcome: When[Allowed, Pinged] | Rejected


class ApprovedPing(When[Allowed, Pinged]):
    """The conditional ping under a business name: a subclass of the relationship, which has it
    whole."""


class Once[R](When[Allowed, R]):
    """A conditional on the allowance, open in what it demands: a generic subclass."""


class NotedPing(When[Allowed, Pinged]):
    """The conditional ping with a premise of its own beside it: the applicant, held with the
    condition, not behind it."""

    applicant: Applicant


class PingAndMail(When[Allowed, Pinged]):
    """The conditional ping with an effect of its own beside it: the mail, demanded with the
    condition, not behind it."""

    mailed: Mailed


class Admitted(Fact):
    """Allowed, pinged once allowed, and mailed regardless: the mail is work the allowance does
    not govern."""

    allowed: Allowed
    pinged: When[Allowed, Pinged]
    mailed: Mailed


class AdmittedByName(Fact):
    allowed: Allowed
    pinged: ApprovedPing
    mailed: Mailed


class AdmittedGenerically(Fact):
    allowed: Allowed
    pinged: Once[Pinged]
    mailed: Mailed


class AdmittedAnnotated(Fact):
    """The conditional under ``Annotated`` metadata, outside and inside: native field metadata
    the relationship carries along."""

    allowed: Allowed
    pinged: Annotated[
        When[
            Annotated[Allowed, Field(description="the registrar's allowance")],
            Annotated[Pinged, Field(description="the desk's ping")],
        ],
        Field(description="the desk pinged once the registrar allows"),
    ]
    mailed: Mailed


class AdmittedWithNote(Fact):
    allowed: Allowed
    pinged: NotedPing
    mailed: Mailed


class AdmittedWithMail(Fact):
    """The mail inside the conditional's class, beside the condition: the same work, demanded
    the same."""

    allowed: Allowed
    pinged: PingAndMail


class Unparametrized(Fact):
    """A conditional that leaves what it demands open: not a product, not a conditional, and
    refused at declaration."""

    allowed: Allowed
    pinged: Once  # pyright: ignore[reportMissingTypeArgument]  the open form under test


class Unapproved(Fact):
    """Refused by the committee, and pinged by the desk regardless."""

    refusal: Refused
    pinged: Pinged


class Vouched(Fact):
    """The applicant vouched for: by the committee's approval, or, refused by the committee, by
    the desk having been pinged. One member of the alternative needs the ping; the other does
    not; the committee's one answer decides which can hold."""

    via: Approved | Unapproved


class PingedWhenVouched(Fact):
    """The desk pinged once the applicant is vouched for. The condition may be established
    without the ping, through the approval, so the conditional orders the ping after it; through
    the other member the condition needs the very ping, which the committee's refusal leaves as
    the one way to be vouched for."""

    pinged: When[Vouched, Pinged]


class Reached(Fact):
    """Reached by having an applicant, or by the desk having been pinged: an alternative whose
    members can both hold, since the applicant is always in the input."""

    via: Applicant | Pinged


class PingedWhenReached(Fact):
    """The desk pinged once the applicant is reached: established at once from the input, and,
    once the ping is there, established two ways at once."""

    pinged: When[Reached, Pinged]


class Fee(Scalar[Decimal]):
    """What admission costs: a business constant."""

    root: Decimal = Decimal("0")


class Waiver(Scalar[Decimal]):
    root: Decimal = Decimal("0")


class Charge(Scalar[Decimal]):
    root: Decimal = Decimal("25")


class Waived(Equal[Fee, Waiver]):
    """The fee equals the waiver: a relation over two business constants, constructed from
    nothing, which holds."""

    value: Fee = Fee()
    bound: Waiver = Waiver()


class Billed(Equal[Fee, Charge]):
    """The fee equals the charge: the same kind of relation, which does not hold."""

    value: Fee = Fee()
    bound: Charge = Charge()


class MailedFree(Fact):
    waived: Waived
    mailed: Mailed


class TextedBilled(Fact):
    billed: Billed
    texted: Texted


class NotifiedByFee(Fact):
    """Mailed when the fee is waived, texted when it is charged: the constants decide."""

    how: MailedFree | TextedBilled


class MailedWhenWaived(Fact):
    """The mail demanded once the waiver is established, from nothing."""

    mailed: When[Waived, Mailed]


class TextedWhenBilled(Fact):
    """The text demanded once the charge is established, which from nothing it never is."""

    texted: When[Billed, Texted]


class Office(Scalar[str]):
    """The office that answers: a business constant whose validator reads the construction's
    context, as any native validator may."""

    root: str = "front desk"

    @model_validator(mode="after")
    def _in_context(self, info: ValidationInfo) -> Self:
        if info.context is None:
            msg = "validated outside any context"
            raise ValueError(msg)
        return self


class Staffed(Fact):
    office: Office
    pinged: Pinged


class Pinging(Fact):
    """A fact of nothing but the ping."""

    pinged: Pinged


class Vacuous(Fact):
    """The ping demanded once the ping is there: a condition established only by the effect it
    would govern, which the program refuses at declaration."""

    pinged: When[Pinging, Pinged]


REGISTRAR = Source("registrar")
COMMITTEE = Source("committee")
DESK = Source("desk")
SCREENING = Source("screening")

BY_APPLICANT = (Correlation(received="applicant", subject="applicant.name"),)

CHECK = Interaction(
    source=REGISTRAR, sends=CheckRequest, receives=(Allowed, Denied), correlated=BY_APPLICANT
)
PING = Interaction(source=DESK, sends=PingRequest, receives=(Pinged,), correlated=BY_APPLICANT)
MAIL = Interaction(source=DESK, sends=MailRequest, receives=(Mailed,), correlated=BY_APPLICANT)
TEXT = Interaction(source=DESK, sends=TextRequest, receives=(Texted,), correlated=BY_APPLICANT)
RATE = Interaction(source=REGISTRAR, sends=RateRequest, receives=(Rated,), correlated=BY_APPLICANT)
SCREEN = Interaction(
    source=SCREENING, sends=ScreenRequest, receives=(Clear, Flagged), correlated=BY_APPLICANT
)
NOTIFY = Interaction(source=DESK, sends=NotifyRequest, receives=(Told,), correlated=BY_APPLICANT)
VETTED_CHECK = Interaction(
    source=REGISTRAR, sends=VettedCheckRequest, receives=(Allowed, Denied), correlated=BY_APPLICANT
)
COMMITTEE_DECISION = Interaction(
    source=COMMITTEE, receives=(Approved, Refused), correlated=BY_APPLICANT
)
APPLICANT_SOURCE = Source("applicant")
WITHDRAWAL = Interaction(source=APPLICANT_SOURCE, receives=(Withdrawal,), correlated=BY_APPLICANT)

ADMISSION = Program(goal=Granted, accepts=Admit, interactions=(CHECK, PING))
"""Allowed and then pinged, with no outcome for a denial."""
JOINT_ADMISSION = Program(goal=Jointly, accepts=Admit, interactions=(CHECK, PING))
"""Allowed and pinged, jointly."""
ADMISSION_VIA_ENCLOSED = Program(goal=GrantedViaEnclosed, accepts=Admit, interactions=(CHECK, PING))
"""The same as ADMISSION, with the conditional wrapped in a plain fact."""
ADMISSION_VIA_DESK = Program(goal=GrantedViaDesk, accepts=Admit, interactions=(CHECK, PING))
"""The same, with the ping wrapped in a plain fact."""
ADMISSION_VIA_CHECKED_DESK = Program(
    goal=GrantedViaCheckedDesk, accepts=Admit, interactions=(CHECK, PING)
)
"""The same, with the ping wrapped in a fact with an opaque identity validator."""
DECISION = Program(goal=Decision, accepts=Admit, interactions=(CHECK, PING))
"""The same, with a fallback outcome for a denial."""
WELCOME = Program(goal=Welcomed, accepts=Admit, interactions=(PING, MAIL))
NOTIFICATION = Program(goal=Notified, accepts=Admit, interactions=(MAIL, TEXT))
RATED_NOTIFICATION = Program(goal=NotifiedByRating, accepts=Admit, interactions=(RATE, MAIL, TEXT))
CLEARANCE = Program(goal=Cleared, accepts=Admit, interactions=(CHECK, SCREEN))
PROCESSING = Program(goal=Processed, accepts=Admit, interactions=(CHECK, SCREEN, MAIL))
HANDLING = Program(goal=Handled, accepts=Admit, interactions=(CHECK, NOTIFY))
VETTING = Program(goal=VettedGranted, accepts=Admit, interactions=(VETTED_CHECK, PING))
ENDORSEMENT = Program(goal=Endorsed, accepts=Admit, interactions=(COMMITTEE_DECISION, PING))
RESOLUTION = Program(goal=Resolved, accepts=Admit, interactions=(CHECK, PING, MAIL, WITHDRAWAL))
"""Granted or withdrawn, with a mail beside the alternative."""
SHARING = Program(goal=Shared, accepts=Admit, interactions=(CHECK, PING))
SHARING_REVERSED = Program(goal=SharedReversed, accepts=Admit, interactions=(CHECK, PING))
TWICE = Program(goal=Twice, accepts=Admit, interactions=(CHECK, PING))
CHAINING = Program(goal=Chained, accepts=Admit, interactions=(CHECK, PING, MAIL))
EITHER = Program(goal=Either, accepts=Admit, interactions=(CHECK, PING))
ADMISSIONS = {
    goal.__name__: Program(goal=goal, accepts=Admit, interactions=(CHECK, PING, MAIL))
    for goal in (
        Admitted,
        AdmittedByName,
        AdmittedGenerically,
        AdmittedAnnotated,
        AdmittedWithNote,
        AdmittedWithMail,
    )
}
"""One conditional in each of its forms, beside work it does not govern."""
VOUCHING = Program(goal=PingedWhenVouched, accepts=Admit, interactions=(COMMITTEE_DECISION, PING))
REACHING = Program(goal=PingedWhenReached, accepts=Admit, interactions=(PING,))
FEES = Program(goal=NotifiedByFee, accepts=Admit, interactions=(MAIL, TEXT))
WAIVED_MAILING = Program(goal=MailedWhenWaived, accepts=Admit, interactions=(MAIL,))
BILLED_TEXTING = Program(goal=TextedWhenBilled, accepts=Admit, interactions=(TEXT,))
STAFFING = Program(goal=Staffed, accepts=Admit, interactions=(PING,))

APPLICANT = Admit(applicant=Applicant(name=Name("ada")))
