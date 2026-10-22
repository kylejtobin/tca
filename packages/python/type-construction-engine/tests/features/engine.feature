Feature: The engine proves a program at startup and answers a route by construction
  Decision records 0015, 0021, 0029, 0030, 0042, 0044, 0045, 0046, 0047, 0048, 0049, 0050, 0051, 0052, 0053, 0054. The
  program is the test module tests/type_construction_engine/test_engine.py: Name(Scalar[str]); Element(Value) with name;
  Elements(Request) with each: tuple[Element, ...]; Said(Setting[str]); Party(Connection) with says: Said and open and
  close that do nothing; Amount(Scalar[Decimal], gt 0); Heard(Record) with amount: Amount; Tell[P: Party, T:
  Record](Action[P, T]) whose perform returns hear(self, self.party.says.root); Asked(Tell[Party, Heard]) holding
  element; Limit(Scalar[Decimal]) with default 10; Low(AtMost[Amount, Limit]) and High(Beyond[Amount, Limit]), each
  with bound defaulted to Limit(); Cheap(element, low: Low); Dear(element, high: High); Total(Sum[Amount]);
  Concluded(valued: tuple[Cheap | Dear, ...], total: Total); Capped(Scalar[Decimal], le 30); Answered(Reply[Concluded])
  with a computed field total -> Capped from total.root; Operation(Route[Elements, Answered]); Parties(Config) with party: Party. The environment holds PARTY__SAYS='{"amount": "2.50"}'. The program
  faults.py beside it holds every fault the proof refuses in one module: SmallAmount (gt 0, le 100) and LargeAmount (gt
  100) carried by Elements; Name carried by Heard as well as by Element; Low with no complement; Unheard(Record) held by
  Concluded and heard by no action; Impossible(Beyond[SmallAmount, LargeAmount]),
  Certain(AtMost[SmallAmount, LargeAmount]) and Never(Equal[SmallAmount, LargeAmount]); AtOrUnder(AtMost[Amount, Limit])
  and Exactly(Equal[Amount, Limit]) held by Either.which as a union; Near[A, B](Relation) declaring no constraints with
  Undecided(Near[Amount, Limit]); Stray(Scalar[str]) held by nothing; Reasked, a second Tell[Party, Heard]; Parties
  holding party and backup, both Party; Egg(chicken: Chicken, elements) and Chicken(egg: Egg); Wrong(cheap: Cheap),
  AnsweredWrong(Reply[Wrong]) and Misplaced(Route[Elements, AnsweredWrong]); Collects(every: tuple[Concluded, ...]);
  and Heard holding tags: tuple[Tag, ...] while heard once per element.

  Scenario: A program's classes are the ones its module defines
    Given vars(program) holds Tell, Tell[Party, Heard], Asked and the imported Fact
    When classes(program) is read
    Then it holds Asked and not Tell, not Tell[Party, Heard] and not Fact

  Scenario: A class whose forward reference is unresolved is rebuilt before it is read
    Given faults' Egg(chicken: "Chicken") defined before Chicken, with no model_rebuild in the module
    When proven is called on faults
    Then Egg.model_fields["chicken"].annotation is the class Chicken, and the cycle is reported

  Scenario: The proof is read once per process
    When prove(Operation, program) is read twice and proven(program) is called twice
    Then the same set is returned both times and proven returns None both times

  Scenario: A route's request class is read from its request field
    When asked(Operation) is read
    Then it is Elements

  Scenario: An action's records are read through the library kind's type variables
    When heard(Asked) is read
    Then it is (Heard,)
    And for an action declared Tell[Party, Heard | Other], heard returns (Heard, Other)

  Scenario: A computed field produces the classes its return type names
    Given Picked(Fact) with amount: Amount and a computed field which -> Amount | Limit
    When produced(Picked) is read
    Then it is {"which": (Amount, Limit)}

  Scenario: The proof is the set of classes that join from the request
    When prove(Operation, program) is read
    Then it holds Elements, Element, Name, Party, Asked, Heard, Amount, Low, High, Cheap, Dear, Total, Concluded, Answered, Capped and Operation

  Scenario: Scope is read as the element a class descends from
    When descends(Cheap, program), descends(Asked, program) and descends(Amount, program) are read
    Then each is {Element}, through Cheap's element field, Asked's element field, and Heard, which carries Amount and is heard by Asked
    And descends(Total, program) and descends(Operation, program) are empty

  Scenario: A class no field names is refused as the mirror of missing
    When proven is called on faults
    Then ValidationError is raised with type unused at loc ("Stray",) and message "no field holds Stray; hold it or delete it"
    And Heard, which no field holds but which carries Amount, is not reported, since what it carries is held

  Scenario: A record no action hears is reported at the field that holds it
    When proven is called on faults
    Then ValidationError is raised with type missing at loc ("Concluded", "unheard")

  Scenario: A record two actions hear is refused
    When proven is called on faults
    Then ValidationError is raised with type hearer at loc ("Heard",)

  Scenario: A scalar two carriers hold is refused
    When proven is called on faults
    Then ValidationError is raised with type carrier at loc ("Name",), carried by Element and by Heard

  Scenario: A party class held twice in the config is refused
    When proven is called on faults
    Then ValidationError is raised with type party at loc ("Party",)

  Scenario: Two classes that hold each other are refused as a cycle, beside the root faults
    When proven is called on faults
    Then ValidationError is raised with type cycle at loc ("Egg",) and at loc ("Chicken",), and Answered, which waits on Concluded's missing Unheard, is not reported as a cycle

  Scenario: A relation its operands' bounds decide is refused
    When proven is called on faults
    Then ValidationError is raised with type relation at loc ("Impossible",) and message "Impossible never holds, by the constraints on its operands"
    And type relation at loc ("Certain",) and message "Certain never refuses, by the constraints on its operands"
    And type relation at loc ("Never",) and "never holds"

  Scenario: Two union members the proof decides can both hold are refused
    When proven is called on faults
    Then ValidationError is raised with type overlap at loc ("Either", "which"), since Equal implies AtMost over the same operands

  Scenario: Two facts told apart by complementary relations are decided disjoint
    When coexist(Cheap, Dear, program) is read
    Then it is False, since Low and High over Amount and Limit cannot both hold
    And coexist(Cheap, Cheap, program) is True

  Scenario: A relation kind that declares no constraints is refused as undecidable
    When proven is called on faults
    Then ValidationError is raised with type undecidable at loc ("Undecided",) and message "Undecided declares no constraints, so the proof cannot tell what it decides"

  Scenario: A scalar over int has no value between two integers
    Given Unit(Scalar[int]) with gt 0 and lt 2, One(Scalar[int]) with ge 1 and le 1, and Same(Equal[Unit, One])
    When never(Same) is read
    Then it is "refuses", since both can only be 1

  Scenario: The solver decides difference constraints with strictness
    When feasible is called with x - 0 <= 5 and 0 - x <= -5
    Then it is True
    When feasible is called with x - 0 <= 5 and 0 - x < -5
    Then it is False

  Scenario: Each element is valued in its own run and collected in order
    When answer(Operation, Elements.model_validate_json('{"each": [{"name": "a"}, {"name": "b"}]}'), Parties(), program) is awaited
    Then Concluded.valued holds two Cheap, for a and b in that order, and Total's root is 5.00
    And Asked was performed once per element, together

  Scenario: The relation that holds decides the outcome
    Given PARTY__SAYS='{"amount": "25"}'
    When answer is awaited for one element
    Then Concluded.valued[0] is a Dear holding a High, and Low was asked for and refused with relation

  Scenario: No element collects the empty tuple
    When answer is awaited for no elements
    Then Concluded.valued is the empty tuple and Total's root is 0

  Scenario: A computed field whose scalar refuses propagates the refusal
    Given PARTY__SAYS='{"amount": "25"}'
    When answer is awaited for two elements, so the total is 50 and Capped refuses it
    Then ValidationError is raised out of answer with one error of type less_than_equal at loc ()

  Scenario: A stalled run names the relation that did not hold
    Given faults, whose only outcome for an element is Cheap, PARTY__SAYS and BACKUP__SAYS with an amount of 25 over the limit, and a request with small 50 and large 150
    When answer is awaited for one element
    Then ValidationError is raised with type relation at loc ("Low",) and message "Low did not hold: Amount exceeds Limit"

  Scenario: A route that descends from an element is refused
    When proven is called on faults
    Then ValidationError is raised with type scope at loc ("Misplaced",), since Wrong holds Cheap, which exists once per element

  Scenario: A tuple that collects a once-per-run class is refused
    When proven is called on faults
    Then ValidationError is raised with type scope at loc ("Collects", "every"), since Concluded descends from nothing

  Scenario: A record heard once per element that holds a collection is refused
    When proven is called on faults
    Then ValidationError is raised with type scope at loc ("Heard",)

  Scenario: An action or a connection without a library kind cannot be constructed
    Given class Bare(Action[Party, Heard]) with element: Element and no perform, and class Mute(Connection) with says: Said and no open or close
    When Bare(party=party, element=element) and Mute(says=said) are constructed
    Then TypeError is raised naming each as abstract

  Scenario: A failing action cancels the pass's others and propagates in a group
    Given the party raising ConnectionError on every perform
    When answer is awaited for two elements
    Then ExceptionGroup is raised whose exceptions are two ConnectionError

  Scenario: Connections open once before answers and close once after, last opened first
    Given Fine and Later, two parties whose open and close record their names, in a config in that order
    When two one-element answers are awaited inside opened(config)
    Then the record is open:Fine, open:Later, the two answers, close:Later, close:Fine

  Scenario: A client set as a private attribute leaves the connection frozen and unserialized
    Given Keyed(Party) with _client: object | None = PrivateAttr(default=None) set in open()
    When open() is awaited on a constructed instance
    Then the client is set, assigning says raises frozen_instance, model_dump_json() is {"says":"{}"}, and hash() is an int

  Scenario: A connection that fails to open closes what opened before it
    Given a config of Fine, whose open and close record, and Down, whose open raises ConnectionError
    When opened(config) is entered
    Then ConnectionError is raised and the record is open:Fine, open:Down, close:Fine

  Scenario: An answer is one span per route and one per performed action
    Given the OpenTelemetry SDK with an in-memory exporter
    When answer is awaited for two elements
    Then the root span is named Operation with attributes tca.request "Elements" and tca.passes 3
    And its children are two spans named Asked with tca.party "Party" and tca.record "Heard"
    And no attribute holds the amount the party said
