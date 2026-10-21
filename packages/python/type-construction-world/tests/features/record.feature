Feature: A record validates by alias only, with generators, paths and discriminators
  Decision records 0006, 0007, 0008, 0009, 0014.

  Background:
    Given class ChargeId(Scalar[str]) with root: str = Field(min_length=1)
    And class Charged(Record) with charge: ChargeId = Field(alias="id")

  Scenario: The wire constructs by alias
    When Charged.model_validate_json('{"id":"c1"}') is called
    Then the instance has charge.root "c1"

  Scenario: The wire refuses the field name
    When Charged.model_validate_json('{"charge":"c1"}') is called
    Then ValidationError is raised with type missing at loc ("id",)

  Scenario: Code refuses the field name
    When Charged(charge=ChargeId("c1")) is constructed
    Then ValidationError is raised with type missing at loc ("id",)

  Scenario: Code constructs by alias keyword
    When Charged(id=ChargeId("c1")) is constructed
    Then the instance has charge.root "c1"

  Scenario: A per-call by_name constructs by field name
    When Charged.model_validate({"charge": ChargeId("c1")}, by_name=True) is called
    Then the instance has charge.root "c1"

  Scenario: Serialization uses the alias
    When Charged.model_validate_json('{"id":"c1"}').model_dump_json() is called
    Then the result is '{"id":"c1"}'

  Scenario: An undeclared field is refused
    When Charged.model_validate({"id": "c1", "status": "ok"}) is called
    Then ValidationError is raised with type extra_forbidden

  Scenario: An alias generator on a subclass names every field for the party
    Given class Camel(Record) with model_config = ConfigDict(alias_generator=to_camel)
    And class Refund(Camel) with refund_id: ChargeId, refund_amount: Amount
    When Refund.model_validate_json('{"refundId":"r1","refundAmount":"1.00"}') is called
    Then the instance has refund_id.root "r1" and refund_amount.root Decimal("1.00")
    And Refund.model_config["strict"] is True
    And Refund.model_config["extra"] is "forbid"

  Scenario: The alias generator subclass still refuses an extra field
    When Refund.model_validate_json('{"refundId":"r1","refundAmount":"1.00","x":1}') is called
    Then ValidationError is raised with type extra_forbidden at loc ("x",)

  Scenario: AliasPath reads a nested value
    Given class Charged2(Record) with charge: ChargeId = Field(validation_alias=AliasPath("data", "id")) and amount: Amount = Field(validation_alias=AliasPath("data", "amount", "value"))
    When Charged2.model_validate_json('{"data":{"id":"c1","amount":{"value":"2.50"}}}') is called
    Then the instance has charge.root "c1" and amount.root Decimal("2.50")

  Scenario: A discriminated union selects by the party's tag
    Given class Ok(Record) with status: Literal["succeeded"] and charge: ChargeId = Field(alias="id")
    And class Declined(Record) with status: Literal["declined"] and reason: ChargeId
    And type ChargeResult = Annotated[Ok | Declined, Field(discriminator="status")]
    And class Heard(RootModel[ChargeResult]) with model_config = ROOT
    When Heard.model_validate_json('{"status":"succeeded","id":"c1"}') is called
    Then the root is an Ok
    When Heard.model_validate_json('{"status":"declined","reason":"nsf"}') is called
    Then the root is a Declined

  Scenario: A discriminated union refuses an unknown tag
    When Heard.model_validate_json('{"status":"other"}') is called
    Then ValidationError is raised with type union_tag_invalid

  Scenario: A generic parameter held by a field distinguishes instances
    Given class Heard[P: Connection](Record) with party: P and text: Sku
    And class Noted(Fact) with heard: Heard[Payments]
    When Noted(heard=Heard[Catalog](party=catalog, text=Sku("t"))) is constructed
    Then ValidationError is raised with type model_type at loc ("heard", "party")
    When Heard[Payments](party=catalog, text=Sku("t")) is constructed
    Then ValidationError is raised with type model_type at loc ("party",)
