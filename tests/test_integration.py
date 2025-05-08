from mock_serial import MockSerial  # type: ignore[import]

import ynca


def test_basic_end_to_end_connection_check(mock_serial: MockSerial) -> None:
    """A sanity check with everything integrated end-to-end."""
    # Keep alive
    mock_serial.stub(
        receive_bytes=b"@SYS:MODELNAME=?\r\n",
        send_bytes=b"@SYS:MODELNAME=TESTMODEL\r\n",
    )
    # Main
    mock_serial.stub(
        receive_bytes=b"@MAIN:AVAIL=?\r\n", send_bytes=b"@MAIN:AVAIL=Ready\r\n"
    )
    # Zone2
    mock_serial.stub(
        receive_bytes=b"@ZONE2:AVAIL=?\r\n", send_bytes=b"@ZONE2:AVAIL=Ready\r\n"
    )
    # Zone 3
    mock_serial.stub(
        receive_bytes=b"@ZONE3:AVAIL=?\r\n", send_bytes=b"@ZONE3:AVAIL=Not Ready\r\n"
    )
    # Zone 4
    mock_serial.stub(receive_bytes=b"@ZONE4:AVAIL=?\r\n", send_bytes=b"@RESTRICTED\r\n")

    y = ynca.YncaApi(mock_serial.port)

    result = y.connection_check()
    assert result.modelname == "TESTMODEL"
    assert len(result.zones) == 3
    assert "MAIN" in result.zones
    assert "ZONE2" in result.zones
    assert "ZONE3" in result.zones
    assert "ZONE4" not in result.zones

    y.close()
