Feature: Routes and actions declare through generic parameters and abstract properties
  Decision records 0005, 0015.

  Scenario: A route's arguments are read from its parametrized base
    Given class Checkout(Route[PlaceOrder, OrderPaid | OrderUnpaid])
    When the __mro__ of Checkout is searched for a base whose __pydantic_generic_metadata__["args"] is non-empty
    Then the args are (PlaceOrder, OrderPaid | OrderUnpaid)
    And Checkout.__pydantic_generic_metadata__ is {"origin": None, "args": (), "parameters": ()}

  Scenario: An abstract property typed by a parameter is satisfied by a subclass
    Given class Post[P: Connection, S: Record, T: Record](Action[P, T]) with @property @abstractmethod sends -> S
    And class Charge(Post[Payments, Payment, Charged]) with placed: Placed and a property sends returning Payment(amount=...)
    When Charge(placed=placed) is constructed
    Then sends is a Payment

  Scenario: A subclass that omits the abstract property cannot be constructed
    Given class Half(Post[Payments, Payment, Charged]) with paid: Paid and no sends
    When Half(paid=paid) is constructed
    Then TypeError is raised naming Half as abstract

  Scenario: A parametrized library kind's arguments are read from its base
    When the parametrized base of Charge with origin Post is read
    Then its args are (Payments, Payment, Charged)
