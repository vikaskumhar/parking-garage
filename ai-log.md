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

## Validation Record

The Python regression suite currently validates the core business rules with seven passing tests. Documentation changes should be checked with `git diff --check`, followed by another `pytest -q` run before publishing changes.