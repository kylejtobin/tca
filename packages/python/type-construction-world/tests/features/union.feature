Feature: A choice is a union; members are told apart by their constraints
  Decision records 0002, 0003.

  Background:
    Given class Priced(Fact) with amount: int = Field(gt=0)
    And class Unpriced(Fact) with amount: int
    And class Quote(Fact) with status: Priced | Unpriced

  Scenario: Smart mode constructs the member whose constraint holds
    When Quote(status={"amount": 0}) is constructed
    Then status is an Unpriced
    When Quote(status={"amount": 5}) is constructed
    Then status is a Priced

  Scenario: An instance of a member is kept as given
    When Quote(status=Unpriced(amount=5)) is constructed
    Then status is an Unpriced
