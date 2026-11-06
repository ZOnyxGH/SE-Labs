# Lab 6: Code and Branch Coverage — Ride Share Fare

A Python module that computes extra-distance fares by cab type, zone, and subscription status, checks passenger/baggage limits, and reports driver pickup status.

## Files

| File | Description |
|---|---|
| `ride_share_fare.py` | Implementation module |
| `test_ride_share_fare.py` | Unit test suite targeting 100% statement and branch coverage |

## Running Tests & Coverage

Run `pytest` with coverage enabled:

```bash
pytest --cov=ride_share_fare --cov-branch --cov-report=term-missing
```

### Coverage Report

```
Name                 Stmts   Miss Branch BrPart  Cover   Missing
----------------------------------------------------------------
ride_share_fare.py      37      0     26      0   100%
----------------------------------------------------------------
TOTAL                   37      0     26      0   100%
============================== 23 passed in 0.42s ==============================
```
