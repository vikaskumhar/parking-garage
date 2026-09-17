from datetime import datetime

import pytest

from parking_garage import FeeCalculator, ParkingGarage, Vehicle


@pytest.fixture
def garage():
    return ParkingGarage(
        floor_count=2,
        spaces_per_floor=3,
        compact_per_floor=1,
        ev_per_floor=1,
        pricing={"first_hour": 50, "additional_hour": 30, "daily_cap": 300},
    )


def test_first_hour_and_partial_hour_round_up():
    start = datetime(2024, 1, 1, 9, 0, 0)

    assert FeeCalculator.calculate(start, datetime(2024, 1, 1, 9, 30, 0), 50, 30, 300) == 50
    assert FeeCalculator.calculate(start, datetime(2024, 1, 1, 10, 20, 0), 50, 30, 300) == 80


def test_daily_cap_applies_across_day_boundaries():
    start = datetime(2024, 1, 1, 9, 0, 0)
    end = datetime(2024, 1, 2, 6, 0, 0)
    charge = FeeCalculator.calculate(start, end, 50, 30, 300)
    assert charge == 300


def test_check_in_and_checkout_with_standard_vehicle(garage):
    vehicle = Vehicle("RJ14AB1234", "standard")
    ticket = garage.check_in(vehicle, datetime(2024, 1, 1, 9, 0, 0))

    assert ticket.license_plate == "RJ14AB1234"
    assert ticket.spot.spot_type == "standard"

    fee = garage.check_out("RJ14AB1234", datetime(2024, 1, 1, 11, 15, 0))
    assert fee == 110
    assert garage.find_vehicle("RJ14AB1234") is None


def test_ev_vehicle_must_use_ev_spot_and_no_double_parking(garage):
    garage.check_in(Vehicle("EV1", "ev"), datetime(2024, 1, 1, 8, 0, 0))
    assert garage.available_spots("ev") == 1

    ticket = garage.check_in(Vehicle("EV2", "ev"), datetime(2024, 1, 1, 8, 30, 0))
    assert ticket.spot.spot_type == "ev"
    assert garage.available_spots("ev") == 0

    with pytest.raises(ValueError):
        garage.check_in(Vehicle("EV1", "ev"), datetime(2024, 1, 1, 9, 0, 0))


def test_find_vehicle_and_availability_lookup(garage):
    garage.check_in(Vehicle("COMPACT1", "compact"), datetime(2024, 1, 1, 7, 0, 0))

    found = garage.find_vehicle("COMPACT1")
    assert found is not None
    assert found.license_plate == "COMPACT1"
    assert found.spot.spot_type == "compact"
    assert garage.available_spots("compact") == 1
    assert garage.available_spots("standard") == 2


def test_garage_full_and_invalid_vehicle_type(garage):
    for index in range(1, 3):
        garage.check_in(Vehicle(f"V{index}", "standard"), datetime(2024, 1, 1, 8, index))

    with pytest.raises(ValueError):
        garage.check_in(Vehicle("FULL", "standard"), datetime(2024, 1, 1, 9, 0, 0))

    with pytest.raises(ValueError):
        garage.check_in(Vehicle("BAD", "truck"), datetime(2024, 1, 1, 9, 5, 0))


def test_ticket_lookup_and_spot_release(garage):
    ticket = garage.check_in(Vehicle("TICKET1", "standard"), datetime(2024, 1, 1, 12, 0, 0))
    found = garage.find_ticket(ticket.ticket_id)
    assert found is not None
    assert found.spot.occupied is True

    garage.check_out("TICKET1", datetime(2024, 1, 1, 13, 0, 0))
    assert garage.find_ticket(ticket.ticket_id) is None
    assert found.spot.occupied is False
