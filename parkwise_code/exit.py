from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from mysql.connector import Error
from datetime import datetime, time
import qrcode
from PIL import Image
import os

app = Flask(__name__)

def show_exit_qr():
    exit_url = "http://192.168.20.215:5002/exit"
    qr = qrcode.make(exit_url)
    
    if not os.path.exists('static'):
        os.makedirs('static')
    
    qr_path = "static/exit_qr.png"
    qr.save(qr_path)
    img = Image.open(qr_path)
    img.show()

@app.route('/exit', methods=['GET'])
def exit_page():
    return render_template('exit_vehicle.html')

@app.route('/process_exit', methods=['POST'])
def process_exit():
    if request.method == 'POST' and 'user_id' in request.form:
        user_id = request.form['user_id']
    else:
        return redirect(url_for('exit_page'))

    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='parking_system'
        )
        cursor = connection.cursor(dictionary=True)

        cursor.execute('''
            SELECT entry_time, vehicle_type, preferred_exit_time, slot_allocated 
            FROM parking_users 
            WHERE user_id = %s AND status = 'parked'
        ''', (user_id,))
        record = cursor.fetchone()

        if record:
            entry_time = record['entry_time']
            vehicle_type = record['vehicle_type']
            preferred_exit_time = record['preferred_exit_time']
            slot_allocated = record['slot_allocated']
            exit_time = datetime.now()

            # Calculate charges
            if vehicle_type == 'two_wheeler':
                base_rate = 10
                hourly_rate = 20
            else:
                base_rate = 30
                hourly_rate = 30

            duration_hours = (exit_time - entry_time).total_seconds() / 3600
            
            if duration_hours <= 1:
                total_charge = base_rate
            else:
                additional_hours = duration_hours - 1
                total_charge = base_rate + (additional_hours * hourly_rate)
            
            # Calculate penalty if exceeded preferred exit time
            if preferred_exit_time:
                if isinstance(preferred_exit_time, str):
                    preferred_time = datetime.strptime(preferred_exit_time, '%H:%M:%S').time()
                elif isinstance(preferred_exit_time, time):
                    preferred_time = preferred_exit_time
                else:
                    hours, remainder = divmod(preferred_exit_time.seconds, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    preferred_time = time(hour=hours, minute=minutes, second=seconds)
                
                preferred_datetime = datetime.combine(entry_time.date(), preferred_time)
                
                if exit_time > preferred_datetime:
                    extra_hours = (exit_time - preferred_datetime).total_seconds() / 3600
                    if extra_hours > 0:
                        extra_hours = int(extra_hours) + (1 if extra_hours % 1 > 0 else 0)
                        penalty_rate = 20 if vehicle_type == 'two_wheeler' else 30
                        penalty_charge = extra_hours * penalty_rate
                        total_charge += penalty_charge

            total_charge = round(total_charge, 2)

            return render_template('payment.html', 
                               user_id=user_id,
                               total_charge=total_charge,
                               slot_allocated=slot_allocated,
                               vehicle_type=vehicle_type.capitalize(),
                               entry_time=entry_time.strftime('%Y-%m-%d %H:%M:%S'),
                               exit_time=exit_time.strftime('%Y-%m-%d %H:%M:%S'),
                               duration=f"{duration_hours:.2f} hours")

        else:
            return "Invalid User ID or Already Exited."

    except Error as e:
        return f"Database Connection Error: {e}"
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/complete_exit', methods=['POST'])
def complete_exit():
    if request.method == 'POST' and 'user_id' in request.form and 'total_charge' in request.form:
        user_id = request.form['user_id']
        total_charge = request.form['total_charge']
    else:
        return redirect(url_for('exit_page'))

    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='parking_system'
        )
        cursor = connection.cursor(dictionary=True)

        exit_time = datetime.now()

        # Get the slot_allocated for this user
        cursor.execute('SELECT slot_allocated FROM parking_users WHERE user_id = %s', (user_id,))
        user_data = cursor.fetchone()
        slot_allocated = user_data['slot_allocated'] if user_data else None

        # Update user record
        cursor.execute('''
            UPDATE parking_users
            SET exit_time = %s,
                total_charge = %s,
                status = 'exited',
                paid = 'yes'
            WHERE user_id = %s
        ''', (exit_time, total_charge, user_id))

        # Update parking_slots table if slot exists
        if slot_allocated:
            cursor.execute('''
                UPDATE parking_slots
                SET status = 'free'
                WHERE slot = %s
            ''', (slot_allocated,))

        connection.commit()

        return render_template('complete.html', 
                           user_id=user_id,
                           slot_freed=slot_allocated,
                           total_charge=total_charge)

    except Error as e:
        return f"Database Update Error: {e}"
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == '__main__':
    show_exit_qr()
    app.run(debug=True, host='0.0.0.0', port=5002)