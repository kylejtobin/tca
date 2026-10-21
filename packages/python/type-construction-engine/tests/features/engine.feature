Feature: The engine proves a program at startup and answers a route by construction
  Decision records 0021, 0029, 0030, 0042, 0044, 0045, 0046, 0047, 0048. Program module shop: Sku, Quantity, Amount,
  LargeAmount (gt 100), SmallAmount (gt 0, le 100), Priced(Scalar[LargeAmount | SmallAmount]), ChargeId;
  Said(Setting[str]); Speaker(Connection) with says: Said and open and close that do nothing; Catalog(Speaker) and
  Payments(Speaker); Line(Request) with sku and quantity; PlaceOrder(Request) with lines: tuple[Line, ...];
  Price(Record) with amount; Charged(Record) with charge alias "id"; Says[P: Speaker, T](Action[P, T]) whose perform
  returns hear(self, self.party.says.root); Quote(Says[Catalog, Price]) holding line; LinePriced(line, price) with
  computed amount -> LargeAmount | SmallAmount returning Priced.model_validate(price.amount.root * line.quantity.root).root;
  Discounted(priced, amount: LargeAmount) with computed total at 90%; FullPrice(priced, amount: SmallAmount) with
  computed total; Charge(Says[Payments, Charged]) holding line: Discounted | FullPrice; LinePaid(line, charged);
  Paid(order, lines: tuple[LinePaid, ...]) with computed total; OrderPaid(Reply[Paid]) with computed total and charges;
  Checkout(Route[PlaceOrder, OrderPaid]); ShopConfig(catalog, payments). The environment holds
  CATALOG__SAYS='{"amount": "2.50"}' and PAYMENTS__SAYS='{"id": "ch_1"}'.

  Scenario: A program's classes are the ones its module defines
    Given vars(shop) holds Says, Says[Catalog, Price], Quote and the imported Fact
    When classes(shop) is read
    Then it holds Quote and not Says, not Says[Catalog, Price] and not Fact

  Scenario: A route's request class is read from its request field
    When asked(Checkout) is read
    Then it is PlaceOrder

  Scenario: An action's record is read through the library kind's type variables
    When heard(Quote) and heard(Charge) are read
    Then they are Price and Charged

  Scenario: An action's party is the annotation of its party field
    When Quote.model_fields["party"].annotation is read
    Then it is Catalog

  Scenario: The proof is the classes a route constructs
    When prove(Checkout, shop) is read
    Then it holds PlaceOrder, Line, Catalog, Payments, Quote, Price, LinePriced, LargeAmount, SmallAmount, Discounted, FullPrice, Charge, Charged, LinePaid, Paid, OrderPaid and Checkout

  Scenario: A record no action hears is reported once, at the field that holds it
    Given shop without Quote
    When proven is called on it
    Then ValidationError is raised with one error of type missing at loc ("LinePriced", "price") and message "no class fills LinePriced.price, which holds Price"

  Scenario: A record two actions hear is refused
    Given shop with a second Says[Catalog, Price] subclass Requote
    When proven is called on it
    Then ValidationError is raised with type hearer at loc ("Price",) and message "2 actions hear Price: Quote, Requote; exactly one must"

  Scenario: A class two computed fields produce is refused
    Given shop with a second fact whose computed field returns LargeAmount | SmallAmount
    When proven is called on it
    Then ValidationError is raised with type producer at loc ("LargeAmount",) and at loc ("SmallAmount",)

  Scenario: A party held twice in the config is refused
    Given shop whose config holds catalog: Catalog and backup: Catalog
    When proven is called on it
    Then ValidationError is raised with type party at loc ("Catalog",) and message "2 config fields hold Catalog: backup, catalog; exactly one must"

  Scenario: Two classes that hold each other are refused as a cycle
    Given shop with Egg(chicken: Chicken, order: PlaceOrder) and Chicken(egg: Egg)
    When proven is called on it
    Then ValidationError is raised with type cycle at loc ("Egg",) and at loc ("Chicken",)

  Scenario: A small order constructs FullPrice
    When answer(Checkout, PlaceOrder.model_validate_json('{"lines": [{"sku": "tea", "quantity": 3}]}'), ShopConfig(), shop) is awaited
    Then the route's reply dumps {"total":"7.50","charges":["ch_1"]}
    And reply.of.lines[0].line is a FullPrice

  Scenario: A three-line order fans out per line and each line chooses its own fact
    When answer is awaited for lines tea 3, gold 50, jam 2
    Then the route's reply dumps {"total":"125.000","charges":["ch_1","ch_1","ch_1"]}
    And the lines hold FullPrice, Discounted, FullPrice
    And Quote and Charge were each performed three times

  Scenario: An action with no library kind cannot be constructed
    Given class Bare(Action[Catalog, Price]) with line: Line and no perform
    When Bare(party=catalog, line=line) is constructed
    Then TypeError is raised naming Bare as abstract

  Scenario: Actions that need nothing from each other are performed together
    Given a second party Shipping with Estimate(Says[Shipping, Eta]) holding line, and LinePriced holding line, price and eta, each perform sleeping 0.2 s
    When answer is awaited for one line
    Then Quote and Estimate start at 0.0 s and end at 0.2 s, and Charge starts at 0.2 s

  Scenario: Connections open once before answers and close once after, last opened first
    Given Catalog and Payments connections whose open and close record their names
    When two answers are awaited inside opened(ShopConfig())
    Then the record is open:Catalog, open:Payments, perform, perform, perform, perform, close:Payments, close:Catalog

  Scenario: A client set as a private attribute leaves the connection frozen and unserialized
    Given class Http(Connection) with _client: httpx.AsyncClient = PrivateAttr() set in open()
    When open() is awaited on a constructed instance
    Then the client is set, assigning a field raises frozen_instance, model_dump_json() omits the client, and hash() works

  Scenario: An answer is one span per route and one per performed action
    Given the OpenTelemetry SDK with an in-memory exporter
    When answer is awaited for lines tea 3 and gold 50
    Then the root span is named Checkout with attributes tca.request "PlaceOrder" and tca.passes
    And its children are two spans named Quote with tca.party "Catalog" and tca.record "Price" and two named Charge with tca.party "Payments" and tca.record "Charged"
    And no attribute holds a request's or a record's contents
