USE hotel_management;

-- 1. Customer accounts. Existing booking rows are preserved.
CREATE TABLE IF NOT EXISTS customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Room-type inventory. Change total_rooms to match your project's room count.
CREATE TABLE IF NOT EXISTS room_types (
    room_type VARCHAR(50) PRIMARY KEY,
    total_rooms INT NOT NULL,
    price_per_night DECIMAL(10,2) NOT NULL
);

INSERT INTO room_types (room_type, total_rooms, price_per_night) VALUES
('Single Room', 10, 1500),
('Double Room', 10, 2500),
('Deluxe Room', 10, 3500),
('Suite Room', 10, 5000)
ON DUPLICATE KEY UPDATE
    price_per_night = VALUES(price_per_night);

-- 3. Add customer ownership and status to the existing bookings table.
-- Run this ALTER TABLE statement only once.
ALTER TABLE bookings
    ADD COLUMN customer_id INT NULL,
    ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'confirmed';

ALTER TABLE bookings
    ADD CONSTRAINT fk_bookings_customer
    FOREIGN KEY (customer_id) REFERENCES customers(id)
    ON DELETE SET NULL;

-- Check the upgraded tables and preserved bookings.
SELECT * FROM room_types;
SELECT * FROM customers;
SELECT * FROM bookings;
