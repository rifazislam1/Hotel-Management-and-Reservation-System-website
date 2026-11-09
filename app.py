import os
from io import BytesIO
from datetime import date
from functools import wraps

import mysql.connector
from dotenv import load_dotenv
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, jsonify, flash, make_response, abort
)
from werkzeug.security import generate_password_hash, check_password_hash
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "9e0728a03112b9b161692a5157a5f6bfd7be2d909883d1537dd70bdc423773c6")

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "Rifaz@123"),
    "database": os.getenv("DB_NAME", "hotel_management"),
}

ROOM_PRICES = {
    "Single Room": 1500,
    "Double Room": 2500,
    "Deluxe Room": 3500,
    "Suite Room": 5000,
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def customer_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not session.get("customer_id"):
            if request.is_json:
                return jsonify({"success": False, "message": "Please log in first."}), 401
            return redirect(url_for("login", next=request.path))
        return function(*args, **kwargs)
    return wrapper

def admin_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))
        return function(*args, **kwargs)
    return wrapper

@app.context_processor
def inject_user():
    user = None
    if session.get("customer_id"):
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT id, full_name, email, phone FROM customers WHERE id=%s",
            (session["customer_id"],)
        )
        user = cur.fetchone()
        cur.close()
        conn.close()
    return {"current_user": user, "admin_logged_in": session.get("admin_logged_in", False)}

@app.route("/")
def home():
    return render_template("index.html", room_prices=ROOM_PRICES)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        if not name or not email or not phone or len(password) < 8:
            flash("Complete all fields. Password must contain at least 8 characters.", "error")
            return render_template("register.html")
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                """INSERT INTO customers (full_name, email, phone, password_hash)
                   VALUES (%s, %s, %s, %s)""",
                (name, email, phone, generate_password_hash(password))
            )
            conn.commit()
            customer_id = cur.lastrowid
            session.clear()
            session["customer_id"] = customer_id
            flash("Account created. You are now logged in.", "success")
            return redirect(url_for("home"))
        except mysql.connector.IntegrityError:
            conn.rollback()
            flash("An account with this email already exists.", "error")
        finally:
            cur.close()
            conn.close()
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM customers WHERE email=%s", (email,))
        customer = cur.fetchone()
        cur.close()
        conn.close()
        if customer and check_password_hash(customer["password_hash"], password):
            session.clear()
            session["customer_id"] = customer["id"]
            return redirect(url_for("home"))
        flash("Invalid email or password.", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/availability")
def availability():
    room_type = request.args.get("room_type", "")
    check_in = request.args.get("check_in", "")
    check_out = request.args.get("check_out", "")
    if room_type not in ROOM_PRICES:
        return jsonify({"available": False, "message": "Choose a valid room type."}), 400
    try:
        start = date.fromisoformat(check_in)
        end = date.fromisoformat(check_out)
        if start < date.today() or end <= start:
            raise ValueError
    except ValueError:
        return jsonify({"available": False, "message": "Enter valid future check-in and check-out dates."}), 400

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT total_rooms FROM room_types WHERE room_type=%s", (room_type,))
    inventory = cur.fetchone()
    cur.execute(
        """SELECT COUNT(*) AS booked FROM bookings
           WHERE room_type=%s AND status='confirmed'
           AND check_in < %s AND check_out > %s""",
        (room_type, end, start)
    )
    booked = cur.fetchone()["booked"]
    cur.close()
    conn.close()
    if not inventory:
        return jsonify({"available": False, "message": "Room inventory is not configured."}), 500
    available_count = max(0, inventory["total_rooms"] - booked)
    return jsonify({
        "available": available_count > 0,
        "available_count": available_count,
        "message": f"{available_count} {room_type}(s) available for these dates."
                   if available_count else "Sorry, this room type is fully booked for these dates."
    })

@app.route("/book", methods=["POST"])
@customer_required
def book():
    data = request.get_json(silent=True) or {}
    room = data.get("room_type", "")
    check_in = data.get("check_in", "")
    check_out = data.get("check_out", "")
    special_requests = str(data.get("special_requests", "")).strip()
    try:
        guests = int(data.get("guests", 0))
        start = date.fromisoformat(check_in)
        end = date.fromisoformat(check_out)
        if room not in ROOM_PRICES or not 1 <= guests <= 10:
            raise ValueError
        if start < date.today() or end <= start or len(special_requests) > 2000:
            raise ValueError
        nights = (end - start).days
        total_price = nights * ROOM_PRICES[room]
    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "Please enter valid reservation details."}), 400

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    try:
        conn.start_transaction()
        # Lock this room-type inventory row so simultaneous requests cannot overbook it.
        cur.execute("SELECT total_rooms FROM room_types WHERE room_type=%s FOR UPDATE", (room,))
        inventory = cur.fetchone()
        if not inventory:
            conn.rollback()
            return jsonify({"success": False, "message": "Room inventory is not configured."}), 500
        cur.execute(
            """SELECT COUNT(*) AS booked FROM bookings
               WHERE room_type=%s AND status='confirmed'
               AND check_in < %s AND check_out > %s""",
            (room, end, start)
        )
        booked = cur.fetchone()["booked"]
        if booked >= inventory["total_rooms"]:
            conn.rollback()
            return jsonify({
                "success": False,
                "message": "Sorry, this room type is fully booked for those dates. Please choose other dates."
            }), 409

        cur.execute(
            """SELECT full_name, email, phone FROM customers WHERE id=%s""",
            (session["customer_id"],)
        )
        customer = cur.fetchone()
        cur.execute(
            """INSERT INTO bookings
               (customer_id, customer_name, email, phone, room_type, check_in,
                check_out, guests, nights, total_price, special_requests, status)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'confirmed')""",
            (session["customer_id"], customer["full_name"], customer["email"],
             customer["phone"], room, start, end, guests, nights,
             total_price, special_requests)
        )
        booking_id = cur.lastrowid
        conn.commit()
        return jsonify({
            "success": True,
            "message": "Your reservation was confirmed!",
            "booking_id": booking_id,
            "nights": nights,
            "total_price": float(total_price),
            "receipt_url": url_for("receipt", booking_id=booking_id)
        })
    except mysql.connector.Error:
        conn.rollback()
        app.logger.exception("Booking database error")
        return jsonify({"success": False, "message": "Database error. Please try again."}), 500
    finally:
        cur.close()
        conn.close()

@app.route("/my-bookings")
@customer_required
def my_bookings():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        "SELECT * FROM bookings WHERE customer_id=%s ORDER BY booking_date DESC",
        (session["customer_id"],)
    )
    bookings = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("booking_history.html", bookings=bookings)

@app.route("/booking/<int:booking_id>/cancel", methods=["POST"])
@customer_required
def cancel_booking(booking_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """UPDATE bookings SET status='cancelled'
           WHERE id=%s AND customer_id=%s AND status='confirmed'""",
        (booking_id, session["customer_id"])
    )
    changed = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    flash("Booking cancelled." if changed else "Booking could not be cancelled.", "success" if changed else "error")
    return redirect(url_for("my_bookings"))

@app.route("/booking/<int:booking_id>/receipt")
def receipt(booking_id):
    if not session.get("customer_id") and not session.get("admin_logged_in"):
        return redirect(url_for("login"))
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    if session.get("admin_logged_in"):
        cur.execute("SELECT * FROM bookings WHERE id=%s", (booking_id,))
    else:
        cur.execute(
            "SELECT * FROM bookings WHERE id=%s AND customer_id=%s",
            (booking_id, session["customer_id"])
        )
    booking = cur.fetchone()
    cur.close()
    conn.close()
    if not booking:
        abort(404)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=22*mm, leftMargin=22*mm)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("GRAND PALACE HOTEL", styles["Title"]),
        Paragraph("Booking Receipt", styles["Heading2"]),
        Spacer(1, 12),
    ]
    rows = [
        ["Booking ID", str(booking["id"])],
        ["Customer", booking["customer_name"]],
        ["Email", booking["email"]],
        ["Phone", booking["phone"]],
        ["Room type", booking["room_type"]],
        ["Check-in", str(booking["check_in"])],
        ["Check-out", str(booking["check_out"])],
        ["Guests", str(booking["guests"])],
        ["Nights", str(booking["nights"])],
        ["Total amount", f"INR {booking['total_price']}"],
        ["Booking status", booking["status"].title()],
        ["Booking date", str(booking["booking_date"])],
    ]
    table = Table(rows, colWidths=[48*mm, 105*mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#e8edf5")),
        ("TEXTCOLOR", (0,0), (-1,-1), colors.HexColor("#142d4e")),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("PADDING", (0,0), (-1,-1), 9),
        ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
    ]))
    story.append(table)
    story.append(Spacer(1, 18))
    story.append(Paragraph("Thank you for choosing Grand Palace Hotel.", styles["Normal"]))
    doc.build(story)
    pdf = buffer.getvalue()
    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"attachment; filename=booking_receipt_{booking_id}.pdf"
    return response

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session.clear()
            session["admin_logged_in"] = True
            return redirect(url_for("admin"))
        flash("Invalid admin username or password.", "error")
    return render_template("admin_login.html")

@app.route("/admin")
@admin_required
def admin():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT COUNT(*) AS total FROM bookings")
    total_bookings = cur.fetchone()["total"]
    cur.execute("SELECT COUNT(*) AS total FROM bookings WHERE status='confirmed'")
    confirmed_bookings = cur.fetchone()["total"]
    cur.execute("SELECT COUNT(*) AS total FROM bookings WHERE status='cancelled'")
    cancelled_bookings = cur.fetchone()["total"]
    cur.execute("SELECT COALESCE(SUM(total_price),0) AS revenue FROM bookings WHERE status='confirmed'")
    revenue = cur.fetchone()["revenue"]
    cur.execute("SELECT * FROM bookings ORDER BY id DESC")
    bookings = cur.fetchall()
    cur.close()
    conn.close()
    return render_template(
        "admin.html", bookings=bookings, total_bookings=total_bookings,
        confirmed_bookings=confirmed_bookings, cancelled_bookings=cancelled_bookings,
        revenue=revenue
    )

@app.route("/admin/cancel/<int:booking_id>", methods=["POST"])
@admin_required
def admin_cancel_booking(booking_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE bookings SET status='cancelled' WHERE id=%s AND status='confirmed'",
        (booking_id,)
    )
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("admin"))

@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "0") == "1")
