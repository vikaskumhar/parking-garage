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
- Client-side operator sign-in gate with session persistence and logout

## Project Files

| File | Purpose |
| --- | --- |
| [parking_garage.py](parking_garage.py) | Python domain model, fee calculator, and CLI |
| [parking_server.py](parking_server.py) | Standard-library HTTP API for automation and lifecycle actions |
| [app.py](app.py) | HTTP API entry point |
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

## Run the Automation API

```bash
python app.py
```

The API listens on `http://127.0.0.1:8001` by default. The automation endpoint closes every active session parked for at least 24 hours and bills it at the supplied clock time:

```bash
curl -X POST http://127.0.0.1:8001/clock \
	-H 'Content-Type: application/json' \
	-d '{"now":"2024-01-02T09:00:00"}'
```

Additional lifecycle endpoints are available for the same service:

- `POST /check-in` accepts `{"license_plate":"EV-1","vehicle_type":"ev","entry_time":"2024-01-01T09:00:00"}`.
- `POST /check-out` accepts `{"license_plate":"EV-1","exit_time":"2024-01-01T11:00:00"}`.
- `POST /rate-card` imports a messy per-type rate card and returns cleaned rates.
- `POST /transfer` accepts `{"from_plate":"OLD-1","to_plate":"NEW-1"}` and preserves the open ticket's spot and entry time.

Rate-card values may contain currency symbols and words such as `"INR 50 / hour"`; the importer extracts the numeric value and normalizes aliases such as `first hour`, `extra hour`, and `daily cap`.

## Run the Browser Demo

```bash
python -m http.server 8000
```

Then open [http://localhost:8000](http://localhost:8000) in a browser. If port `8000` is already in use, start the server on another port, for example `python -m http.server 8080`.

The browser demo sign-in uses:

- Operator ID: `attendant`
- Password: `parkline2026`

Use **Create account** on the sign-in screen to register another local demo operator. The account is remembered in that browser using `localStorage`, while the active sign-in is remembered for the current tab using `sessionStorage`.

This authentication is intentionally client-side because the project is served as static files. It protects the demo workflow and demonstrates the user experience, but it is not a production security boundary. Production authentication should move credential verification and session management to a backend or identity provider.

The dashboard also includes swipeable insight cards for occupancy, EV readiness, shift status, and operator tips. On mobile, the cards and operational sections use native horizontal scrolling and responsive stacking so the main actions remain comfortable to use.

## Pricing Rules

The default Python rates are:

- First hour: `50`
- Every additional started hour: `30`
- Daily cap: `300`

Partial hours round up. Each rolling 24-hour billing window is capped independently. Checkout releases the assigned spot and removes the active ticket from the lookup indexes.

## Verification

The test suite covers first-hour and partial-hour billing, daily caps, check-in and checkout, EV restrictions, duplicate parking prevention, availability lookup, full garages, invalid vehicle types, ticket lookup, and spot release.