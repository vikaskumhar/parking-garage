# AI Development Log

## Prompt 1

I want to build a parking garage management system. Imagine a busy city parking garage where cars are constantly coming and going. I want the system to help the attendant manage everything without manually tracking cars and parking spaces.

## Prompt 2

Now I asked you to start with the basic backend structure. Create the main classes we will need for the parking garage and keep the design clean so we can expand it later.

## Prompt 3

I want you to create a Vehicle class now. It should store the license plate and vehicle type. For vehicle types, let's support compact, standard, and EV.

## Prompt 4

Please add validation to the vehicle. The license plate shouldn't be empty, and if someone enters lowercase letters or extra spaces, normalize the plate automatically.

## Prompt 5

Now add a ParkingSpot class. I want every parking spot to know which floor it belongs to, its number, its type, and whether it is currently occupied.

## Prompt 6

I also need a parking ticket. Create a ticket object that connects a vehicle with its assigned parking spot and stores the vehicle's entry time.

## Prompt 7

Now make the ticket capable of storing the exit time and final parking fee as well, because we will need that information during checkout.

## Prompt 8

Can you create the main ParkingGarage class now? I don't want the garage hardcoded for one example. It should work with different numbers of floors and parking spaces.

## Prompt 9

Please make the garage automatically create all of its parking spots when it is initialized.

## Prompt 10

Now I want each floor to support different parking spot types. We need compact, standard, and EV spots.

## Prompt 11

Can you give every parking spot a useful ID? Something that tells me the floor and spot type would be helpful when the attendant needs to locate a car.

## Prompt 12

Now add the logic for finding a free parking spot. The system should look at the vehicle type and find an appropriate available spot.

## Prompt 13

I specifically want EV vehicles to use only EV spots. Don't allow an EV to take a normal parking space.

## Prompt 14

For compact vehicles, try a compact spot first. But if there isn't one available, let the compact vehicle use a standard spot.

## Prompt 15

Standard vehicles should only be assigned standard spots. Please make sure that rule is enforced.

## Prompt 16

Now implement the check-in process. When a vehicle arrives, find a suitable free spot, mark it occupied, create a ticket, and store the vehicle as active.

## Prompt 17

Please make sure the same license plate cannot be checked in twice while the vehicle is already inside the garage. I don't want duplicate active vehicles.

## Prompt 18

What should happen if there is no suitable parking space? Add proper error handling and give the attendant a useful message.

## Prompt 19

Now I want a way to find a currently parked vehicle using its license plate. The attendant shouldn't have to search manually.

## Prompt 20

Please add ticket lookup as well. If I have a ticket ID, I should be able to find the active ticket.

## Prompt 21

Now add a function that tells me which parking spots are currently occupied.

## Prompt 22

I also want to know how many spots are available. Make it possible to ask for compact, standard, or EV availability separately.

## Prompt 23

Can you add a simple helper for checking whether an EV charging spot is currently free? This is something the attendant will probably ask frequently.

## Prompt 24

The parking allocation is looking good. Now I want to work on the most important part: calculating the parking fee correctly.

## Prompt 25

Make the first started hour use the first-hour price. Even if someone stays for only 20 or 30 minutes, charge the first-hour rate.

## Prompt 26

Now add the additional-hour rate. Every started hour after the first should use the additional-hour price.

## Prompt 27

Please make sure partial hours are rounded up. For example, 1 hour and 10 minutes should count as 2 hours.

## Prompt 28

Now add a daily maximum charge. If the calculated fee becomes higher than the daily cap, use the daily cap instead.

## Prompt 29

I want the fee calculation separated from the garage logic. Create a FeeCalculator so the pricing rules are easier to test and maintain.

## Prompt 30

Please test the fee calculator with different parking durations. Include less than one hour, exactly one hour, more than one hour, and long parking sessions.

## Prompt 31

There's another important case: a car can enter one day and leave the next day. Make sure the daily cap logic handles day boundaries correctly.

## Prompt 32

Please make checkout reject an exit time that is earlier than the entry time. That should never be considered a valid parking session.

## Prompt 33

Now implement the actual checkout flow. Find the vehicle, calculate the fee, store the checkout details, release the parking spot, and remove the vehicle from active vehicles.

## Prompt 34

Please make sure that after checkout the parking spot immediately becomes available for another vehicle.

## Prompt 35

What happens if the attendant tries to check out a car that isn't currently parked? Add a clear error for that situation.

## Prompt 36

Now I want a simple command-line interface so I can test the parking garage without using the website.

## Prompt 37

Add a command for creating a garage from the CLI. I should be able to specify the number of floors and spaces per floor, including compact and EV spaces.

## Prompt 38

Now add a CHECK_IN command. It should accept a license plate and vehicle type and show the ticket and parking spot after successful check-in.

## Prompt 39

Please add a CHECK_OUT command as well. I want to enter a license plate and see the calculated parking fee.

## Prompt 40

Add a FIND_VEHICLE command so the attendant can quickly locate a parked car using its plate number.

## Prompt 41

Now add an AVAILABLE command. I want to be able to ask how many compact, standard, or EV spaces are free.

## Prompt 42

Please add a SHOW_OCCUPIED command that tells me which spots are occupied and which vehicle is using each spot.

## Prompt 43

Now I asked you to create automated tests for the important parking rules. Don't just test the happy path.

## Prompt 44

Add tests for the fee calculation. I want to verify first-hour billing, partial-hour rounding, additional hours, and the daily cap.

## Prompt 45

Please add tests for EV allocation, compact fallback to standard, standard vehicles, and a completely full garage.

## Prompt 46

Now test duplicate check-ins. The same vehicle should never be allowed to occupy two spots.

## Prompt 47

Also test vehicle lookup, ticket lookup, checkout, and spot release. I want to make sure the garage state stays consistent.

## Prompt 48

The backend is working now. I asked you to build a proper web interface for the attendant. Make it feel like a real professional parking operations dashboard instead of a basic college project.

## Prompt 49

Now improve the website design. I want a clean Apple-inspired look with modern typography, rounded cards, subtle animations, clear spacing, responsive desktop/mobile layouts, live capacity information, and professional check-in and checkout forms.

## Prompt 50

Finally, I want you to review the whole parking garage project from the perspective of an actual attendant using it during a busy day. Check the parking logic, fee calculation, spot allocation, duplicate vehicle handling, lookup functions, checkout flow, error messages, activity log, and UI. Fix anything that could cause incorrect charges or incorrect occupancy. Keep the system configurable so it works for different garages, not just the demo data.

The final result should feel like a small production-quality parking management system that is simple for an attendant to understand and reliable enough to use throughout the day.

## Prompt 51

Please add authentication to the website. I want the attendant to sign in before seeing the garage dashboard, stay signed in during the browser session, and have a sign-out button.

### Resulting direction

- Add a dedicated Parkline sign-in screen before the dashboard.
- Validate the demo operator credentials and show a useful error for invalid input.
- Persist the authenticated state in `sessionStorage` for the active browser tab.
- Show the signed-in operator in the header and provide logout.
- Document that static client-side authentication is only a demo boundary and must be replaced with server or identity-provider authentication for production.

## Prompt 52

The login is too limited. Add a proper signup flow too, remember created operators, let users switch between sign in and create account, and keep the session after refreshing the page.

### Resulting direction

- Add sign-in and create-account tabs to the auth screen.
- Validate names, unique operator IDs, password length, and password confirmation.
- Store demo accounts in `localStorage` and the active session in `sessionStorage`.
- Keep the security note visible because this is still a static frontend demo.

## Prompt 53

Extend the parking website so it feels like a high-level Apple-style product: colorful but calm, dynamic, responsive, and comfortable to swipe on a phone.

### Resulting direction

- Add live insight cards for occupancy, EV readiness, shift state, and operator guidance.
- Use a native CSS scroll-snap rail for touch-friendly horizontal swiping.
- Derive live metrics from garage state instead of hard-coding dashboard numbers.
- Preserve the quiet Apple-inspired structure while adding blue, green, orange, and violet accents.
- Keep the operational forms accessible and stack them cleanly on mobile.