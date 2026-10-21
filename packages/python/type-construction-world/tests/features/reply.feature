Feature: A reply holds one fact as its parameter and serializes only its computed fields
  Decision record 0010.

  Background:
    Given class Sku(Scalar[str]) with root: str = Field(min_length=1)
    And class Paid(Fact) with sku: Sku
    And class Other(Fact) with sku: Sku
    And class OrderPaid(Reply[Paid]) with a computed_field product -> Sku returning self.of.sku

  Scenario: The dump carries the computed field only
    When OrderPaid(of=Paid(sku=Sku("tea"))).model_dump_json() is called
    Then the result is '{"product":"tea"}'

  Scenario: The held fact stays readable
    When OrderPaid(of=Paid(sku=Sku("tea"))).of.sku.root is read
    Then the value is "tea"

  Scenario: The serialization schema lists the computed field only
    When OrderPaid.model_json_schema(mode="serialization")["properties"] is read
    Then its keys are ["product"]

  Scenario: The held fact is required for construction
    When OrderPaid() is constructed
    Then ValidationError is raised with type missing at loc ("of",)
    And OrderPaid.model_json_schema(mode="validation")["required"] is ["of"]

  Scenario: A fact of another class is refused
    When OrderPaid(of=Other(sku=Sku("x"))) is constructed
    Then ValidationError is raised with type model_type at loc ("of",)

  Scenario: The reply's fact is read from its generic argument
    When the __mro__ of OrderPaid is searched for a base whose __pydantic_generic_metadata__["args"] is non-empty
    Then the args are (Paid,)
