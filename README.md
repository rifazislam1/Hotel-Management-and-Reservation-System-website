# 🏨 Hotel Management and Reservation System

A web-based **Hotel Management and Reservation System** developed as a B.Tech Computer Science and Engineering mini project. The application allows customers to explore hotel rooms, check booking costs, and submit room reservations. It also provides an admin panel to manage customer reservations.

## 📌 Project Overview

The main purpose of this project is to simplify the hotel reservation process using web technologies and database management.

The system provides a user-friendly interface where customers can enter their personal details, select room types, choose check-in and check-out dates, and confirm their reservations.

## ✨ Features

### Customer Module
- Attractive and responsive hotel website.
- View available room categories and prices.
- Customer reservation form.
- Automatic calculation of total booking cost.
- Check-in and check-out date validation.
- Booking confirmation with booking ID.

### Admin Module
- Secure admin login page.
- Admin dashboard to view customer reservations.
- Display customer and booking information.
- Delete existing reservations.
- View total number of bookings.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| HTML5 | Website structure |
| CSS3 | Website styling and layout |
| JavaScript | Form validation and price calculation |
| Python | Backend development |
| Flask | Python web framework |
| MySQL | Database management |

## 🗂️ Project Structure

```text
Hotel-Management-System/
│
├── app.py
│
├── templates/
│   ├── index.html
│   ├── admin_login.html
│   └── admin.html
│
├── static/
│   ├── style.css
│   └── script.js
│
├── README.md
└── requirements.txt
```

## 🏨 Room Categories and Pricing

| Room Type | Price per Night |
|---|---:|
| Single Room | ₹1,500 |
| Double Room | ₹2,500 |
| Deluxe Room | ₹3,500 |
| Suite Room | ₹5,000 |

**Price Calculation:**

Total Price = Number of Nights × Room Price per Night

## 🗄️ Database

Database Name: `hotel_management`

Main Table: `bookings`

The bookings table stores:

- Booking ID
- Customer Name
- Email Address
- Phone Number
- Room Type
- Check-in Date
- Check-out Date
- Number of Guests
- Number of Nights
- Total Price
- Special Requests
- Booking Date

## ⚙️ Installation and Setup

Follow these steps to run the project on your computer.

### Step 1: Install Required Software

Install the following:
- Python
- MySQL Server
- MySQL Workbench
- Visual Studio Code

### Step 2: Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

Navigate to the project directory:

```bash
cd Hotel-Management-System
```

### Step 3: Install Python Dependencies

```bash
pip install flask mysql-connector-python
```

### Step 4: Configure MySQL Database

Open MySQL Workbench and execute:

```sql
CREATE DATABASE hotel_management;

USE hotel_management;
```

Create the bookings table using the SQL commands provided with the project.

### Step 5: Configure Database Connection

Update the MySQL connection details in `app.py` according to your local MySQL configuration.

**Important:** Keep your database password private. Do not upload real credentials to GitHub.

### Step 6: Run the Application

Open the terminal in the project folder and execute:

```bash
python app.py
```

### Step 7: Open the Website

Open your browser and visit:

```text
http://127.0.0.1:5000/
```

The hotel website should now be running locally.

## 🔐 Admin Panel

To access the admin dashboard:

1. Open the hotel website.
2. Scroll down to the Contact section.
3. Click on Admin Login.
4. Enter the admin credentials configured in `app.py`.
5. Access the reservation dashboard.

Change any default admin credentials before deployment.

## 🚀 FEATURES

:

- Room availability checking and double-booking prevention.
- Customer registration and login.
- Customer booking history.
- Booking cancellation.
- Admin dashboard with revenue statistics.
- Downloadable booking receipts.
- Online payment integration.
- Email booking confirmation.

## 🎯 Project Objective

This project demonstrates the practical implementation of frontend development, backend programming, database connectivity, and CRUD operations using modern web technologies.

## 👨‍💻 Developed By

**Name:** Rifaz Islam  
**Department:** Computer Science and Engineering  
**Course:** B.Tech CSE  
**Project:** Hotel Management and Reservation System

## 📄 License

This project is developed for educational and academic purposes as a college mini project.

---

⭐ If you find this project interesting, feel free to explore the source code and suggest improvements.
