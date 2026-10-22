Feature: Scalars, constants, fresh scalars and Duration
  Decision records 0002, 0011, 0043, 0057. Classes: Quantity(Scalar[int]) with root: int = Field(gt=0);
  Placed(Fact) with line: Line, at: Instant and id: Identity.

  Scenario: A constrained root refuses a value outside the constraint
    When Quantity(0) is constructed
    Then ValidationError is raised with type greater_than at loc ()
    When Quantity(3) is constructed
    Then the instance has root 3

  Scenario: Code constructs strict
    When Quantity("3") is constructed
    Then ValidationError is raised with type int_type at loc ()

  Scenario: Duration refuses zero and accepts a positive timedelta
    When Duration(timedelta(0)) is constructed
    Then ValidationError is raised with type greater_than at loc ()
    When Duration(timedelta(seconds=1)) is constructed
    Then the instance has root timedelta(seconds=1)

  Scenario: Instant and Identity are fresh scalars, required on their holder and constructed for it by the engine
    When the required fields of Placed are read
    Then they are ["line", "at", "id"]
    When Placed(line=tea) is constructed
    Then ValidationError is raised with type missing at loc ("at",) and at loc ("id",)
    When Placed(line=tea, at=Instant(), id=Identity()) is constructed
    Then at.root is an aware datetime and id.root is a UUID
    And Instant.model_fields["root"].default_factory is set and the field is not required, so the engine reads the class as fresh

  Scenario: Two fresh scalars never share a value
    When Instant() is constructed twice and Identity() twice
    Then the second instant is not before the first, and the two identities differ

  Scenario: A weak value for Instant is refused
    When Placed(line=tea, at="now", id=Identity()) is constructed
    Then ValidationError is raised with type datetime_type at loc ("at",)
