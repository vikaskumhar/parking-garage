# Parking Garage Management System

A configurable multi-floor parking garage system for checking vehicles in and out, assigning compatible spaces, calculating fees, and preventing duplicate parking.

## Features

- Configurable floors, spaces per floor, compact spaces, and EV spaces
- Vehicle types: `compact`, `standard`, and `ev`
- EV vehicles can use EV spaces only
- Compact vehicles prefer compact spaces and can use standard spaces when needed
- Standard vehicles use standard spaces only
- Duplicate active parking prevention by license plate
- Ticket lookup and vehicle lookup
- Occupancy and available-space lookup
- Hourly pricing with a configurable daily cap
- Interactive command-line interface
- Polished responsive browser dashboard with setup, check-in, check-out, availability, and activity log

## Project Files

| File | Purpose |
| --- | --- |
| [parking_garage.py](parking_garage.py) | Python domain model, fee calculator, and CLI |
| [tests/test_parking_garage.py](tests/test_parking_garage.py) | Business-rule regression tests |
| [index.html](index.html) | Browser demo structure |
| [style.css](style.css) | Browser demo styling |
| [script.js](script.js) | Browser demo behavior |
| [reasoning.md](reasoning.md) | Core logic and processing pipeline |
| [ai-log.md](ai-log.md) | Prompts and implementation requests used for the project |

## Run Tests

From the project directory:

```bash
pytest -q
```

Expected result:

```text
7 passed
```

## Run the Python CLI

```bash
python parking_garage.py
```

The CLI supports commands such as:

```text
CREATE_GARAGE 2 10 2 2
CHECK_IN RJ14AB1234 standard
FIND_VEHICLE RJ14AB1234
AVAILABLE standard
SHOW_OCCUPIED
CHECK_OUT RJ14AB1234
EXIT
```

The `CREATE_GARAGE` arguments are floors, spaces per floor, compact spaces per floor, and EV spaces per floor.

## Run the Browser Demo

```bash
python -m http.server 8000
```

Then open [http://localhost:8000](http://localhost:8000) in a browser. If port `8000` is already in use, start the server on another port, for example `python -m http.server 8080`.

## Pricing Rules

The default Python rates are:

- First hour: `50`
- Every additional started hour: `30`
- Daily cap: `300`

Partial hours round up. Each rolling 24-hour billing window is capped independently. Checkout releases the assigned spot and removes the active ticket from the lookup indexes.

## Verification

The test suite covers first-hour and partial-hour billing, daily caps, check-in and checkout, EV restrictions, duplicate parking prevention, availability lookup, full garages, invalid vehicle types, ticket lookup, and spot release.