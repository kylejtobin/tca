Feature: Routes and actions declare through generic parameters, fields the kind holds, and abstract properties
  Decision records 0005, 0015.

  Scenario: A route's request and reply are the annotations of its fields
    Given class Checkout(Route[PlaceOrder, OrderPaid | OrderUnpaid])
    When Checkout.model_fields["request"].annotation and ["reply"].annotation are read
    Then they are PlaceOrder and OrderPaid | OrderUnpaid
    And Checkout.__pydantic_generic_metadata__ is {"origin": None, "args": (), "parameters": ()}

  Scenario: An action's party is the annotation of the field the kind holds
    Given class Post[P: Connection, S: Record, T: Record](Action[P, T]) with @property @abstractmethod sends -> S
    And class Charge(Post[Payments, Payment, Charged]) with placed: Placed and a property sends returning Payment(amount=...)
    When Charge.model_fields["party"].annotation is read
    Then it is Payments

  Scenario: An abstract property typed by a parameter is satisfied by a subclass
    When Charge(party=payments, placed=placed) is constructed
    Then sends is a Payment

  Scenario: A subclass that omits the abstract property cannot be constructed
    Given class Half(Post[Payments, Payment, Charged]) with paid: Paid and no sends
    When Half(party=payments, paid=paid) is constructed
    Then TypeError is raised naming Half as abstract

  Scenario: An action without a party cannot be constructed
    When Charge(placed=placed) is constructed
    Then ValidationError is raised with type missing at loc ("party",)

  Scenario: A parametrized library kind's arguments are read from its base
    When parametrized(Charge) is read
    Then it yields Post with (Payments, Payment, Charged), then Action with (Payments, Charged)

  Scenario: An action declares a union of records as what it hears
    Given class Screen(Says[Fraud, Clear | Flagged]) with order: PlaceOrder
    When basedpyright checks the module and parametrized(Screen) is read
    Then it reports no error, and the Action base's second argument is Clear | Flagged
