from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import qrcode
from PIL import Image
import random
import string
import os

app = Flask(__name__)

# Make sure these directories exist
os.makedirs('static', exist_ok=True)
os.makedirs('templates', exist_ok=True)

def init_db():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='parking_system'
        )
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS parking_users (
                user_id VARCHAR(20) PRIMARY KEY,
                name VARCHAR(50),
                vehicle_no VARCHAR(20),
                vehicle_type VARCHAR(20),
                preferred_exit_time TIME,
                slot_allocated VARCHAR(10),
                entry_time TIMESTAMP,
                exit_time TIMESTAMP NULL,
                total_charge DECIMAL(10,2) DEFAULT 0,
                status ENUM('parked', 'exited') DEFAULT 'parked',
                paid VARCHAR(20) DEFAULT 'no'
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS parking_slots (
                slot VARCHAR(10) PRIMARY KEY,
                vehicle_type VARCHAR(20),
                status ENUM('free', 'occupied') DEFAULT 'free'
            )
        ''')
        
        # Initialize some parking slots if they don't exist
        cursor.execute("SELECT COUNT(*) FROM parking_slots")
        if cursor.fetchone()[0] == 0:
            # Add two-wheeler slots
            for i in range(1, 51):
                cursor.execute(
                    "INSERT INTO parking_slots (slot, vehicle_type, status) VALUES (%s, %s, %s)",
                    (f"A{i}", "two_wheeler", "free")
                )
            # Add four-wheeler slots
            for i in range(1, 101):
                cursor.execute(
                    "INSERT INTO parking_slots (slot, vehicle_type, status) VALUES (%s, %s, %s)",
                    (f"B{i}", "four_wheeler", "free")
                )
        
        connection.commit()
        print("Database initialized successfully!")
    except Error as e:
        print(f"Error initializing database: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def generate_user_id(name, vehicle_no):
    name = name.strip().lower()
    vehicle_no = vehicle_no.strip().upper()

    name_part = name[:2] if len(name) >= 2 else name.ljust(2, 'x')
    vehicle_part = vehicle_no[-2:] if len(vehicle_no) >= 2 else vehicle_no.rjust(2, '0')
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))

    return (name_part + vehicle_part + random_part).upper()

def get_unique_user_id(cursor, name, vehicle_no):
    while True:
        user_id = generate_user_id(name, vehicle_no)
        cursor.execute("SELECT COUNT(*) FROM parking_users WHERE user_id = %s", (user_id,))
        if cursor.fetchone()[0] == 0:
            return user_id

def find_free_slot(cursor, vehicle_type):
    # Map the form value to the database value
    vehicle_type_mapping = {
        'two_wheeler': 'two_wheeler',
        'four_wheeler': 'four_wheeler'
    }
    
    db_vehicle_type = vehicle_type_mapping.get(vehicle_type, vehicle_type)
    
    cursor.execute('''
        SELECT slot FROM parking_slots
        WHERE vehicle_type = %s AND status = 'free'
        LIMIT 1
    ''', (db_vehicle_type,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        return None

@app.route('/')
def home():
    return render_template('register_vehicle.html')

@app.route('/register', methods=['POST'])
def register():
    # Get form data
    name = request.form['name']
    vehicle_no = request.form['vehicle_no']
    vehicle_type = request.form['vehicle_type']
    preferred_exit_time = request.form['preferred_exit_time']
   
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='parking_system'
        )
        cursor = connection.cursor()

        # Generate user_id
        user_id = get_unique_user_id(cursor, name, vehicle_no)
        
        entry_time = datetime.now()

        # Allocate slot
        slot_allocated = find_free_slot(cursor, vehicle_type)
        if not slot_allocated:
            # Handle case where no slots are available
            return "No available slots for your vehicle type. Please try again later."

        # Update slot status to occupied
        cursor.execute('''
            UPDATE parking_slots
            SET status = 'occupied'
            WHERE slot = %s
        ''', (slot_allocated,))

        # Insert registration details
        cursor.execute('''
            INSERT INTO parking_users 
            (user_id, name, vehicle_no, vehicle_type, preferred_exit_time, slot_allocated, entry_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (user_id, name, vehicle_no, vehicle_type, preferred_exit_time, slot_allocated, entry_time))

        connection.commit()
        
        # Pass data to the confirmation page
        return render_template('registration_success.html', 
                              user_id=user_id, 
                              slot_allocated=slot_allocated)

    except Error as e:
        return f"Database Error: {e}"
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

def generate_qr():
    url = "http://localhost:5000/"  # you can update this with your actual server address
    qr = qrcode.make(url)
    qr_path = "static/qr.png"
    qr.save(qr_path)
    return qr_path

@app.route('/qr')
def show_qr():
    qr_path = generate_qr()
    return render_template('qr.html', qr_path=qr_path)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0')