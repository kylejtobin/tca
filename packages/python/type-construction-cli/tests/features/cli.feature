Feature: The command line is rendered from the request's JSON schema and validates leniently
  Decision records 0026, 0027, 0029, 0030. Program module: PlaceOrder with sku: Sku, quantity: Quantity, amount: Amount,
  currency: Currency (StrEnum USD, EUR), ship_to: Address (Value with city: City), tags: tuple[Sku, ...],
  lines: tuple[Line, ...] (Value with sku, quantity); Checkout(Route[PlaceOrder, OrderPaid]) with docstring
  "Price an order and charge for it."; ShopConfig with payments: Payments (url: Url, key: Key, retries: Retries)
  and catalog: Catalog (url: Url). Field docstrings: sku "The product ordered."; type docstrings on Sku,
  Quantity, Amount, City, Line, Url, Key, Retries.

  Scenario: The schema parses into one node class per key shape, chosen by the discriminator
    When Schema.model_validate(PlaceOrder.model_json_schema(), strict=False) is called
    Then each property is a Reference
    And defs["Sku"] is a Primitive with type "string" and min_length 1
    And defs["Amount"] is an AnyOf whose first form is a Primitive with type "number" and exclusive_minimum 0
    And defs["Currency"] is a Primitive with enum ("USD", "EUR")
    And defs["Address"] is an Object with properties {"city"} and required ("city",)
    And the property "tags" is an Array whose items is a Reference to "Sku"

  Scenario: A node with an unknown type is refused at its path
    When Schema.model_validate({"type": "object", "properties": {"x": {"type": "weird"}}}, strict=False) is called
    Then ValidationError is raised with type literal_error at loc ("properties", "x", "primitive", "type")

  Scenario: The program's help lists routes and environment variables
    When main([], name="shop") is called
    Then the exit code is 0
    And stdout contains "checkout  Price an order and charge for it."
    And stdout contains "PAYMENTS__URL      Where the party is. (uri)"
    And stdout contains "PAYMENTS__KEY      The credential the business holds for the party. (password)"
    And stdout contains "PAYMENTS__RETRIES  How many times a call is retried. (>= 0)"

  Scenario: A route's help shows each option from the schema
    When parser("shop checkout", PlaceOrder).format_help() is called
    Then it contains "--sku SKU             The product ordered. (min length 1)"
    And it contains "--quantity QUANTITY   How many of a product an order asks for. (> 0)"
    And it contains "--amount NUMBER       A sum of money. (> 0.0)"
    And it contains "--currency {USD,EUR}"
    And it contains "--ship-to.city CITY   The city an order ships to. (min length 1)"
    And it contains "--tags SKU            What the shop calls a product. (min length 1)"
    And it contains "--lines JSON          One product and how many of it."

  Scenario: The parsed options rebuild the nested tree
    When parser("shop checkout", PlaceOrder).parse_args(["--sku", "tea", "--quantity", "3", "--amount", "2.50", "--currency", "EUR", "--ship-to.city", "Boston", "--tags", "gift", "--tags", "rush", "--lines", '{"sku":"tea","quantity":3}']) is passed to tree()
    Then the result is {"sku": "tea", "quantity": "3", "amount": "2.50", "currency": "EUR", "ship_to": {"city": "Boston"}, "tags": ["gift", "rush"], "lines": [{"sku": "tea", "quantity": 3}]}
    And PlaceOrder.model_validate(result, strict=False) constructs

  Scenario: A value outside a constraint exits 1 naming the field
    When main(["checkout", "--sku", "tea", "--quantity", "0", "--amount", "2.50", "--currency", "EUR", "--ship-to.city", "Boston"], name="shop") is called
    Then the exit code is 1
    And stderr contains "quantity" and "greater_than"

  Scenario: An unknown route exits 2
    When main(["refund"], name="shop") is called
    Then the exit code is 2
    And stderr contains the route list

  Scenario: A valid request reaches answer
    When main(["checkout", "--sku", "tea", "--quantity", "3", "--amount", "2.50", "--currency", "EUR", "--ship-to.city", "Boston", "--tags", "gift", "--lines", '{"sku":"tea","quantity":3}'], name="shop") is called
    Then answer is called with Checkout, a constructed PlaceOrder, a constructed ShopConfig, and the program module
