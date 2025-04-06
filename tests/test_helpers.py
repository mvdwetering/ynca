from ynca.helpers import RingBuffer, number_to_string_with_stepsize


def test_number_to_string_with_stepsize_decimals() -> None:
    assert number_to_string_with_stepsize(0.0, 0, 1) == "0"
    assert number_to_string_with_stepsize(0.0, 1, 1) == "0.0"
    assert number_to_string_with_stepsize(0.0, 2, 1) == "0.00"

    assert number_to_string_with_stepsize(1, 0, 1) == "1"
    assert number_to_string_with_stepsize(1, 1, 1) == "1.0"
    assert number_to_string_with_stepsize(1, 2, 1) == "1.00"

    assert number_to_string_with_stepsize(-1, 0, 1) == "-1"
    assert number_to_string_with_stepsize(-1, 1, 1) == "-1.0"
    assert number_to_string_with_stepsize(-1, 2, 1) == "-1.00"


def test_number_to_string_with_stepsize_sign() -> None:
    assert number_to_string_with_stepsize(0.0, 2, 0.5) == "0.00"
    assert number_to_string_with_stepsize(-0.0, 2, 0.5) == "0.00"

    assert number_to_string_with_stepsize(0.5, 2, 0.5) == "0.50"
    assert number_to_string_with_stepsize(-0.5, 2, 0.5) == "-0.50"

    assert number_to_string_with_stepsize(1.0, 2, 0.5) == "1.00"
    assert number_to_string_with_stepsize(-1.0, 2, 0.5) == "-1.00"


def test_number_to_string_with_stepsize_stepsize() -> None:
    assert number_to_string_with_stepsize(0.0, 2, 0.5) == "0.00"
    assert number_to_string_with_stepsize(0.1, 2, 0.5) == "0.00"
    assert number_to_string_with_stepsize(0.4, 2, 0.5) == "0.50"

    assert number_to_string_with_stepsize(-0.0, 2, 0.5) == "0.00"
    assert number_to_string_with_stepsize(-0.1, 2, 0.5) == "0.00"
    assert number_to_string_with_stepsize(-0.4, 2, 0.5) == "-0.50"

    assert number_to_string_with_stepsize(0.0, 2, 1) == "0.00"
    assert number_to_string_with_stepsize(1.1, 2, 1) == "1.00"
    assert number_to_string_with_stepsize(-1.1, 2, 1) == "-1.00"


def test_ringbuffer() -> None:
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
