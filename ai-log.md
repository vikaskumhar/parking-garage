# AI Development Log

This file records the requests used to shape the parking garage project and the resulting implementation direction.

## Prompt 1: Define the Main Problem

> Build the attendant something so every car is charged correctly and no spot is double-parked.

### Resulting direction

- Model vehicles, spots, tickets, and the garage explicitly.
- Make occupancy state authoritative.
- Reject duplicate active vehicles.
- Calculate fees from entry and exit timestamps.

## Prompt 2: Make It Reusable

> Build it for any garage, not one.

### Resulting direction

- Make floor count and space counts configurable.
- Support compact, standard, and EV spot types.
- Avoid relying on one fixed garage layout.

## Prompt 3: Prioritize the Core Workflow

> Get check-in / check-out and the fee right first, then the spot types and lookups.

### Resulting direction

- Implement check-in and checkout before secondary reporting features.
- Add deterministic hourly billing and daily caps.
- Release spots during checkout.
- Add lookup maps for license plates and tickets.

## Prompt 4: Add a Usable Interface

> run this

> run in web

> run this project in website version

### Resulting direction

- Add an interactive Python CLI.
- Add a standalone HTML, CSS, and JavaScript browser demo.
- Provide local run commands using `pytest` and `python -m http.server`.

## Prompt 5: Expand to the Complete Specification

> Build a complete Parking Garage Management System for a busy multi-level city-centre parking garage. Include configurable garage design, vehicle check-in and check-out, correct fee calculation, EV restrictions, spot lookups, ticket lookup, availability, and a CLI.

### Resulting direction

- Use an object-oriented Python design.
- Add `Vehicle`, `ParkingSpot`, `ParkingTicket`, `FeeCalculator`, `ParkingGarage`, and `GarageCLI`.
- Test edge cases including partial hours, daily caps, duplicate plates, unavailable spots, invalid vehicle types, and spot release.

## Prompt 6: Document the Project

> In this parking garage problem add README.md, reasoning.md in which you write the core logic behind this project pipeline, and ai-log.md in which you write a prompt as it looks like I asked the prompt to AI. Also push it into GitHub.

### Resulting direction

- Make the README the entry point for setup, commands, features, and verification.
- Explain the domain and processing pipeline in `reasoning.md`.
- Preserve the request history and implementation decisions in this file.
- Push the completed documentation and source files to the configured GitHub remote after local validation.

## Prompt 7: Add Different Vehicle Types

> I need compact cars, normal cars, and electric cars to be treated differently. Please add vehicle type validation.

### Resulting direction

- Normalize vehicle types before processing.
- Reject unsupported types early with a clear error.
- Keep vehicle compatibility rules in the garage rather than in the CLI.

## Prompt 8: Reserve EV Spaces Correctly

> An EV should never take a regular spot. Make sure the system refuses the check-in if no EV spot is free.

### Resulting direction

- Restrict EV vehicles to EV spots only.
- Check EV availability before changing occupancy.
- Keep the operation atomic when no compatible spot exists.

## Prompt 9: Prevent Duplicate Parking

> What happens if the attendant enters the same number plate twice? I want a proper error and no extra occupied spot.

### Resulting direction

- Maintain an active-session index keyed by normalized license plate.
- Reject a duplicate before allocating a spot.
- Leave all occupancy and ticket state unchanged after rejection.

## Prompt 10: Make the Garage Multi-Level

> Please support multiple floors and show the floor number on the ticket when a car checks in.

### Resulting direction

- Build spots per floor during garage initialization.
- Include floor information in each parking spot and ticket.
- Use deterministic spot IDs that identify the floor and type.

## Prompt 11: Add Ticket Numbers

> Every checked-in car should receive a unique ticket number that I can use later to find the parking record.

### Resulting direction

- Generate sequential ticket IDs.
- Store active tickets in a ticket lookup map.
- Return ticket details from check-in and support ticket lookup.

## Prompt 12: Calculate Partial Hours

> Charge by started hours, so even 20 minutes should count as one hour and 1 hour 10 minutes should count as two.

### Resulting direction

- Convert duration to seconds.
- Round partial hours up with ceiling logic.
- Apply the first-hour and additional-hour rates consistently.

## Prompt 13: Add a Daily Maximum

> Add a maximum daily charge so a customer does not keep paying unlimited hourly fees.

### Resulting direction

- Add a configurable daily cap to pricing.
- Apply the cap to each rolling 24-hour billing window.
- Preserve the normal hourly calculation below the cap.

## Prompt 14: Reject Invalid Checkout Times

> If the checkout time is before the entry time, show an error instead of calculating a negative fee.

### Resulting direction

- Validate timestamp order inside the fee calculator.
- Raise the domain error before changing the ticket or spot.
- Keep the active session intact after invalid checkout input.

## Prompt 15: Release the Spot at Checkout

> Once a car leaves, its spot must become available immediately for the next car.

### Resulting direction

- Mark the assigned spot unoccupied after fee calculation succeeds.
- Remove the active plate and ticket indexes.
- Allow a later check-in to reuse the released spot.

## Prompt 16: Add Availability Queries

> Give the attendant a quick way to see how many compact, standard, and EV spaces are free.

### Resulting direction

- Add a type-filtered availability method.
- Count only unoccupied spots.
- Expose the query through the CLI and browser view.

## Prompt 17: Show Occupied Spaces

> Add a command that lists the occupied spots and the license plate parked in each one.

### Resulting direction

- Iterate over occupied spots.
- Match each occupied spot to its active ticket.
- Print a concise spot-to-plate report.

## Prompt 18: Use Better Data Structures

> The garage can be large, so do not search through every old parking record when finding an active car.

### Resulting direction

- Keep active tickets in dictionaries keyed by plate and ticket ID.
- Keep spot indexes by ID and floor.
- Remove completed sessions from active maps at checkout.

## Prompt 19: Separate Business Logic from the CLI

> The command-line interface should only handle input and output. Put the parking rules in reusable classes.

### Resulting direction

- Keep validation and allocation in `ParkingGarage`.
- Keep fee calculation in `FeeCalculator`.
- Let `GarageCLI` translate commands into domain method calls.

## Prompt 20: Add Regression Tests

> Write tests for the important parking rules before we call this finished.

### Resulting direction

- Add pytest coverage for pricing, check-in, checkout, EV rules, duplicates, lookups, and release behavior.
- Use fixed timestamps so fee tests are deterministic.
- Test both successful operations and expected errors.

## Prompt 21: Make Tests Import Reliably

> Pytest cannot find the parking module from the tests folder. Fix the project test setup.

### Resulting direction

- Add a minimal `pytest.ini` configuration for the project root.
- Run the suite from the repository directory.
- Keep the source layout simple instead of adding unnecessary packaging steps.

## Prompt 22: Build a Browser Version

> I want to demonstrate this in a website, with forms for setup, check-in, and checkout.

### Resulting direction

- Add an HTML interface with setup and transaction forms.
- Use JavaScript state to model the demo garage.
- Render availability, active cars, and a garage activity log.

## Prompt 23: Handle Browser Errors Clearly

> When a check-in fails in the web page, show the user what went wrong instead of failing silently.

### Resulting direction

- Wrap browser actions in error handling.
- Display status messages for successful and rejected operations.
- Keep the UI state unchanged when an operation fails.

## Prompt 24: Make the Browser Demo Easy to Run

> Tell me exactly how to open the website locally, and mention what to do if port 8000 is already busy.

### Resulting direction

- Document `python -m http.server 8000`.
- Provide the localhost URL.
- Explain how to use an alternate port such as 8080.

## Prompt 25: Review Before Publishing

> Before pushing this project, check the tests, whitespace, generated files, and Git status.

### Resulting direction

- Run `pytest -q`.
- Run `git diff --check`.
- Ignore Python caches and virtual environments.
- Inspect the staged file list before committing.

## Prompt 26: Publish the Finished Project

> Commit the complete parking garage project and push it to my GitHub repository on the main branch.

### Resulting direction

- Stage source code, tests, browser files, and documentation.
- Create a descriptive commit.
- Push to the configured `origin/main` remote.
- Confirm that the working tree and branch are synchronized afterward.

## Validation Record

The Python regression suite currently validates the core business rules with seven passing tests. Documentation changes should be checked with `git diff --check`, followed by another `pytest -q` run before publishing changes.