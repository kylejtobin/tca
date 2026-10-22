Feature: The engine proves a program at startup, placing every class, and answers a route by construction
  Decision records 0003, 0005, 0011, 0015, 0021, 0030, 0042, 0044, 0045, 0046, 0047, 0048, 0049, 0050, 0051, 0052,
  0053, 0054, 0055, 0056, 0057, 0058, 0059. The program is the test module
  tests/type_construction_engine/test_engine.py: Name(Scalar[str], min length 1); Element(Value) with name;
  Elements(Request) with each: tuple[Element, ...]; Said(Setting[str]); Party(Connection) with says: Said and open
  and close that do nothing; Teller(Party); Amount(Scalar[Decimal], gt 0); Share(Scalar[Decimal], gt 0, le 1);
  Part(Value) with share; Heard(Record) with amount: Amount and parts: tuple[Part, ...]; Tell[P: Party, T:
  Record](Action[P, T]) whose perform returns hear(self, self.party.says.root); Asked(Tell[Party, Heard]) holding
  element; Portion(Times[Share, Amount]); Portions(Sum[Portion]); Largest(Greatest[Portion]); Limit(Scalar[Decimal])
  with root defaulted to 10; Low(AtMost[Amount, Limit]); High(Beyond[Amount, Limit]); Word(Scalar[str]);
  Noted(Record) with word; Notify(Tell[Teller, Noted]) holding high: High; Cheap(element, low, portions, largest);
  Dear(element, high, portions, largest, noted: Noted); Total(Sum[Amount]); Concluded(valued: tuple[Cheap | Dear,
  ...], total: Total, at: Instant); Capped(Scalar[Decimal], le 30); Answered(Reply[Concluded]) with a computed field
  total -> Capped from total.root; Operation(Route[Elements, Answered]); Parties(Config) with party: Party and
  teller: Teller. The environment holds PARTY__SAYS='{"amount": "2.50", "parts": [{"share": "0.5"}, {"share":
  "0.5"}]}' and TELLER__SAYS='{"word": "dear"}'. faults.py beside it holds every fault the proof refuses in one
  module; stalls.py holds a program whose one outcome, Cheap holding Low, a party's answer refutes; lifecycle.py
  holds parties Fine, Down and Later that record their opening and closing, and the configs Opened and Lifecycle.

  Scenario: A program's classes are the ones its module defines
    Given vars(program) holds Tell, Tell[Party, Heard], Asked and the imported Fact
    When classes(program) is read
    Then it holds Asked and not Tell, not Tell[Party, Heard] and not Fact

  Scenario: A class whose forward reference is unresolved is rebuilt before it is read
    Given faults' Egg(chicken: "Chicken") defined before Chicken, with no model_rebuild in the module
    When proven is called on faults
    Then Egg.model_fields["chicken"].annotation is the class Chicken, and the cycle is reported

  Scenario: A route's request class is read from its request field
    When asked(Operation) is read
    Then it is Elements

  Scenario: An action's records are read through the library kind's type variables
    When heard(Asked) is read
    Then it is (Heard,)
    And for an action declared Tell[Party, Heard | Other], heard returns (Heard, Other)

  Scenario: A record union is heard as the member the text constructs
    Given Clear(Record) with status: Literal["clear"], Flagged(Record) with status: Literal["flagged"] and word: Word, and Screen(Tell[Party, Clear | Flagged])
    When hear(screen, '{"status": "clear"}') and hear(screen, '{"status": "flagged", "word": "no"}') are read
    Then the first is a Clear and the second a Flagged

  Scenario: A computed field names the classes it constructs as words
    Given Picked(Fact) with amount: Amount and a computed field which -> Amount | Limit
    When produces(Picked) is read
    Then it is {"which": (Amount, Limit)}

  Scenario: The proof places every class by its fields, as a path of element classes
    When proven(program) is read
    Then Elements, Limit, Total, Concluded and Operation are placed at ()
    And Element, Name, Asked, Heard, Amount, Portions, Largest, Low, Notify, Noted and Cheap are placed at (Element,)
    And Part, Share and Portion are placed at (Element, Part)
    And nothing is waiting, and the constants are (Limit,)

  Scenario: The classes a route builds are those its reply leads to that have no source of their own
    When proof.built(Operation) is read
    Then it is Asked, Portion, Portions, Largest, Low, High, Notify, Cheap, Dear, Total, Concluded, Answered and Operation
    And neither Heard nor Limit is among them

  Scenario: Each element is valued in its own scope and each part in its own, and the reply is the derivation
    When answer(Operation, Elements.model_validate_json('{"each": [{"name": "a"}, {"name": "b"}]}'), Parties(), proven(program)) is awaited
    Then Concluded.valued holds two Cheap, for a and b in that order
    And each Cheap's portions.root is 2.500 and its largest.chosen.root is 1.250
    And Total's root is 5.00 and the reply serializes to {"total":"5.00"}
    And Asked was performed once per element, together, and the run took 4 passes

  Scenario: The relation that holds decides the outcome, and the effect on that branch is performed
    Given PARTY__SAYS='{"amount": "25", "parts": [{"share": "1"}]}'
    When answer is awaited for one element
    Then Concluded.valued holds one Dear, whose high.ordering is 1, whose portions.root is 25 and whose noted.word.root is "dear"
    And the reply serializes to {"total":"25"}

  Scenario: A fresh scalar is constructed for each holder
    When answer is awaited twice for no elements
    Then each Concluded.at.root is an aware datetime and the second is later than the first
    And Concluded.model_validate({"valued": (), "total": Total(of=())}) raises ValidationError with type missing at loc ("at",)

  Scenario: No element collects the empty tuple
    When answer is awaited for no elements
    Then Concluded.valued is the empty tuple and Total's root is 0

  Scenario: A relation that cannot hold or cannot refuse is read from its operands' intervals
    When never is read for faults' Impossible, Certain, Never and Undecided, and for Low and Cheap
    Then they are "holds", "refuses", "holds", "refuses", None and None

  Scenario: An interval is read from the bounds, the default or the operation
    When interval is read for Amount, Share, Limit, Portion and Total
    Then they are Interval(low=0, low_strict=True), Interval(low=0, low_strict=True, high=1), Interval(low=10, high=10), Interval(low=0) and Interval(low=0)
    And outcomes(interval(Amount), interval(Limit)) is {-1, 0, 1}, and for faults' SmallAmount against LargeAmount it is {-1}

  Scenario: A scalar over int has no value between two integers
    Given Unit(Scalar[int]) with gt 0 and lt 2, One(Scalar[int]) with ge 1 and le 1, and Same(Equal[Unit, One])
    When interval(Unit) and never(Same) are read
    Then they are Interval(low=1, high=1) and "refuses"

  Scenario: Two facts told apart by complementary relations are proven exclusive
    When coexist(Cheap, Dear, proof.classes) is read
    Then it is False, since Low and High admit disjoint orderings of Amount against Limit
    And coexist(Cheap, Cheap, proof.classes) is True
    And coexist(AtOrUnder, Exactly, models(faults)) is True, since Equal implies AtMost

  Scenario: The proof refuses every fault at once, as one ValidationError titled Proof
    When proven is called on faults
    Then ValidationError is raised with type missing at loc ("Concluded", "unheard")
    And type cycle at loc ("Egg",) and at loc ("Chicken",), and not at ("Answered",)
    And type twice at loc ("Name",), ("Heard",) and ("Party",)
    And type unplaceable at loc ("Twin",)
    And type collects at loc ("Collects",)
    And type route at loc ("Misplaced",)
    And type unreached at loc ("Stray",)
    And type unmodeled at loc ("Bare", "count")
    And type boundary at loc ("Direct", "cheap") and at loc ("Parties", "limit")
    And type config at loc ("type_construction_engine.faults",)
    And type ambiguous at loc ("Either", "which")
    And type never at loc ("Impossible",), ("Certain",), ("Never",) and ("Undecided",)
    And type undiscriminated at loc ("Both",)
    And type undecided at loc ("Charge",), and not at ("Asked",)

  Scenario: A stalled run names the relation that did not hold with the ordering observed
    Given stalls, PARTY__SAYS='{"amount": "25"}' and one element
    When answer(stalls.Operation, request, stalls.Parties(), proven(stalls)) is awaited
    Then ValidationError is raised with exactly one error, type relation at loc ("Low",), message "Low did not hold: value Amount > bound Limit"

  Scenario: A stalled run names the selection with nothing to choose and not the complement that was decided
    Given PARTY__SAYS='{"amount": "2.50", "parts": []}' and one element
    When answer is awaited
    Then ValidationError is raised with exactly one error, type relation at loc ("Largest",), message "Largest did not hold: Tuple should have at least 1 item after validation, not 0"

  Scenario: A selection's shape is its tuple annotation
    When Least[Amount](of=()) is constructed
    Then ValidationError is raised with type too_short at loc ("of",)
    When Only[Element].model_validate({"of": ()}) is called
    Then ValidationError is raised with type missing at loc ("of", 0)
    When Only[Element].model_validate({"of": (a, b)}) is called with two elements
    Then ValidationError is raised with type too_long at loc ("of",)

  Scenario: A relation's ordering is computed, admitted by its Literal, excluded from its dump and never given
    When Low.model_validate({"value": Amount(5), "bound": Limit()}) is called
    Then ordering is -1 and model_dump() is {"value": Decimal("5"), "bound": Decimal("10")}
    When Low.model_validate({"value": Amount(11), "bound": Limit(), "ordering": 0}) is called
    Then ValidationError is raised with type computed at loc ("ordering",)
    When Low.model_validate({"value": Amount(5), "bound": Limit(), "ordering": -1}) is called
    Then ValidationError is raised with type computed at loc ("ordering",), the ordering it would have computed

  Scenario: An action or a connection without a library kind cannot be constructed
    Given class Bare(Action[Party, Heard]) with element: Element and no perform, and class Mute(Connection) with says: Said and no open or close
    When Bare(party=party, element=element) and Mute(says=said) are constructed
    Then TypeError is raised naming each as abstract

  Scenario: A failing action cancels the pass's others and propagates in a group
    Given the party raising ConnectionError on every perform
    When answer is awaited for two elements
    Then ExceptionGroup is raised whose exceptions are two ConnectionError

  Scenario: Connections open once before answers and close once after, last opened first
    Given lifecycle's Fine and Later in Lifecycle, in that order
    When two one-element answers are awaited inside opened(config)
    Then the record is open:Fine, open:Later, the two answers, close:Later, close:Fine

  Scenario: A connection that fails to open closes what opened before it
    Given lifecycle's Fine and Down in Opened
    When opened(config) is entered
    Then ConnectionError is raised and the record is open:Fine, open:Down, close:Fine

  Scenario: A client set as a private attribute leaves the connection frozen and unserialized
    Given Keyed(Party) with _client: object | None = PrivateAttr(default=None) set in open()
    When open() is awaited on a constructed instance
    Then the client is set, assigning says raises frozen_instance, model_dump_json() is {"says":"{}"}, and hash() is an int

  Scenario: An answer is one span per route and one per performed action
    Given the OpenTelemetry SDK with an in-memory exporter
    When answer is awaited for two elements
    Then the root span is named Operation with attributes tca.request "Elements" and tca.passes 4
    And its children are two spans named Asked with tca.party "Party" and tca.record "Heard"
    And no attribute holds the amount the party said

  Scenario: A reply's word that refuses refuses when the reply is serialized
    Given PARTY__SAYS='{"amount": "25", "parts": [{"share": "1"}]}' and two elements
    When answer is awaited and the reply's model_dump_json() is called
    Then the run answered with Total 50 and the call raised PydanticSerializationError holding "1 validation error for Capped" with less_than_equal
