Feature: The command line is rendered from the request class through the engine's reads and validates leniently
  Decision records 0005, 0023, 0026, 0027, 0029, 0030, 0055, 0059. The program is the test module
  tests/type_construction_cli/test_cli.py: Name(Scalar[str], min length 1, "What the thing is called.");
  Count(Scalar[int], gt 0); Amount(Scalar[Decimal], gt 0, "What is offered."); Kind(StrEnum) one, two;
  City(Scalar[str], min length 1); Place(Value) with city: City under the docstring "The city it goes to.";
  Tag(Scalar[str], min length 1); Label(Scalar[str]); Size(Scalar[int], ge 1); Element(Value) with label and size;
  Ask(Request) with name "The thing's name.", count "How many.", amount, kind "Which kind.", place, tags: tuple[Tag,
  ...] "Words attached.", each: tuple[Element, ...] "The elements, any number."; Said(Setting[str]) "What the party
  says."; Retries(Setting[int], ge 0, "How many times the party is asked again."); Party(Connection) with says and
  retries; Word(Scalar[str]); Heard(Record) with word; Tell and Asked(Tell[Party, Heard]) holding element;
  Counted(Fact) with element and heard; Concluded(Fact) with ask: Ask and counted: tuple[Counted, ...];
  Told(Reply[Concluded]) with computed fields name -> Name and words -> tuple[Word, ...]; Question(Route[Ask, Told])
  "Ask about a thing and its elements."; Parties(Config) with party. The environment holds PARTY__SAYS='{"word":
  "yes"}' and PARTY__RETRIES=0. The command is ask; ran(prog, args, module) is main's body over a module, and
  exits(prog, args, module) is ran with its refusals printed.

  Scenario: The program is proven before anything is listed or run, and its help lists routes and variables
    When ran("ask", [], program) is called
    Then the exit code is 0
    And stdout contains "usage: ask <route> [options]"
    And stdout contains "question        Ask about a thing and its elements."
    And stdout contains "PARTY__SAYS     What the party says."
    And stdout contains "PARTY__RETRIES  How many times the party is asked again. (>= 0)"

  Scenario: A route's help shows each option read from the request class
    When ran("ask", ["question", "--help"], program) is called
    Then argparse exits 0 and stdout contains "What is asked."
    And it contains "--name NAME        The thing's name. (min length 1)"
    And it contains "--count COUNT      How many. (> 0)"
    And it contains "--amount AMOUNT    What is offered. (> 0)", the class docstring where the field has none
    And it contains "--kind {one,two}   Which kind."
    And it contains "--place.city CITY  The city it goes to. (min length 1)"
    And it contains "--tags TAG         Words attached. (min length 1)"
    And it contains "--each JSON        The elements, any number."

  Scenario: The parsed options rebuild the tree the request validates from
    Given the parsed options {"name": "tea", "count": "3", "amount": "2.50", "kind": "two", "place.city": "Boston", "tags": ["gift", "rush"], "each": [{"label": "a", "size": 1}]}
    When tree(given, Ask) is read
    Then it is {"name": "tea", "count": "3", "amount": "2.50", "kind": "two", "place": {"city": "Boston"}, "tags": ["gift", "rush"], "each": [{"label": "a", "size": 1}]}
    And Ask.model_validate(tree, strict=False) constructs with count.root 3, amount.root Decimal("2.50"), kind Kind.TWO and each[0].size.root 1

  Scenario: An option not given is absent from the tree and the request reports it missing
    When exits("ask", ["question", ...GIVEN without --name], program) is called
    Then the exit code is 1
    And stderr contains "name" and "Field required"

  Scenario: A value outside a constraint exits 1 naming the field
    When exits("ask", ["question", ...GIVEN with --count 0], program) is called
    Then the exit code is 1
    And stderr contains "count" and "greater_than"

  Scenario: An unknown route exits 2 with the route list
    When ran("ask", ["nothing"], program) is called
    Then the exit code is 2
    And stderr contains "routes:"

  Scenario: A valid request reaches answer and the reply is printed
    When ran("ask", ["question", "--name", "tea", "--count", "3", "--amount", "2.50", "--kind", "two", "--place.city", "Boston", "--tags", "gift", "--tags", "rush", "--each", '{"label": "a", "size": 1}', "--each", '{"label": "b", "size": 2}'], program) is called
    Then the exit code is 0
    And stdout is '{"name":"tea","words":["yes","yes"]}' and a newline

  Scenario: The program's variables are listed from the config through the connections' settings
    When usage("ask", commands(proven(program)), config(program)) is read
    Then its last two lines are "  PARTY__SAYS     What the party says." and "  PARTY__RETRIES  How many times the party is asked again. (>= 0)"

  Scenario: The proof is computed once and passed to the run
    When proven(program) is read
    Then Counted is placed at (Element,) and Concluded at ()
