from ynca.uaw import Uaw

SYS = "SYS"
SUBUNIT = "UAW"

INITIALIZE_FULL_RESPONSES = [
    (
        (SUBUNIT, "AVAIL"),
        [
            (SUBUNIT, "AVAIL", "Ready"),
        ],
    ),
    (
        (SYS, "VERSION"),
        [
            (SYS, "VERSION", "Version"),
        ],
    ),
]


def test_initialize(connection, update_callback):

    connection.get_response_list = INITIALIZE_FULL_RESPONSES

    uaw = Uaw(connection)
    uaw.register_update_callback(update_callback)

    uaw.initialize()

    assert update_callback.call_count == 1