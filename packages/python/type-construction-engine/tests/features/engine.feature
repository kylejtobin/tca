Feature: The engine proves a program at startup and answers a route by construction
  Decision records 0015, 0021, 0029, 0030, 0042, 0044, 0045, 0046, 0047, 0048, 0049, 0050, 0051. Program module
  shop, tests/type_construction_engine/shop.py: Sku, Quantity (gt 0), UnitPrice (gt 0), Threshold with default 100,
  Rate with default 0.9, ChargeId, Reason, OrderTotal (ge 0), CheapestLine (ge 0); Said(Setting[str]);
  Speaker(Connection) with says: Said and open and close that do nothing; Catalog, Payments and Fraud (Speaker);
  Line(Value) with sku and quantity; PlaceOrder(Request) with lines: tuple[Line, ...]; Price(Record) with amount:
  UnitPrice; Charged(Record) with charge alias "id"; Clear(Record) with status Literal "clear"; Flagged(Record) with
  status Literal "flagged" and reason: Reason; Says[P: Speaker, T: Record](Action[P, T]) whose perform returns
  hear(self, self.party.says.root); Quote(Says[Catalog, Price]) holding line; Screen(Says[Fraud, Clear | Flagged])
  holding order; LineTotal(Times[UnitPrice, Quantity]); Small(AtMost[LineTotal, Threshold]) and
  Large(Beyond[LineTotal, Threshold]), each with bound defaulted to Threshold(); Reduced(Times[LineTotal, Rate]) with
  right defaulted to Rate(); FullPrice(line, tier: Small, due: LineTotal); Discounted(line, tier: Large, due: Reduced);
  Charge(Says[Payments, Charged]) holding priced: Discounted | FullPrice; LinePaid(priced, charged);
  Cheapest(Least[LineTotal]); Screened(order, clear: Clear); Refused(order, flagged: Flagged); Paid(screened, lines:
  tuple[LinePaid, ...], cheapest); OrderPaid(Reply[Paid]) with computed total -> OrderTotal summing each line's
  due.root, charges, and cheapest -> CheapestLine from cheapest.chosen.root; OrderRefused(Reply[Refused]) with
  computed reason; Checkout(Route[PlaceOrder, OrderPaid | OrderRefused]); ShopConfig(catalog, payments, fraud). The
  environment holds CATALOG__SAYS='{"amount": "2.50"}', PAYMENTS__SAYS='{"id": "ch_1"}' and
  FRAUD__SAYS='{"status": "clear"}'.

  Scenario: A program's classes are the ones its module defines
    Given vars(shop) holds Says, Says[Catalog, Price], Quote and the imported Fact
    When classes(shop) is read
    Then it holds Quote and not Says, not Says[Catalog, Price] and not Fact

  Scenario: A route's request class is read from its request field
    When asked(Checkout) is read
    Then it is PlaceOrder

  Scenario: An action's records are read through the library kind's type variables
    When heard(Quote) and heard(Screen) are read
    Then they are (Price,) and (Clear, Flagged)

  Scenario: An action's party is the annotation of its party field
    When Quote.model_fields["party"].annotation is read
    Then it is Catalog

  Scenario: The proof is the classes a route constructs, once per run and once per element
    When prove(Checkout, shop) is read
    Then once per run holds PlaceOrder, Catalog, Payments, Fraud, Screen, Clear, Flagged, Reason, Screened, Refused, Cheapest, Paid, OrderPaid, OrderTotal, CheapestLine, OrderRefused and Checkout
    And once per element holds Line, Sku, Quantity, Quote, Price, UnitPrice, LineTotal, Small, Large, Reduced, Discounted, FullPrice, Charge, Charged, ChargeId and LinePaid

  Scenario: A carrier's scalars join the run with it
    When prove(Checkout, shop) is read
    Then Sku and Quantity are once per element, carried by Line, and UnitPrice is once per element, carried by Price
    And Reason is once per run, carried by Flagged

  Scenario: The proof reports every root fault at once
    Given shop whose Paid also holds unheard: Unheard, a record no action hears, and weight: Weight, a scalar nothing carries
    When proven is called on it
    Then ValidationError is raised with type missing at loc ("Paid", "unheard") and type missing at loc ("Paid", "weight")

  Scenario: A record no action hears is reported once, at the field that holds what it carries
    Given shop without Quote
    When proven is called on it
    Then ValidationError is raised with one error of type missing at loc ("LineTotal", "left") and message "no class fills LineTotal.left, which holds UnitPrice"

  Scenario: A record two actions hear is refused
    Given shop with a second Says[Catalog, Price] subclass Requote
    When proven is called on it
    Then ValidationError is raised with type hearer at loc ("Price",) and message "2 actions hear Price: Quote, Requote; exactly one must"

  Scenario: A class two computed fields produce is refused
    Given shop whose OrderRefused also has a computed field returning OrderTotal
    When proven is called on it
    Then ValidationError is raised with type producer at loc ("OrderTotal",) and message "2 computed fields produce OrderTotal: OrderPaid.total, OrderRefused.total; exactly one must"

  Scenario: A scalar two carriers hold is refused
    Given shop whose Charged also holds amount: UnitPrice
    When proven is called on it
    Then ValidationError is raised with type carrier at loc ("UnitPrice",) and message "2 classes carry UnitPrice: Charged, Price; exactly one must"

  Scenario: A party class held twice in the config is refused
    Given shop whose config holds catalog: Catalog and backup: Catalog
    When proven is called on it
    Then ValidationError is raised with type party at loc ("Catalog",) and message "2 config fields hold Catalog: backup, catalog; exactly one must"

  Scenario: Two classes that hold each other are refused as a cycle
    Given shop with Egg(chicken: Chicken, order: PlaceOrder) and Chicken(egg: Egg)
    When proven is called on it
    Then ValidationError is raised with type cycle at loc ("Egg",) and at loc ("Chicken",)

  Scenario: Two union members the proof can see both constructing are refused
    Given shop with Large rewritten as AtMost[LineTotal, Threshold], so Discounted and FullPrice both hold an AtMost over the same operands under tier
    When proven is called on it
    Then ValidationError is raised with exactly type overlap at loc ("Charge", "priced") and type overlap at loc ("LinePaid", "priced")

  Scenario: A relation its operands' constraints decide is refused
    Given shop whose Price also carries small: SmallAmount (gt 0, le 100) and large: LargeAmount (gt 100), with Impossible(Beyond[SmallAmount, LargeAmount]), Certain(AtMost[SmallAmount, LargeAmount]), Never(Equal[SmallAmount, LargeAmount]) and Outside(Between[LargeAmount, SmallAmount, SmallAmount]) held by Holder
    When proven is called on it
    Then ValidationError is raised with type relation at loc ("Impossible",) with message "Impossible never holds, by the constraints on its operands"
    And type relation at loc ("Certain",) with message "Certain never refuses, by the constraints on its operands"
    And type relation at loc ("Never",) with "never holds" and type relation at loc ("Outside",) with "never holds"

  Scenario: A small order constructs FullPrice
    When answer(Checkout, PlaceOrder.model_validate_json('{"lines": [{"sku": "tea", "quantity": 3}]}'), ShopConfig(), shop) is awaited
    Then the route's reply dumps {"total":"7.50","charges":["ch_1"],"cheapest":"7.50"}
    And reply.of.lines[0].priced is a FullPrice holding a Small whose value is the LineTotal 7.50
    And Large was asked for and refused with relation, and Discounted was never built
    And Quote, Screen and Charge were each performed once

  Scenario: A large order constructs Discounted
    When answer is awaited for one line of gold 50
    Then the route's reply dumps {"total":"112.500","charges":["ch_1"],"cheapest":"125.00"}
    And reply.of.lines[0].priced is a Discounted holding a Large and a Reduced whose root is 112.500

  Scenario: A derivation is constructed from the operands its carriers brought
    When answer is awaited for one line of tea 3
    Then LineTotal was constructed once from the UnitPrice carried by Price and the Quantity carried by Line, with root 7.50

  Scenario: A party that says no answers the other reply
    Given FRAUD__SAYS='{"status": "flagged", "reason": "velocity"}'
    When answer is awaited for one line of tea 3
    Then the route's reply is an OrderRefused that dumps {"reason":"velocity"}
    And Screened and Paid were never built

  Scenario: An action with no library kind cannot be constructed
    Given class Bare(Action[Catalog, Price]) with line: Line and no perform
    When Bare(party=catalog, line=line) is constructed
    Then TypeError is raised naming Bare as abstract

  Scenario: Independent actions are performed together
    Given each perform sleeping 0.2 s
    When answer is awaited for one line
    Then Quote and Screen start at 0.0 s and end at 0.2 s, and Charge starts at 0.2 s

  Scenario: Connections open once before answers and close once after, last opened first
    Given Catalog, Payments and Fraud connections whose open and close record their names
    When two one-line answers are awaited inside opened(ShopConfig())
    Then the record is open:Catalog, open:Payments, open:Fraud, six performs, close:Fraud, close:Payments, close:Catalog
    And the performs used three distinct connection instances

  Scenario: A connection without a library kind cannot be constructed
    Given class Bare(Connection) with says: Said and no open or close
    When Bare(says=...) is constructed
    Then TypeError is raised naming Bare as abstract

  Scenario: A client set as a private attribute leaves the connection frozen and unserialized
    Given class Http(Connection) with _client: httpx.AsyncClient = PrivateAttr() set in open()
    When open() is awaited on a constructed instance
    Then the client is set, assigning a field raises frozen_instance, model_dump_json() omits the client, and hash() works

  Scenario: A three-line order fans out per line and collects in order
    Given each perform sleeping 0.2 s
    When answer is awaited for lines tea 3, milk 1, jam 2
    Then Quote, LineTotal, Small, FullPrice, Charge and LinePaid are constructed once per line, and Screen, Cheapest and Paid once
    And three Quotes and the Screen start at 0.0 s and three Charges start at 0.2 s
    And the route's reply dumps {"total":"15.00","charges":["ch_1","ch_1","ch_1"],"cheapest":"2.50"}

  Scenario: Each line chooses its own outcome by the relation that holds
    When answer is awaited for lines tea 3, gold 50, jam 2
    Then the lines hold FullPrice, Discounted, FullPrice
    And the route's reply dumps {"total":"125.000","charges":["ch_1","ch_1","ch_1"],"cheapest":"5.00"}

  Scenario: A selection is constructed once from every element's value
    When answer is awaited for lines tea 3, gold 50, jam 2
    Then Cheapest holds three LineTotals in element order and its chosen is the jam line's, with root 5.00

  Scenario: A reply's fact that holds an element directly is refused
    Given shop with Wrong(order, one: LinePaid), OrderWrong(Reply[Wrong]) and Checkout(Route[PlaceOrder, OrderWrong])
    When proven is called on it
    Then ValidationError is raised with type scope at loc ("Checkout",) and message "Checkout exists once per element; a route exists once per run, so its reply's fact collects elements as tuple[X, ...] instead of holding one"

  Scenario: A tuple that collects a once-per-run class is refused
    Given shop with Collects(orders: tuple[Paid, ...]), OrderCollects(Reply[Collects]) and Checkout(Route[PlaceOrder, OrderCollects])
    When proven is called on it
    Then ValidationError is raised with type scope at loc ("Collects", "orders") and message "Collects.orders collects Paid, which exists once per run; hold it directly"

  Scenario: An answer is one span per route and one per performed action
    Given the OpenTelemetry SDK with an in-memory exporter
    When answer is awaited for lines tea 3 and gold 50
    Then the root span is named Checkout with attributes tca.request "PlaceOrder" and tca.passes 4
    And its children are one span named Screen with tca.party "Fraud" and tca.record "Clear", two named Quote with tca.party "Catalog" and tca.record "Price", and two named Charge with tca.party "Payments" and tca.record "Charged"
    And every status is unset
    And no attribute holds a request's or a record's contents
