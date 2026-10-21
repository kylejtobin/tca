Feature: Strict construction in code, JSON and strings modes at the edges
  Pydantic 2.13.5, Python 3.14. Classes use PRODUCT and ROOT from type_construction.world.
  Decision records 0017, 0026.

  Background:
    Given class Quantity(Scalar[int]) with root: int = Field(gt=0)
    And class Amount(Scalar[Decimal]) with root: Decimal = Field(gt=0)
    And class Sku(Scalar[str]) with root: str = Field(min_length=1)
    And class PlaceOrder(Request) with fields sku: Sku, quantity: Quantity, amount: Amount

  Scenario: Python mode refuses a string for an int root
    When Quantity("3") is constructed
    Then ValidationError is raised

  Scenario: Python mode accepts the primitive
    When Quantity(3) is constructed
    Then the instance has root 3

  Scenario: Python mode refuses a string for a Decimal root
    When Amount("2.50") is constructed
    Then ValidationError is raised

  Scenario: JSON mode accepts a number for an int root and a string for a Decimal root
    When PlaceOrder.model_validate_json('{"sku":"tea","quantity":3,"amount":"2.50"}') is called
    Then the instance has quantity.root 3 and amount.root Decimal("2.50")

  Scenario: JSON mode accepts a number for a Decimal root
    When PlaceOrder.model_validate_json('{"sku":"tea","quantity":3,"amount":2.5}') is called
    Then the instance has amount.root Decimal("2.5")

  Scenario: JSON mode refuses a string for an int root
    When PlaceOrder.model_validate_json('{"sku":"tea","quantity":"3","amount":"2.50"}') is called
    Then ValidationError is raised

  Scenario: A nested model accepts a dict in strict mode
    Given class Holder(Fact) with field a: A where A(Fact) has x: int
    When Holder(a={"x": 1}) is constructed
    Then the instance has a.x 1

  Scenario: A nested model refuses an instance of another class
    Given class B(Fact) with y: int
    When Holder(a=B(y=1)) is constructed
    Then ValidationError is raised with type model_type

  Scenario: A lenient per-call validation constructs a strict request from a tree of text
    Given class Address(Value) with city: Sku and class Line(Value) with sku: Sku, quantity: Quantity
    And class PlaceOrder(Request) with quantity: Quantity, amount: Amount, currency: Currency, ship_to: Address, skus: tuple[Sku, ...], lines: tuple[Line, ...]
    And tree = {"quantity": "3", "amount": "2.50", "currency": "USD", "ship_to": {"city": "Boston"}, "skus": ["tea", "milk"], "lines": [{"sku": "tea", "quantity": 3}]}
    When PlaceOrder.model_validate(tree, strict=False) is called
    Then the instance has quantity.root 3, amount.root Decimal("2.50"), currency Currency.USD, ship_to.city.root "Boston", skus of two Sku, lines of one Line

  Scenario: The same tree is refused in strict mode
    When PlaceOrder.model_validate(tree) is called
    Then ValidationError is raised with types int_type at ("quantity",), is_instance_of at ("amount",), is_instance_of at ("currency",), tuple_type at ("skus",), tuple_type at ("lines",)

  Scenario: The lenient call still applies constraints
    When PlaceOrder.model_validate({**tree, "quantity": "0"}, strict=False) is called
    Then ValidationError is raised with type greater_than at loc ("quantity",)

  Scenario: The lenient call still forbids an undeclared field
    When PlaceOrder.model_validate({**tree, "x": "1"}, strict=False) is called
    Then ValidationError is raised with type extra_forbidden at loc ("x",)
