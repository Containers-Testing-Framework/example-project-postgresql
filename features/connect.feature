Feature: Postgresql connection

  Background:
    Given postgresql container param "POSTGRESQL_USER" is set to "user"
      And postgresql container param "POSTGRESQL_PASSWORD" is set to "pass"
      And postgresql container param "POSTGRESQL_DATABASE" is set to "db"

  Scenario: User account - smoke test
    When postgresql container is started
    Then postgresql connection can be established

  Scenario: Root account - smoke test
    Given postgresql container param "POSTGRESQL_ADMIN_PASSWORD" is set to "root_passw"
     When postgresql container is started
     Then postgresql connection with parameters can be established:
          | param               | value      |
          | POSTGRESQL_USER     | root       |
          | POSTGRESQL_PASSWORD | root_passw |
          | POSTGRESQL_DATABASE | db         |

  Scenario Outline: Incorrect connection data - user account
    When postgresql container is started
    Then postgresql connection with parameters can not be established:
          | param               | value      |
          | POSTGRESQL_USER     | <user>     |
          | POSTGRESQL_PASSWORD | <password> |
          | POSTGRESQL_DATABASE | <db>       |

    Examples:
    | user      | password | db  |
    | userr     | pass     | db  |
    | user      | passs    | db  |
    | user      | pass     | db1 |
    | \$invalid | pass     | db  |
    | user      | '        | db  |
    | user      | pass     | $invalid  |
    | user      | pass     | very_long_database_name_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx  |
    | very_long_username | pass     | db  |

  Scenario Outline: Incorrect connection data - root account
    Given postgresql container param "POSTGRESQL_ADMIN_PASSWORD" is set to "root_passw"
     When postgresql container is started
    Then postgresql connection with parameters can not be established:
          | param               | value      |
          | POSTGRESQL_USER     | root       |
          | POSTGRESQL_PASSWORD | <password> |
          | POSTGRESQL_DATABASE | <db>       |

    Examples:
    | password    | db  |
    | root_passw1 | db  |
    | root_passw  | db1 |
    | '           | db  |

  Scenario: Incomplete params
    When postgresql container is started
    Then postgresql connection with parameters can not be established:
          | param               | value |
          | POSTGRESQL_USER     | user  |
          | POSTGRESQL_PASSWORD | pass  |
     And postgresql connection with parameters can not be established:
          | param               | value |
          | POSTGRESQL_USER     | user  |
          | POSTGRESQL_DATABASE | pass  |
     And postgresql connection with parameters can not be established:
          | param               | value |
          | POSTGRESQL_PASSWORD | pass  |
          | POSTGRESQL_DATABASE | pass  |