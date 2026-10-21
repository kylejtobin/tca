Feature: Config reads the environment and .env with nested names; deployment values are Settings
  Decision records 0019, 0025.

  Scenario: Nested connection fields come from a .env file
    Given class Payments(Connection) with url: Url and key: Key
    And class ShopConfig(Config) with payments: Payments
    And a .env file in the working directory containing PAYMENTS__URL=https://p.test and PAYMENTS__KEY=k
    When ShopConfig() is constructed
    Then payments.url.root is HttpUrl("https://p.test/")
    And payments.key.root is a SecretStr

  Scenario: A Setting of each primitive constructs from .env
    Given class Url(Setting[HttpUrl]), class Key(Setting[SecretStr]) with root: SecretStr = Field(min_length=1), class Retries(Setting[int]) with root: int = Field(ge=0), class Wait(Setting[timedelta]) with root: timedelta = Field(gt=timedelta(0)), class Fee(Setting[Decimal]) with root: Decimal = Field(gt=0), class On(Setting[bool])
    And class Payments(Connection) with fields url: Url, key: Key, retries: Retries, wait: Wait, fee: Fee, on: On
    And class ShopConfig(Config) with payments: Payments
    And a .env file containing PAYMENTS__URL=https://p.test, PAYMENTS__KEY=k, PAYMENTS__RETRIES=3, PAYMENTS__WAIT=2, PAYMENTS__FEE=2.50, PAYMENTS__ON=true
    When ShopConfig().payments is read
    Then url.root is HttpUrl("https://p.test/"), key.root is a SecretStr, retries.root is 3, wait.root is timedelta(seconds=2), fee.root is Decimal("2.50"), on.root is True

  Scenario: A Setting keeps its constraint
    When Retries(-1) is constructed
    Then ValidationError is raised with type greater_than_equal

  Scenario: A Setting constructs in code from the typed value
    When Payments(url=Url(HttpUrl("https://p.test")), key=Key(SecretStr("k")), retries=Retries(3), wait=Wait(timedelta(seconds=2)), fee=Fee(Decimal("2.50")), on=On(True)) is constructed
    Then the instance constructs
