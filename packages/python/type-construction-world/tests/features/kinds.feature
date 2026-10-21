Feature: Derivation, relation and selection kinds construct a value, a rule or a choice from what they hold
  Decision records 0047, 0048, 0049. Classes: UnitPrice(Scalar[Decimal]) with gt 0, Quantity(Scalar[int]) with gt 0,
  Rate(Scalar[Decimal]) with root defaulted to 0.9, Sku(Scalar[str]), Line(Value) with sku and quantity;
  LineTotal(Times[UnitPrice, Quantity]); Reduced(Times[LineTotal, Rate]) with right defaulted to Rate();
  Lines(Sum[LineTotal]); Allowed(Between[Quantity, Quantity, Quantity]); Same(Equal[Quantity, Quantity]);
  Cheapest(Least[LineTotal]); Dearest(Greatest[LineTotal]); Opening(First[Line]); Sole(Only[Line]).

  Scenario: Times multiplies its operands exactly
    When LineTotal(left=UnitPrice(Decimal("2.50")), right=Quantity(3)).root is read
    Then it is Decimal("7.50")

  Scenario: A constant factor is a scalar defaulted on the subclass
    When Reduced(left=LineTotal(left=UnitPrice(Decimal("2.50")), right=Quantity(50))).root is read
    Then it is Decimal("112.500")
    And the required fields of Reduced are ["left"]

  Scenario: Sum adds every element and none is zero
    When Lines(of=(LineTotal 7.50, LineTotal 125.00)).root is read
    Then it is Decimal("132.50")
    When Lines(of=()).root is read
    Then it is Decimal(0)

  Scenario: An operand outside the bound is a checker error
    Given class Wrong(Times[Sku, Quantity])
    When basedpyright checks the module
    Then it reports Sku is not assignable to Numeric

  Scenario: AtMost holds at the bound and refuses above it with relation
    When Small(value=LineTotal 100.00, bound=Threshold()) is constructed
    Then the instance constructs
    When Small(value=LineTotal 125.00, bound=Threshold()) is constructed
    Then ValidationError is raised with one error of type relation and message "LineTotal exceeds Threshold"

  Scenario: Beyond refuses at the bound and holds above it
    When Large(value=LineTotal 100.00, bound=Threshold()) is constructed
    Then ValidationError is raised with one error of type relation and message "LineTotal is within Threshold"
    When Large(value=LineTotal 125.00, bound=Threshold()) is constructed
    Then the instance constructs

  Scenario: Between holds inside the bounds and refuses outside with relation
    When Allowed(value=Quantity(1), lower=Quantity(1), upper=Quantity(10)) and the same with Quantity(10) are constructed
    Then both construct
    When Allowed(value=Quantity(11), lower=Quantity(1), upper=Quantity(10)) is constructed
    Then ValidationError is raised with one error of type relation and message "Quantity is over Quantity"
    When Allowed(value=Quantity(1), lower=Quantity(2), upper=Quantity(10)) is constructed
    Then ValidationError is raised with one error of type relation and message "Quantity is under Quantity"

  Scenario: Equal holds on the same value and refuses with relation
    When Same(value=Quantity(3), bound=Quantity(3)) is constructed
    Then the instance constructs
    When Same(value=Quantity(3), bound=Quantity(4)) is constructed
    Then ValidationError is raised with one error of type relation and message "Quantity differs from Quantity"

  Scenario: A relation's refusal names the operands' classes, never their values
    When Small(value=LineTotal 125.00, bound=Threshold()) is constructed
    Then the error message contains "LineTotal" and "Threshold" and not "125"

  Scenario: Least and Greatest choose by value and ties go to the earliest element
    Given cheap, dear and cheap_again with roots 1, 2 and 1
    When Cheapest(of=(cheap, dear, cheap_again)).chosen and Dearest(of=(cheap, dear, cheap_again)).chosen are read
    Then they are cheap and dear, by identity

  Scenario: Least refuses no elements
    When Cheapest(of=()) is constructed
    Then ValidationError is raised with type too_short at loc ("of",)

  Scenario: First chooses by position over any element class
    Given tea and jam, two Lines
    When Opening(of=(tea, jam)).chosen is read
    Then it is tea, by identity

  Scenario: Only chooses the one element and refuses any other count with relation
    When Sole(of=(tea,)).chosen is read
    Then it is tea, by identity
    When Sole(of=(tea, jam)) is constructed
    Then ValidationError is raised with one error of type relation and message "2 elements, not one"
    When Sole(of=()) is constructed
    Then ValidationError is raised with one error of type relation and message "0 elements, not one"

  Scenario: chosen is a property, so a selection serializes its elements and not its choice
    When Cheapest(of=(cheap, dear)).model_dump() is read
    Then its keys are ["of"]
