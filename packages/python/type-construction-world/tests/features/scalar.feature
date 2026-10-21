Feature: Scalars, Instant, Identity and Duration
  Decision records 0002, 0011.

  Scenario: A constrained root refuses a value outside the constraint
    Given class Quantity(Scalar[int]) with root: int = Field(gt=0)
    When Quantity(0) is constructed
    Then ValidationError is raised with type greater_than

  Scenario: Duration refuses zero
    When Duration(timedelta(0)) is constructed
    Then ValidationError is raised with type greater_than

  Scenario: Duration accepts a positive timedelta
    When Duration(timedelta(seconds=1)) is constructed
    Then the instance has root timedelta(seconds=1)

  Scenario: Instant and Identity construct themselves on the holder
    Given class Placed(Fact) with order: PlaceOrder, at: Instant, id: Identity
    When Placed(order=PlaceOrder(quantity=Quantity(1))) is constructed
    Then at.root is a datetime and id.root is a UUID
    And the required fields of Placed are ["order"]

  Scenario: A weak value for Instant is refused
    When Placed(order=PlaceOrder(quantity=Quantity(1)), at="now") is constructed
    Then ValidationError is raised
