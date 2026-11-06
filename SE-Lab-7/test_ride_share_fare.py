from hypothesis import given, strategies as st
from ride_share_fare import parse_trip, fare_average, payable_fare

# Fuzz tests using arbitrary text or None to ensure functions don't crash unhandled

@given(st.text() | st.none())
def test_parse_trip_no_crash(s):
    try:
        res = parse_trip(s)
        # If input happened to be valid, verify the output types
        assert isinstance(res, tuple) and len(res) == 2
        assert isinstance(res[0], str)
        assert isinstance(res[1], float)
    except (ValueError, AttributeError):
        # Expected errors on malformed string or None
        pass


@given(st.text() | st.none())
def test_fare_average_no_crash(s):
    try:
        res = fare_average(s)
        # If valid, result must be an integer average
        assert isinstance(res, int)
    except (ValueError, AttributeError, ZeroDivisionError):
        # Expected errors on non-integer, empty, or None
        pass


@given(st.text() | st.none())
def test_payable_fare_no_crash(s):
    try:
        res = payable_fare(s)
        # If valid, payable fare should be a non-negative number
        assert isinstance(res, (int, float))
        assert res >= 0
    except (ValueError, AttributeError):
        # Expected errors on missing '|' or non-numeric values
        pass


# Extra property-based checks on validly formatted inputs

@given(st.text(min_size=1).filter(lambda x: ":" not in x), st.floats(min_value=0, max_value=500, allow_nan=False))
def test_parse_trip_valid_inputs(cab_name, km):
    input_str = f"{cab_name}:{km}"
    cab, dist = parse_trip(input_str)
    assert cab == cab_name.strip().title()
    assert abs(dist - km) < 1e-4

@given(st.lists(st.integers(min_value=10, max_value=1000), min_size=1, max_size=20))
def test_fare_average_valid_list(fares):
    csv_str = ",".join(str(f) for f in fares)
    avg = fare_average(csv_str)
    assert avg == sum(fares) // len(fares)

@given(st.floats(min_value=10, max_value=1000, allow_nan=False), st.floats(min_value=0, max_value=200, allow_nan=False))
def test_payable_fare_valid_inputs(fare, promo):
    input_str = f"{fare}|{promo}"
    result = payable_fare(input_str)
    expected = max(float(fare) * 1.18 - float(promo), 0.0)
    assert abs(result - expected) < 1e-4
