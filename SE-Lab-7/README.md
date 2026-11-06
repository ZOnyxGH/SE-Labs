# Lab 7: Fuzz Testing — Ride Share Fare

A Python module that parses trip details, calculates average fares from CSV data, and computes payable fares after promotional discounts. Fuzz testing is performed using the `Hypothesis` framework.

## Files

| File | Description |
|---|---|
| `ride_share_fare.py` | Implementation module |
| `test_ride_share_fare.py` | Hypothesis fuzz and property-based tests |

## Running Tests

Run `pytest` to execute the fuzz test suite:

```bash
pytest -v test_ride_share_fare.py
```

### Test Overview

- `test_parse_trip_no_crash`: Fuzzes `parse_trip` using arbitrary strings and `None` (`st.text() | st.none()`), handling expected formatting exceptions cleanly without crashing.
- `test_fare_average_no_crash`: Fuzzes `fare_average` using arbitrary strings and `None`, ensuring safe handling of non-integer or empty CSV inputs.
- `test_payable_fare_no_crash`: Fuzzes `payable_fare` using arbitrary text and `None` to confirm resilience against invalid delimiters and values.
- Additional property tests verify correctness on validly formatted inputs.
