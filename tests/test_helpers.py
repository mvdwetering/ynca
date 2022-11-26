from ynca.helpers import RingBuffer, number_to_string_with_stepsize


def test_number_to_string_with_stepsize_decimals():
    assert "0" == number_to_string_with_stepsize(0.0, 0, 1)
    assert "0.0" == number_to_string_with_stepsize(0.0, 1, 1)
    assert "0.00" == number_to_string_with_stepsize(0.0, 2, 1)

    assert "1" == number_to_string_with_stepsize(1, 0, 1)
    assert "1.0" == number_to_string_with_stepsize(1, 1, 1)
    assert "1.00" == number_to_string_with_stepsize(1, 2, 1)

    assert "-1" == number_to_string_with_stepsize(-1, 0, 1)
    assert "-1.0" == number_to_string_with_stepsize(-1, 1, 1)
    assert "-1.00" == number_to_string_with_stepsize(-1, 2, 1)


def test_number_to_string_with_stepsize_sign():
    assert "0.00" == number_to_string_with_stepsize(0.0, 2, 0.5)
    assert "0.00" == number_to_string_with_stepsize(-0.0, 2, 0.5)

    assert "0.50" == number_to_string_with_stepsize(0.5, 2, 0.5)
    assert "-0.50" == number_to_string_with_stepsize(-0.5, 2, 0.5)

    assert "1.00" == number_to_string_with_stepsize(1.0, 2, 0.5)
    assert "-1.00" == number_to_string_with_stepsize(-1.0, 2, 0.5)


def test_number_to_string_with_stepsize_stepsize():
    assert "0.00" == number_to_string_with_stepsize(0.0, 2, 0.5)
    assert "0.00" == number_to_string_with_stepsize(0.1, 2, 0.5)
    assert "0.50" == number_to_string_with_stepsize(0.4, 2, 0.5)

    assert "0.00" == number_to_string_with_stepsize(-0.0, 2, 0.5)
    assert "0.00" == number_to_string_with_stepsize(-0.1, 2, 0.5)
    assert "-0.50" == number_to_string_with_stepsize(-0.4, 2, 0.5)

    assert "0.00" == number_to_string_with_stepsize(0.0, 2, 1)
    assert "1.00" == number_to_string_with_stepsize(1.1, 2, 1)
    assert "-1.00" == number_to_string_with_stepsize(-1.1, 2, 1)


def test_ringbuffer():
    rb = RingBuffer[int](3)
    assert rb.get_buffer() == []

    rb.add(1)
    assert rb.get_buffer() == [1]
    rb.add(2)
    assert rb.get_buffer() == [1, 2]
    rb.add(3)
    assert rb.get_buffer() == [1, 2, 3]
    rb.add(4)
    assert rb.get_buffer() == [2, 3, 4]
