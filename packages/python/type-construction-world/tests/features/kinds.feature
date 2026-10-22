Feature: Derivation, relation and selection kinds declare a value, a rule or a choice once, as Pydantic reads it
  Decision records 0047, 0048, 0049, 0057. A relation is the restriction of one comparison to the orderings its
  Literal admits; a selection's shape is its tuple annotation; a derivation's root is computed at construction by its
  Derived operation. A computed field, a root or an ordering, declares its Computation in its annotation with COMPUTED
  as its default: Pydantic computes it from the validated operands and validates the result by the field's type, and
  refuses anything given for it, equal to the result or not, in Python or in JSON, at any depth. Classes: UnitPrice(Scalar[Decimal]) with gt 0, Quantity(Scalar[int]) with gt 0,
  Threshold(Scalar[Decimal]) with root defaulted to 100, Rate(Scalar[Decimal]) with root defaulted to 0.9,
  Sku(Scalar[str]), Line(Value) with sku and quantity; LineTotal(Times[UnitPrice, Quantity]); Reduced(Times[LineTotal,
  Rate]); Lines(Sum[LineTotal]); Small(AtMost[LineTotal, Threshold]); Large(Beyond[LineTotal, Threshold]);
  Allowed(Between[Quantity, Quantity, Quantity]); Same(Equal[Quantity, Quantity]); Other(Differs[Quantity,
  Quantity]); Below(Under[Quantity, Quantity]); Above(AtLeast[Quantity, Quantity]); Cheapest(Least[LineTotal]);
  Dearest(Greatest[LineTotal]); Opening(First[Line]); Sole(Only[Line]).

  Scenario: Times multiplies its operands exactly at construction and excludes the root from its dump
    When LineTotal(left=UnitPrice(Decimal("2.50")), right=Quantity(3)) is constructed
    Then root is Decimal("7.50") and model_dump() is {"left": Decimal("2.50"), "right": 3}

  Scenario: A constant factor is a scalar with a default root, required on the holder and seeded by the engine
    When Reduced(left=LineTotal 125.00, right=Rate()).root is read
    Then it is Decimal("112.500")
    And the required fields of Reduced are ["left", "right"]

  Scenario: Sum adds every element and none is zero
    When Lines(of=(LineTotal 7.50, LineTotal 125.00)).root is read
    Then it is Decimal("132.50")
    When Lines(of=()).root is read
    Then it is Decimal(0)

  Scenario: A derivation declares its operation once, as the Derived metadata of its root
    When the Computation in LineTotal.model_fields["root"].metadata and in Lines.model_fields["root"].metadata is read
    Then each is a Derived, with operands ("left", "right") and ("of",)
    And LineTotal.model_fields["root"].default is COMPUTED and the field is not required

  Scenario: A root is computed and never given, equal to the result or not, in Python or in JSON
    When LineTotal(left=UnitPrice(Decimal("2.50")), right=Quantity(3), root=Decimal("7.50")) is constructed
    Then ValidationError is raised with one error of type computed at loc ("root",), message "root is computed from left and right and never given", input Decimal("7.50")
    When LineTotal.model_validate_json('{"left": "2.50", "right": 3, "root": "7.50"}') is called
    Then ValidationError is raised with one error of type computed at loc ("root",), input "7.50"
    When LineTotal.model_validate_json('{"left": "2.50", "right": 3}') is called
    Then root is Decimal("7.50")
    When Lines.model_validate({"of": ({"left": Decimal(1), "right": 1, "root": Decimal(1)},)}) is called
    Then ValidationError is raised with type computed at loc ("of", 0, "root") and type uncomputed at loc ("root",)

  Scenario: A root whose operand did not construct is uncomputed, beside the operand's error
    When LineTotal.model_validate_json('{"left": "0", "right": 3}') is called
    Then ValidationError is raised with type greater_than at loc ("left",) and type uncomputed at loc ("root",), message "root is computed from left, which did not construct"

  Scenario: An operand outside the bound is a checker error
    Given class Wrong(Times[Sku, Quantity]) and class Bad(Scalar[Thing]) with Thing a Fact
    When basedpyright checks the module
    Then it reports Sku is not assignable to Numeric, and Thing is not assignable to Primitive

  Scenario: AtMost admits -1 and 0 and refuses 1 with literal_error at the ordering field
    When Small(value=LineTotal 100.00, bound=Threshold()) is constructed
    Then the instance constructs with ordering 0
    When Small(value=LineTotal 125.00, bound=Threshold()) is constructed
    Then ValidationError is raised with one error of type literal_error at loc ("ordering",), message "Input should be -1 or 0", input 1

  Scenario: Beyond admits 1 and refuses 0
    When Large(value=LineTotal 100.00, bound=Threshold()) is constructed
    Then ValidationError is raised with one error of type literal_error at loc ("ordering",), message "Input should be 1", input 0
    When Large(value=LineTotal 125.00, bound=Threshold()) is constructed
    Then the instance constructs with ordering 1

  Scenario: Between computes two orderings and refuses at the one that does not hold
    When Allowed(value=Quantity(1), lower=Quantity(1), upper=Quantity(10)) and the same with Quantity(10) are constructed
    Then both construct, the first with below 0 and the second with above 0
    When Allowed(value=Quantity(11), lower=Quantity(1), upper=Quantity(10)) is constructed
    Then ValidationError is raised with type literal_error at loc ("above",), input 1
    When Allowed(value=Quantity(1), lower=Quantity(2), upper=Quantity(10)) is constructed
    Then ValidationError is raised with type literal_error at loc ("below",), input 1

  Scenario: Equal, Differs, Under and AtLeast are the same comparison with other admitted orderings
    When Same(value=Quantity(3), bound=Quantity(3)) is constructed
    Then the instance constructs with ordering 0
    When Same(value=Quantity(3), bound=Quantity(4)) is constructed
    Then ValidationError is raised with one error of type literal_error, message "Input should be 0"
    When Other(value=Quantity(3), bound=Quantity(4)) is constructed
    Then the instance constructs with ordering -1
    When Other(value=Quantity(3), bound=Quantity(3)) is constructed
    Then ValidationError is raised with one error of type literal_error, message "Input should be -1 or 1"
    When Below(value=Quantity(3), bound=Quantity(4)) and Above(value=Quantity(4), bound=Quantity(4)) are constructed
    Then their orderings are -1 and 0

  Scenario: An ordering is computed and never given, admitted or not, and is excluded from the dump
    When Small.model_validate({"value": LineTotal 125.00, "bound": Threshold(), "ordering": 0}) is called
    Then ValidationError is raised with one error of type computed at loc ("ordering",), input 0
    When Small(value=LineTotal 100.00, bound=Threshold(), ordering=0) is constructed
    Then ValidationError is raised with one error of type computed at loc ("ordering",), input 0
    When Small.model_validate_json('{"value": {"left": "100.00", "right": 1}, "bound": "100", "ordering": 0}') is called
    Then ValidationError is raised with one error of type computed at loc ("ordering",), input 0
    When Small(value=LineTotal 100.00, bound=Threshold()).model_dump() is read
    Then it is {"value": {"left": Decimal("100.00"), "right": 1}, "bound": Decimal("100")}

  Scenario: A relation kind declares its comparison once, as the Comparison metadata of its ordering field
    When the Computation in the metadata of Small.ordering, Allowed.below and Allowed.above is read
    Then they are Comparison(("value", "bound")), Comparison(("lower", "value")) and Comparison(("value", "upper")), each with default COMPUTED
    And the admitted orderings of Under, AtMost, Equal, AtLeast, Beyond and Differs are (-1,), (-1, 0), (0,), (0, 1), (1,) and (-1, 1)

  Scenario: Least and Greatest choose by value and ties go to the earliest element
    Given cheap, dear and cheap_again with roots 1, 2 and 1
    When Cheapest(of=(cheap, dear, cheap_again)).chosen and Dearest(of=(cheap, dear, cheap_again)).chosen are read
    Then they are cheap and dear, by identity

  Scenario: A selection with no element to choose from refuses by its tuple shape
    When Cheapest, Dearest and Opening are validated from {"of": ()}
    Then each raises ValidationError with one error of type too_short at loc ("of",), message "Tuple should have at least 1 item after validation, not 0"
    When Sole is validated from {"of": ()}
    Then ValidationError is raised with one error of type missing at loc ("of", 0), message "Field required"

  Scenario: First chooses by position over any element class
    Given tea and jam, two Lines
    When Opening(of=(tea, jam)).chosen is read
    Then it is tea, by identity

  Scenario: Only is the shape tuple[E] and refuses more than one with too_long
    When Sole(of=(tea,)).chosen is read
    Then it is tea, by identity
    When Sole is validated from {"of": (tea, jam)}
    Then ValidationError is raised with one error of type too_long at loc ("of",), message "Tuple should have at most 1 item after validation, not 2"
    And Sole.model_fields["of"].annotation is tuple[Line] and Opening.model_fields["of"].metadata is [MinLen(min_length=1)]

  Scenario: chosen is a property, so a selection serializes its elements and not its choice
    When Cheapest(of=(cheap, dear)).model_dump() is read
    Then its keys are ["of"]
