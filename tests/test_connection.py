from ynca.connection import YncaConnection


def test_close_uninitialized():
    connection = YncaConnection("dummy")
    connection.close()
