# Core Logic and Processing Pipeline

## Goal

The system must ensure that every active vehicle has one valid location, no spot is assigned to two vehicles, EV rules are enforced, and checkout produces a deterministic fee.

## Domain Objects

### Vehicle

`Vehicle` stores the license plate and vehicle type. Input is normalized by trimming the plate, converting it to uppercase, and converting the vehicle type to lowercase. Only `compact`, `standard`, and `ev` are accepted.

### ParkingSpot

`ParkingSpot` stores its floor, number, type, identifier, and occupancy state. The `occupied` flag is changed only when a ticket is successfully created or checked out.

### ParkingTicket

`ParkingTicket` connects a vehicle to a spot and entry time. It also stores checkout time and the final fee after checkout.

## Garage Initialization

1. Validate that the number of floors and spaces per floor is positive.
2. Build every spot for every floor.
3. Assign each spot a type based on the configured compact and EV counts.
4. Index spots by ID and by floor.
5. Create empty active-session indexes for plates and ticket IDs.

The garage is configurable because spot types and floor counts are constructor inputs rather than hard-coded business assumptions.

## Check-in Pipeline

1. Normalize or validate the incoming vehicle.
2. Check the plate index. An active plate cannot check in twice.
3. Select the first compatible unoccupied spot.
4. Enforce compatibility:
   - EV vehicles can use EV spots only.
   - Compact vehicles prefer compact spots and may use standard spots.
   - Standard vehicles use standard spots only.
5. Generate a unique ticket ID.
6. Mark the spot occupied.
7. Add the ticket to both the plate and ticket indexes.
8. Return the ticket containing the assigned floor and spot.

The occupancy flag and both indexes are updated together so lookup and availability remain consistent.

## Fee Calculation Pipeline

1. Reject an exit time earlier than the entry time.
2. Divide the stay into rolling 24-hour windows starting at entry.
3. For each window, round partial hours up.
4. Charge the first-hour rate for the first started hour.
5. Charge the additional-hour rate for each later started hour.
6. Apply the daily cap to that 24-hour window.
7. Add all window totals.

For example, a 2 hour 15 minute stay with rates of 50 for the first hour and 30 for each additional hour costs 110 because it uses three started hours.

## Checkout Pipeline

1. Normalize the requested plate.
2. Find the active ticket by plate.
3. Calculate the fee using the stored entry time and supplied exit time.
4. Store the exit time and fee on the ticket.
5. Mark the ticket's spot as available.
6. Remove the ticket from both active indexes.
7. Return the fee.

After checkout, the vehicle can check in again and the released spot can be assigned to another compatible vehicle.

## Lookup and Availability

- Plate lookup uses `_sessions_by_plate`.
- Ticket lookup uses `_sessions_by_ticket`.
- Spot availability scans indexed spots and counts unoccupied spots, optionally filtered by type.
- Occupied spot reporting compares active tickets with their assigned spots.

These structures make the invariants visible and keep the main operations straightforward.

## Browser Pipeline

The browser demo mirrors the core workflow in JavaScript:

1. Configure spot counts and pricing.
2. Create a `Car` and check it into the in-memory `ParkingGarage`.
3. Resolve a compatible spot type and update occupancy.
4. Render availability, active cars, and the activity log.
5. Check out by plate, calculate the fee, release occupancy, and render again.

The browser implementation is intentionally standalone and does not call the Python module. For production use, the Python domain logic would sit behind an API and the browser would call that API instead of maintaining local state.

## Frontend Experience Pipeline

The browser interface is designed as an operations product rather than a collection of generic forms:

1. Establish a quiet visual hierarchy with a clear garage identity, live system state, and a single primary hero message.
2. Put capacity at the top of the working area so an attendant can understand the garage before acting.
3. Group setup and vehicle movement into separate panels with numbered steps and obvious action buttons.
4. Keep current vehicles and activity history in a live view beneath the actions.
5. Use restrained neutrals for structure, blue for primary actions, orange for departures, and green for healthy capacity signals.
6. Use short reveal, hover, focus, and status transitions to make changes legible without slowing down repeated work.
7. Collapse the two-column layout into a single mobile workflow while preserving the same control order.

The visual direction takes cues from Apple's product pages: generous whitespace, precise typography, soft surfaces, quiet borders, and small moments of motion. It is adapted for a busy garage operator, so the interface remains information-dense and task-focused rather than becoming a marketing page.

The browser demo also normalizes license plates and rejects invalid checkout times before mutating occupancy. This keeps the client-side demonstration aligned with the Python system's core invariants.

## Authentication Pipeline

The static browser demo has a lightweight operator authentication layer:

1. Load the sign-in screen before exposing the garage dashboard.
2. Seed the local demo account if it does not exist.
3. Let an operator switch between sign-in and account creation without leaving the page.
4. Validate new account fields, prevent duplicate operator IDs, and store demo accounts in `localStorage`.
5. Find the matching account during sign-in and store only an authenticated flag and display name in `sessionStorage`.
6. Reveal the dashboard and show the active operator in the top bar.
7. Clear the session and return to the sign-in screen when the operator signs out.

This is a frontend experience layer, not secure production authentication. Since static HTML and JavaScript cannot safely keep a secret, a real deployment must verify credentials on a server or through an identity provider, issue a secure session cookie, and enforce authorization on every backend operation.

## Twists Pipeline

### Messy rate-card import

`RateCardImporter` accepts a mapping for compact, standard, and EV spots. It normalizes case and punctuation in field names, accepts aliases such as `first hour`, `extra hour`, and `maximum`, and extracts the first numeric value from currency-heavy strings. The cleaned card is stored per spot type, so checkout selects pricing from the actual assigned spot rather than applying one global price.

### Nightly clock automation

`ParkingGarage.auto_close_overdue(now)` scans active sessions and selects sessions aged at least 24 hours. It calls the same checkout path used by the attendant, which calculates the fee, marks the spot free, removes both active indexes, and records the closed ticket. `POST /clock` supplies the automation timestamp and returns each auto-closed ticket and fee.

### Valet plate transfer

`transfer_session(old_plate, new_plate)` changes only the active plate index and the ticket's vehicle plate. The ticket ID, assigned spot, vehicle type, and entry timestamp remain unchanged. It rejects missing sessions and a destination plate that is already active, so a valet hand-off cannot create duplicate occupancy.

The standard-library API in `parking_server.py` exposes `/clock`, `/rate-card`, and `/transfer` without adding a framework dependency. `app.py` is the executable entry point for local automation testing.

## Live Insight and Responsive Pipeline

The dashboard derives occupancy percentage, open EV bays, and current shift time from the same in-memory garage state used by the forms. These values are re-rendered whenever configuration, check-in, or checkout changes. The insight cards are laid out as a horizontal scroll-snap rail, which gives touch users a natural swipe interaction while desktop users see the complete row. CSS media queries stack the operational panels, reduce navigation density, and preserve large touch targets on smaller screens.

## Verification Strategy

The tests focus on business invariants rather than only happy-path output:

- Fee rounding and daily caps
- Correct spot type selection
- EV-only assignment
- Duplicate active plates
- Full-garage behavior
- Invalid vehicle types
- Ticket and plate lookup
- Spot release after checkout