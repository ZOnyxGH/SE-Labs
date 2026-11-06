import pytest
from ride_share_fare import extra_distance_fare, seats_and_bags_ok, pickup_status

# Starter example tests
def test_within_included_distance():
    assert extra_distance_fare("sedan", 5, "city", False) == 0

def test_seats_and_bags_ok():
    assert seats_and_bags_ok(2, 1, False) is True


# --- extra_distance_fare tests ---

def test_unknown_cab_type():
    with pytest.raises(ValueError, match="unknown cab type"):
        extra_distance_fare("auto", 10, "city", False)

def test_negative_distance():
    with pytest.raises(ValueError, match="invalid distance"):
        extra_distance_fare("mini", -4, "city", False)

def test_exact_included_distance():
    # Mini has 5 km included, extra = 0
    assert extra_distance_fare("mini", 5, "city", False) == 0

def test_subscriber_extra_km_non_suv():
    # Subscriber on sedan gets 8 + 3 = 11 km included
    # 10 km is within the 11 km limit -> 0
    assert extra_distance_fare("sedan", 10, "city", True) == 0
    # 13 km means 2 extra km at city rate 12 -> 24
    assert extra_distance_fare("sedan", 13, "city", True) == 24

def test_subscriber_suv_no_bonus():
    # SUV subscriber should not get the +3 bonus, keeps base 12 km
    # 15 km means 3 extra km at city rate 12 -> 36
    assert extra_distance_fare("suv", 15, "city", True) == 36

def test_city_rate_short_extra():
    # Mini has 5 km included; 15 km means 10 extra km at city rate 12 -> 120
    assert extra_distance_fare("mini", 15, "city", False) == 120

def test_non_city_rate_short_extra():
    # Mini has 5 km included; 10 km means 5 extra km at non-city rate 18 -> 90
    assert extra_distance_fare("mini", 10, "rural", False) == 90

def test_extra_over_20_city():
    # Mini included 5 km; distance 30 km -> 25 extra km
    # Extra > 20 in city -> rate = 12 + 8 = 20 -> 25 * 20 = 500
    assert extra_distance_fare("mini", 30, "city", False) == 500

def test_extra_over_20_outstation():
    # Sedan included 8 km; distance 38 km -> 30 extra km
    # Extra > 20 and outstation -> rate = 18 + 8 + 4 = 30 -> 30 * 30 = 900
    assert extra_distance_fare("sedan", 38, "outstation", False) == 900

def test_extra_over_20_other_zone():
    # SUV included 12 km; distance 35 km -> 23 extra km
    # Extra > 20 and other non-city/non-outstation zone -> rate = 18 + 8 = 26 -> 23 * 26 = 598
    assert extra_distance_fare("suv", 35, "suburbs", False) == 598


# --- seats_and_bags_ok tests ---

def test_wheelchair_valid_passengers():
    # Max 2 passengers when wheelchair needed
    assert seats_and_bags_ok(2, 4, True) is True

def test_wheelchair_too_many_passengers():
    assert seats_and_bags_ok(3, 1, True) is False

def test_exceeds_max_passengers():
    # Without wheelchair, max passengers is 4
    assert seats_and_bags_ok(5, 1, False) is False

def test_valid_bags():
    # Within 4 passengers and up to 2 bags
    assert seats_and_bags_ok(4, 2, False) is True

def test_too_many_bags():
    # 3 bags exceeds the limit of 2
    assert seats_and_bags_ok(3, 3, False) is False


# --- pickup_status tests ---

def test_pickup_scheduled_airport_on_time():
    # Cutoff = 10 (scheduled) + 10 (airport) = 20
    assert pickup_status(20, True, True) == "on_time"

def test_pickup_scheduled_airport_delayed():
    # Cutoff = 20, threshold for delayed is 20 - 15 = 5
    assert pickup_status(10, True, True) == "delayed"
    assert pickup_status(5, True, True) == "delayed"

def test_pickup_scheduled_airport_missed():
    # Below cutoff - 15 (< 5)
    assert pickup_status(4, True, True) == "missed"

def test_pickup_unscheduled_non_airport_on_time():
    # Cutoff = 5
    assert pickup_status(5, False, False) == "on_time"
    assert pickup_status(12, False, False) == "on_time"

def test_pickup_unscheduled_non_airport_delayed():
    # Cutoff = 5, delayed between -10 and 4
    assert pickup_status(0, False, False) == "delayed"
    assert pickup_status(-10, False, False) == "delayed"

def test_pickup_unscheduled_non_airport_missed():
    # Less than -10
    assert pickup_status(-11, False, False) == "missed"
