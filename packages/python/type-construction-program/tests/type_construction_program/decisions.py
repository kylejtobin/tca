"""Decisions, and the effects that depend on them.

An applicant is admitted when the registrar allows it and the welcome desk has been pinged. The
registrar may allow or deny; the desk, when pinged, pings. Nothing here says in what order the
registrar is asked and the desk is pinged: the business says only that both are needed for an
admission, and that one of them may say no. The other programs vary that one relationship: a
fallback outcome for the denial; two effects nothing declared decides between; the same two
decided by a rating; two effects both needed with nothing to decide; two decisions at once; a
consumer that wants the desk told after a denial, which the desk's own requirement forbids.
"""

from decimal import Decimal
from typing import Self

from pydantic import Field, model_validator

from type_construction.program import Correlation, Interaction, Program, Source
from type_construction.world import AtMost, Beyond, Fact, Record, Scalar, Value


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
    """The outcome: allowed, and the desk pinged."""

    allowed: Allowed
    pinged: Pinged


class Desk(Fact):
    """The desk's ping, wrapped in an ordinary fact with no validator: plain composition."""

    pinged: Pinged


class GrantedViaDesk(Fact):
    allowed: Allowed
    desk: Desk


class CheckedDesk(Fact):
    """The desk's ping behind an opaque identity validator: it changes nothing and the evaluator
    cannot know that."""

    pinged: Pinged

    @model_validator(mode="after")
    def _same(self) -> Self:
        return self


class GrantedViaCheckedDesk(Fact):
    allowed: Allowed
    desk: CheckedDesk


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
    """Two decisions inside one fact, and a mail beside them."""

    cleared: Cleared
    mailed: Mailed


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
    """A decision nothing is sent for: the committee approves or refuses on its own."""

    approved: Approved
    pinged: Pinged


class Withdrawal(Record):
    applicant: Name


class Withdrawn(Fact):
    """The applicant withdrew: a passive alternative nothing can refuse."""

    withdrawal: Withdrawal


class Resolved(Fact):
    """Granted or withdrawn, and the applicant mailed either way."""

    outcome: Granted | Withdrawn
    mailed: Mailed


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
"""Allowed and pinged, with no outcome for a denial."""
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

APPLICANT = Admit(applicant=Applicant(name=Name("ada")))
