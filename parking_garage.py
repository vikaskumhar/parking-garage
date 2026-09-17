from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional


VALID_VEHICLE_TYPES = {"compact", "standard", "ev"}
VALID_SPOT_TYPES = {"compact", "standard", "ev"}


class ParkingGarageError(ValueError):
    pass


@dataclass
class Vehicle:
    license_plate: str
    vehicle_type: str

    def __post_init__(self):
        self.license_plate = str(self.license_plate).strip().upper()
        if not self.license_plate:
            raise ParkingGarageError("License plate cannot be empty")

        self.vehicle_type = str(self.vehicle_type).strip().lower()
        if self.vehicle_type not in VALID_VEHICLE_TYPES:
            raise ParkingGarageError(f"Invalid vehicle type: {self.vehicle_type}")


@dataclass
class ParkingSpot:
    spot_id: str
    floor_number: int
    spot_number: int
    spot_type: str
    occupied: bool = False

    def __post_init__(self):
        self.spot_type = str(self.spot_type).strip().lower()
        if self.spot_type not in VALID_SPOT_TYPES:
            raise ParkingGarageError(f"Invalid spot type: {self.spot_type}")

    @property
    def label(self) -> str:
        return f"{self.spot_type.upper()}-{self.spot_number:03d}"


@dataclass
class ParkingTicket:
    ticket_id: str
    vehicle: Vehicle
    spot: ParkingSpot
    entry_time: datetime
    exit_time: Optional[datetime] = None
    fee: Optional[int] = None

    @property
    def license_plate(self) -> str:
        return self.vehicle.license_plate


class FeeCalculator:
    @staticmethod
    def _calculate_segment(
        duration_seconds: float,
        first_hour_rate: float,
        additional_hour_rate: float,
    ) -> int:
        if duration_seconds <= 0:
            return 0

        hours = max(1, math.ceil(duration_seconds / 3600))
        if hours <= 1:
            return int(first_hour_rate)
        return int(first_hour_rate + (hours - 1) * additional_hour_rate)

    @staticmethod
    def calculate(
        entry_time: datetime,
        exit_time: datetime,
        first_hour_rate: float,
        additional_hour_rate: float,
        daily_cap: float,
    ) -> int:
        if entry_time > exit_time:
            raise ParkingGarageError("Exit time must be after entry time")

        total_fee = 0
        current = entry_time

        while current < exit_time:
            window_end = min(exit_time, current + timedelta(days=1))
            window_seconds = (window_end - current).total_seconds()
            window_fee = FeeCalculator._calculate_segment(
                window_seconds,
                first_hour_rate,
                additional_hour_rate,
            )
            if daily_cap > 0:
                window_fee = min(window_fee, int(daily_cap))
            total_fee += window_fee
            current = window_end

        return total_fee

    @classmethod
    def calculate_by_rates(cls, entry_time: datetime, exit_time: datetime, pricing: Dict[str, float]) -> int:
        return cls.calculate(
            entry_time,
            exit_time,
            pricing.get("first_hour", 0),
            pricing.get("additional_hour", 0),
            pricing.get("daily_cap", 0),
        )


class ParkingGarage:
    def __init__(
        self,
        floor_count: int = 1,
        spaces_per_floor: int = 20,
        compact_per_floor: int = 0,
        ev_per_floor: int = 0,
        pricing: Optional[Dict[str, float]] = None,
    ) -> None:
        if floor_count <= 0 or spaces_per_floor <= 0:
            raise ParkingGarageError("Garage dimensions must be positive")

        self.floor_count = int(floor_count)
        self.spaces_per_floor = int(spaces_per_floor)
        self.compact_per_floor = int(compact_per_floor)
        self.ev_per_floor = int(ev_per_floor)

        default_pricing = {"first_hour": 50, "additional_hour": 30, "daily_cap": 300}
        self.pricing = {**default_pricing, **(pricing or {})}

        self.spots_by_id: Dict[str, ParkingSpot] = {}
        self.spots_by_floor: Dict[int, List[ParkingSpot]] = {}
        self._sessions_by_plate: Dict[str, ParkingTicket] = {}
        self._sessions_by_ticket: Dict[str, ParkingTicket] = {}
        self._ticket_counter = 1000
        self._build_garage()

    @property
    def active_sessions(self) -> List[ParkingTicket]:
        return list(self._sessions_by_plate.values())

    @property
    def total_spots(self) -> int:
        return len(self.spots_by_id)

    def _build_garage(self) -> None:
        for floor_number in range(1, self.floor_count + 1):
            self.spots_by_floor[floor_number] = []
            for spot_number in range(1, self.spaces_per_floor + 1):
                if spot_number <= self.compact_per_floor:
                    spot_type = "compact"
                elif spot_number <= self.compact_per_floor + self.ev_per_floor:
                    spot_type = "ev"
                else:
                    spot_type = "standard"

                spot = ParkingSpot(
                    spot_id=f"F{floor_number}-{spot_type.upper()}-{spot_number:03d}",
                    floor_number=floor_number,
                    spot_number=spot_number,
                    spot_type=spot_type,
                )
                self.spots_by_id[spot.spot_id] = spot
                self.spots_by_floor[floor_number].append(spot)

    def _next_ticket_id(self) -> str:
        self._ticket_counter += 1
        return f"T{self._ticket_counter}"

    def available_spots(self, spot_type: Optional[str] = None) -> int:
        normalized = (spot_type or "").strip().lower()
        count = 0
        for spot in self.spots_by_id.values():
            if normalized and spot.spot_type != normalized:
                continue
            if not spot.occupied:
                count += 1
        return count

    def is_ev_spot_available(self) -> bool:
        return self.available_spots("ev") > 0

    def _find_free_spot_for_vehicle(self, vehicle: Vehicle) -> Optional[ParkingSpot]:
        if vehicle.vehicle_type == "ev":
            ordered_types = ["ev"]
        elif vehicle.vehicle_type == "compact":
            ordered_types = ["compact", "standard"]
        else:
            ordered_types = ["standard"]

        for spot_type in ordered_types:
            for spot in self.spots_by_id.values():
                if spot.spot_type == spot_type and not spot.occupied:
                    return spot
        return None

    def find_vehicle(self, license_plate: str) -> Optional[ParkingTicket]:
        plate = str(license_plate).strip().upper()
        return self._sessions_by_plate.get(plate)

    def find_ticket(self, ticket_id: str) -> Optional[ParkingTicket]:
        return self._sessions_by_ticket.get(str(ticket_id).strip().upper())

    def get_occupied_spots(self) -> List[ParkingSpot]:
        return [spot for spot in self.spots_by_id.values() if spot.occupied]

    def check_in(self, vehicle: Vehicle, entry_time: Optional[datetime] = None) -> ParkingTicket:
        if not isinstance(vehicle, Vehicle):
            if isinstance(vehicle, str):
                vehicle = Vehicle(vehicle, "standard")
            else:
                raise ParkingGarageError("Vehicle object required")

        if vehicle.license_plate in self._sessions_by_plate:
            raise ParkingGarageError(f"Vehicle {vehicle.license_plate} is already parked")

        spot = self._find_free_spot_for_vehicle(vehicle)
        if spot is None:
            raise ParkingGarageError(f"No compatible spot available for {vehicle.vehicle_type} vehicle")

        if entry_time is None:
            entry_time = datetime.now()

        ticket_id = self._next_ticket_id()
        ticket = ParkingTicket(ticket_id=ticket_id, vehicle=vehicle, spot=spot, entry_time=entry_time)
        spot.occupied = True
        self._sessions_by_plate[vehicle.license_plate] = ticket
        self._sessions_by_ticket[ticket_id] = ticket
        return ticket

    def check_out(self, license_plate: str, exit_time: Optional[datetime] = None) -> int:
        plate = str(license_plate).strip().upper()
        ticket = self._sessions_by_plate.get(plate)
        if ticket is None:
            raise ParkingGarageError(f"Vehicle {plate} not found")

        if exit_time is None:
            exit_time = datetime.now()

        fee = FeeCalculator.calculate_by_rates(ticket.entry_time, exit_time, self.pricing)
        ticket.exit_time = exit_time
        ticket.fee = fee
        ticket.spot.occupied = False

        del self._sessions_by_plate[plate]
        del self._sessions_by_ticket[ticket.ticket_id]
        return fee


class GarageCLI:
    def __init__(self) -> None:
        self.garage: Optional[ParkingGarage] = None

    def run(self) -> None:
        while True:
            command = input("> ").strip()
            if not command:
                continue
            if command.upper() == "EXIT":
                break
            try:
                self._handle_command(command)
            except Exception as exc:
                print(f"Error: {exc}")

    def _handle_command(self, command: str) -> None:
        parts = command.split()
        if not parts:
            return

        action = parts[0].upper()

        if action == "CREATE_GARAGE":
            if len(parts) < 3:
                raise ParkingGarageError("Usage: CREATE_GARAGE <floors> <spaces_per_floor> [compact_per_floor] [ev_per_floor]")
            self.garage = ParkingGarage(
                floor_count=int(parts[1]),
                spaces_per_floor=int(parts[2]),
                compact_per_floor=int(parts[3]) if len(parts) > 3 else 0,
                ev_per_floor=int(parts[4]) if len(parts) > 4 else 0,
            )
            print("Garage initialized successfully.")
            return

        if self.garage is None:
            raise ParkingGarageError("Garage not initialized")

        if action == "CHECK_IN":
            if len(parts) < 3:
                raise ParkingGarageError("Usage: CHECK_IN <plate> <vehicle_type>")
            ticket = self.garage.check_in(Vehicle(parts[1], parts[2]))
            print("Vehicle checked in successfully.")
            print(f"Ticket: {ticket.ticket_id}")
            print(f"Plate: {ticket.vehicle.license_plate}")
            print(f"Type: {ticket.vehicle.vehicle_type}")
            print(f"Floor: {ticket.spot.floor_number}")
            print(f"Spot: {ticket.spot.spot_id}")
            print(f"Entry Time: {ticket.entry_time.strftime('%Y-%m-%d %H:%M')}")
            return

        if action == "CHECK_OUT":
            if len(parts) < 2:
                raise ParkingGarageError("Usage: CHECK_OUT <plate>")
            fee = self.garage.check_out(parts[1])
            print(f"Vehicle: {parts[1]}")
            print(f"Parking Fee: ₹{fee}")
            print("Spot released successfully.")
            return

        if action == "FIND_VEHICLE":
            if len(parts) < 2:
                raise ParkingGarageError("Usage: FIND_VEHICLE <plate>")
            ticket = self.garage.find_vehicle(parts[1])
            if ticket is None:
                print("Vehicle not found")
                return
            print(f"Plate: {ticket.vehicle.license_plate}")
            print(f"Type: {ticket.vehicle.vehicle_type}")
            print(f"Ticket: {ticket.ticket_id}")
            print(f"Floor: {ticket.spot.floor_number}")
            print(f"Spot: {ticket.spot.label}")
            print(f"Entry Time: {ticket.entry_time.strftime('%Y-%m-%d %H:%M')}")
            return

        if action == "AVAILABLE":
            if len(parts) < 2:
                raise ParkingGarageError("Usage: AVAILABLE <compact|standard|ev>")
            print(self.garage.available_spots(parts[1]))
            return

        if action == "SHOW_OCCUPIED":
            occupied = self.garage.get_occupied_spots()
            if not occupied:
                print("No occupied spots.")
                return
            for spot in occupied:
                for ticket in self.garage.active_sessions:
                    if ticket.spot.spot_id == spot.spot_id:
                        print(f"{spot.spot_id} -> {ticket.vehicle.license_plate}")
            return

        raise ParkingGarageError(f"Unknown command: {action}")


Car = Vehicle
ParkingRecord = ParkingTicket

__all__ = [
    "Vehicle",
    "Car",
    "ParkingSpot",
    "ParkingTicket",
    "ParkingRecord",
    "FeeCalculator",
    "ParkingGarage",
    "GarageCLI",
]


if __name__ == "__main__":
    GarageCLI().run()
