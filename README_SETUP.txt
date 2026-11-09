HOTEL MANAGEMENT SYSTEM - UPGRADE

WHAT IS INCLUDED
1. Room availability check and server-side prevention of overbooking.
2. Customer booking history.
3. Customer booking cancellation.
4. Admin dashboard with total/confirmed/cancelled bookings and confirmed-booking revenue.
5. Customer registration and login (passwords are hashed).
6. Downloadable PDF booking receipt.

IMPORTANT DATABASE NOTES
- Back up your existing hotel_management database first.
- Open database_upgrade.sql in MySQL Workbench and execute it ONCE.
- It preserves the existing bookings table and its rows.
- Existing old bookings remain visible to admin, but are not linked to customer accounts.
- The sample inventory is 10 rooms per room type. Change total_rooms in room_types to your actual inventory.
- Do not run the ALTER TABLE section a second time; it adds columns to your existing table.

SETUP ON WINDOWS / VS CODE
1. Extract this ZIP into your project folder (keep templates and static folders).
2. Copy .env.example and rename the copy to .env.
3. Open .env and set DB_PASSWORD to your current MySQL root password.
4. Change SECRET_KEY and ADMIN_PASSWORD to private values.
5. Open VS Code terminal in the project folder:
      python -m pip install -r requirements.txt
6. Execute database_upgrade.sql in MySQL Workbench.
7. Start the application:
      python app.py
8. Open:
      http://127.0.0.1:5000

ADMIN LOGIN
Set ADMIN_USERNAME and ADMIN_PASSWORD in .env. Defaults are admin / admin123
only if you do not change them. Change the default before sharing the app.

BOOKING FLOW
- Customers must register/login before booking.
- Availability display is informational; the booking endpoint rechecks capacity inside a database transaction.
- A confirmed booking occupies one room of its room type over [check-in, check-out).
- Cancelled bookings do not count toward availability or confirmed-booking revenue.

SECURITY / DEMO NOTES
- Do not publish your .env file or share database credentials.
- For a public deployment, use a production WSGI server, HTTPS, a strong SECRET_KEY,
  secure session-cookie settings, and a properly permissioned database account.
- This is a student-project starter, not a payment-processing system.
