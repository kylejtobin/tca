Feature: A docstring under a field is its description
  Decision record 0018.

  Background:
    Given class Sku(Scalar[str]) with docstring "What the shop calls a product."
    And class Quantity(Scalar[int]) with docstring "How many of a product an order asks for."
    And class PlaceOrder(Request) with docstring "An order a customer places.", field sku: Sku followed by the docstring "The product ordered.", and field quantity: Quantity with no docstring

  Scenario: The field docstring is the property description
    When PlaceOrder.model_json_schema()["properties"]["sku"]["description"] is read
    Then the value is "The product ordered."

  Scenario: The type docstring is the $defs description
    When PlaceOrder.model_json_schema()["$defs"]["Sku"]["description"] is read
    Then the value is "What the shop calls a product."

  Scenario: A field with no docstring has no property description
    When PlaceOrder.model_json_schema()["properties"]["quantity"].get("description") is read
    Then the value is None
