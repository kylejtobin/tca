Feature: The smell check reports procedure on a page with the construct to write instead
  Decision records 0035, 0037. The checker is .agents/skills/smell-check/smell-check; just check runs it on every program.

  Background:
    Given a page with the lines "count: int", "maybe: Sku | None", "@model_validator(mode=\"after\")", "def check(self) -> Self:", "if self.count: raise ValueError(\"x\")", "def helper(self, x: Any) -> object:", "return cast(int, getattr(self, \"count\", lambda: None))"

  Scenario: A bare primitive field is PRIMITIVE and names the Scalar to write
    When the checker runs on the page
    Then it reports PRIMITIVE on "count: int" with the instruction to write `class Count(Scalar[int])`

  Scenario: None is PROCEDURE and names the absent-case class
    Then it reports PROCEDURE on "maybe: Sku | None" with "an absence is a class"

  Scenario: A validator is VALIDATOR and names the constraint
    Then it reports VALIDATOR on "@model_validator" with "the rule is a Scalar constraint"

  Scenario: A def not under @property or @computed_field is METHOD
    Then it reports METHOD on "def check" and on "def helper"

  Scenario: A branch is PROCEDURE and names the union
    Then it reports PROCEDURE on "if self.count" with "a branch is a union"

  Scenario: Any, object and cast are WEAKENED
    Then it reports WEAKENED on "def helper(self, x: Any) -> object:" and on the cast line

  Scenario: A computation in a computed field is COMPUTATION and names the kind to declare
    Given the page also has the lines "return Total(sum((v.amount.root for v in self.of.valued), Decimal(0)))", "return Total(self.of.total.root * 2)" and "return Total(self.of.total.root)"
    Then it reports COMPUTATION on the sum line and on the "* 2" line with "a computed field is a projection", and not on the projection

  Scenario: getattr is REFLECTION and names the field
    Then it reports REFLECTION on the getattr line with "a lookup by name"

  Scenario: The exit code is 1 with any hit
    Then the exit code is 1

  Scenario: A clean page passes
    Given a page with a Scalar subclass with a Field(gt=0) root and a Fact with two fields and one @computed_field @property returning an expression
    When the checker runs on the page
    Then it reports nothing and the exit code is 0
