########################
Application Integration
########################


::

    import celpy
    expr = celpy.ExpressionBuilder().create_expression("""

    account.balance >= transaction.withdrawal
    || (account.overdraftProtection
    && account.overdraftLimit >= transaction.withdrawal  - account.balance)

    """)
    assert not expr.evaluate(account={"balance": 500, "overdraftProtection": False}, transaction={"withdrawl": 600})

To an extent, the Python classes are loosely based on the object model in https://github.com/google/cel-go

We don't need all the Go formalisms, however, and rely on Pythonic variants.
