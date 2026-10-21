Feature: The engine proves a route once and answers it by construction
  Decision records 0016, 0021, 0029, 0030, 0042, 0044, 0045, 0046. Program module: Sku, Quantity, Amount, LargeAmount (gt 100), SmallAmount (gt 0, le 100),
  Priced(Scalar[LargeAmount | SmallAmount]), ChargeId; Catalog and Payments connections; PlaceOrder(sku, quantity);
  Price(amount) and Charged(charge alias "id") records; Says[P, T](Action[P, T]) whose perform returns a fixed record;
  Quote(Says[Catalog, Price]) holding order; Placed(order, price) with computed amount -> LargeAmount | SmallAmount returning
  Priced(price.amount.root * order.quantity.root).root; Discounted(placed, amount: LargeAmount) and FullPrice(placed, amount: SmallAmount)
  each with computed total; Charge(Says[Payments, Charged]) holding priced: Discounted | FullPrice; Paid(priced, charged);
  OrderPaid(Reply[Paid]) with computed charge and total; Checkout(Route[PlaceOrder, OrderPaid]); ShopConfig(catalog, payments).
  The catalog says Price(amount=2.50); payments says Charged(id="ch_1").

  Scenario: A program's classes exclude the parametrizations Pydantic registers in the module
    Given vars(shop) holds Says, Says[Catalog, Price] and Quote
    When classes(shop) is read
    Then it holds Says and Quote and not Says[Catalog, Price]

  Scenario: An action's record and party are read through the library kind's type variables
    When hears(Charge) and party(Charge) are read
    Then they are Charged and Payments

  Scenario: The proof orders the classes a route needs
    When prove(Checkout, shop) is called
    Then the order is Quote, Price, Placed, LargeAmount, Discounted, SmallAmount, FullPrice, Charge, Charged, Paid

  Scenario: The proof reports every fault at once
    Given a route whose reply's fact holds unheard: Unheard, a record no action hears, and amount: Amount, a scalar nothing produces
    When prove is called on it
    Then ValidationError is raised with type hearer at loc (route, "unheard") and type source at loc (route, "amount")

  Scenario: The proof refuses a class two computed fields produce
    Given a route whose reply's fact holds amount: Amount, and Discounted.total and FullPrice.total both return Amount
    When prove is called on it
    Then ValidationError is raised with type producer and message "2 computed fields produce Amount; exactly one must"

  Scenario: A small order constructs FullPrice
    When answer(Checkout, PlaceOrder(sku="tea", quantity=3), ShopConfig(), shop) is awaited
    Then the reply dumps {"charge":"ch_1","total":"7.50"}
    And reply.of.priced is a FullPrice
    And Quote was performed once and Charge was performed once

  Scenario: A large order constructs Discounted
    When answer(Checkout, PlaceOrder(sku="tea", quantity=50), ShopConfig(), shop) is awaited
    Then the reply dumps {"charge":"ch_1","total":"112.500"}
    And reply.of.priced is a Discounted
    And Quote was performed once and Charge was performed once

  Scenario: An action with no library kind cannot be constructed
    Given class Bare(Action[Catalog, Price]) with order: PlaceOrder and no perform
    When Bare(order=...) is constructed
    Then TypeError is raised naming Bare as abstract

  Scenario: Independent actions are performed together
    Given a second party Shipping with Estimate(Says[Shipping, Eta]) holding order, Eta(days: Days), and Placed holding order, price and eta, each perform sleeping 0.2 s
    When levels(Checkout, shop) is read
    Then the levels are [Quote, Price, Estimate, Eta], [Placed], [Charge, Charged], [Paid]
    When answer is awaited
    Then Quote and Estimate start at 0.0 s and end at 0.2 s, and Charge starts at 0.2 s

  Scenario: A party class held twice in the config is refused
    Given a config with catalog: Catalog and other: Catalog
    When prove(Checkout, shop) is called
    Then ValidationError is raised with type party and message "2 config fields hold Catalog, the party of Quote; exactly one must"

  Scenario: Levels hold only the classes the run builds
    When levels(Checkout, shop) is read for the discount program
    Then the levels are [Quote], [LinePriced], [Discounted, FullPrice], [Charge], [LinePaid], [Paid], with no record and no produced scalar in any level

  Scenario: Connections open once before answers and close once after, last opened first
    Given Catalog and Payments connections whose open and close record their names
    When two answers are awaited inside opened(ShopConfig())
    Then the record is open:Catalog, open:Payments, perform, perform, perform, perform, close:Payments, close:Catalog
    And the four performs used two distinct clients

  Scenario: A connection without a library kind cannot be constructed
    Given class Bare(Connection) with url: Url and no open or close
    When Bare(url=...) is constructed
    Then TypeError is raised naming Bare as abstract

  Scenario: A client set as a private attribute leaves the connection frozen and unserialized
    Given class Http(Connection) with _client: httpx.AsyncClient = PrivateAttr() set in open()
    When open() is awaited on a constructed instance
    Then the client is set, assigning a field raises frozen_instance, model_dump_json() omits the client, and hash() works

  Scenario: A three-line order fans out per line and collects in order
    Given PlaceOrder with lines: tuple[Line, ...], Quote holding line: Line, LinePriced(line, price), Charge holding priced: LinePriced, LinePaid(priced, charged), Paid(order, lines: tuple[LinePaid, ...]) with computed total, each perform sleeping 0.2 s
    When answer is awaited for lines tea×3, milk×1, jam×2 at 2.50 each
    Then elements(shop) is {Line: (PlaceOrder, "lines")}
    And scopes gives Quote, Price, LinePriced, Charge, Charged, LinePaid per Line and Paid once per run
    And three Quotes start at 0.0 s and three Charges start at 0.2 s
    And the reply dumps {"total":"15.00","charges":["ch_tea","ch_milk","ch_jam"]}

  Scenario: Each line chooses its own fact from a computed union
    Given LinePriced with computed amount -> LargeAmount | SmallAmount, Discounted holding amount: LargeAmount, FullPrice holding amount: SmallAmount, and Charge holding line: Discounted | FullPrice
    When answer is awaited for lines tea×3 and gold×50 at 2.50 each
    Then the first line is a FullPrice and the second a Discounted
    And the reply dumps {"total":"120.000","charges":["ch_tea","ch_gold"]}

  Scenario: A reply's fact that exists per element is refused
    Given class Wrong(Fact) with order: PlaceOrder and one: LinePaid, and a route whose reply is Reply[Wrong]
    When prove is called on it
    Then ValidationError is raised with type scope and message "Wrong exists once per Line; a reply's fact exists once per run, so it collects tuple[..., ...] instead of holding an element"

  Scenario: A tuple that collects a once-per-run class is refused
    Given class Collects(Fact) with orders: tuple[Paid, ...], and a route whose reply is Reply[Collects]
    When prove is called on it
    Then ValidationError is raised with type scope and message "Collects.orders collects Paid, which exists once per run; hold it directly"

  Scenario: An answer is one span per route and one per performed action
    Given the OpenTelemetry SDK with an in-memory exporter
    When answer is awaited for lines tea×3 and gold×50
    Then the root span is named Checkout with attributes tca.request "PlaceOrder" and tca.levels 6 and events skipped {tca.class: "Discounted"} and skipped {tca.class: "FullPrice"}
    And its children are two spans named Quote with tca.party "Catalog" and tca.record "Price" and two named Charge with tca.party "Payments" and tca.record "Charged"
    And no attribute holds a request's or a record's contents
