# Smartwise-Automated-Parking-Allocation-System
ParkWise is a QR-based smart parking management system built using Flask (Python), MySQL, and HTML/CSS/JS. It automates vehicle entry/exit, tracks slot availability in real-time, calculates billing, and provides a visual admin dashboard. The system aims to simplify and digitize the parking process efficiently.

 Features
 Admin Login
Secure login system that allows only authorized admins to access and manage the dashboard.
Ensures privacy and restricts unauthorized users from changing slot data or billing records.

 QR Code-Based Vehicle Registration
When a user enters the parking area, they fill a form to generate a unique QR code.
This code is scanned at entry and exit points to log time and track vehicle movement.

 Real-Time Slot Tracking with Color Indicators
Slots are dynamically updated and shown using color-coded indicators.
Green represents available slots, while Red shows occupied ones — updated live as QR codes are scanned.
This visual view makes it easy for admins to understand parking status at a glance.

Automated Billing System
Calculates parking fees based on the total time the vehicle stayed.
At the time of exit, the system generates a detailed bill with duration and amount.

Admin Dashboard with Analytics
The admin dashboard shows key metrics like total entries/exits, current slot status, and revenue.
Graphs and charts (using Chart.js or similar) give a clear visual of daily operations and trends.

 Backend and Database
The backend is developed using Flask for routing, logic, and session handling.
MySQL stores all vehicle data, timestamps, slot status, QR code info, and billing history.

 User-Friendly Frontend
Designed using HTML, CSS, and JavaScript for a clean, responsive interface.
Forms, dashboards, and slot indicators are easy to use and mobile-friendly.
