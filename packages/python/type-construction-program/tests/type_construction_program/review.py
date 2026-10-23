"""A case decided by the one approval it receives before the review closes.

Approvals arrive from reviewers over time, and the reviewers say when the review is closed.
``Sole`` is ``Only`` over every approval: exactly one. With none, or with two, the case is not
decided this way, and the program declares no other way.
"""

from pydantic import Field

from type_construction.program import Correlation, Interaction, Program, Source
from type_construction.world import Fact, Only, Record, Scalar, Value


class CaseId(Scalar[str]):
    root: str = Field(min_length=1)


class Reviewer(Scalar[str]):
    root: str = Field(min_length=1)


class Case(Value):
    id: CaseId


class ReviewCase(Value):
    """The command: decide this case."""

    case: Case


class Approval(Record):
    case: CaseId = Field(alias="case_id")
    reviewer: Reviewer


class ReviewClosed(Record):
    case: CaseId = Field(alias="case_id")


class Sole(Only[Approval]):
    """The one approval, when there is exactly one."""


class Decided(Fact):
    case: Case
    approval: Sole


REVIEWERS = Source("reviewers")
BY_CASE = (Correlation(received="case", subject="case.id"),)

APPROVALS = Interaction(
    source=REVIEWERS, receives=(Approval,), correlated=BY_CASE, closed_by=ReviewClosed
)
CLOSING = Interaction(source=REVIEWERS, receives=(ReviewClosed,), correlated=BY_CASE)

REVIEW = Program(goal=Decided, accepts=ReviewCase, interactions=(APPROVALS, CLOSING))

CASE = ReviewCase(case=Case(id=CaseId("case-3")))
