DELIVERY MANAGEMENT APPLICATION
=================================================

1. PROJECT OVERVIEW
-------------------
Web-based delivery management system developed with Django.
Complete solution for transport and delivery company operations.

2. MAIN FEATURES (SECTIONS 0-6)
--------------------------------
Section 0: Favorites – Quick access to frequently used features
Section 1: Tables – Clients, Drivers, Vehicles, Destinations, Service Types
Section 2: Shipments – Creation, tracking, delivery tours, automatic pricing
Section 3: Billing – Automatic invoices with 19% VAT calculation
Section 4: Incidents – Problem reporting and management
Section 5: Claims – Customer claims handling and tracking
Section 6: Dashboards – Statistics, reports, and data analysis

3. INSTALLATION INSTRUCTIONS
----------------------------
1. Extract the ZIP file to your desired location
2. Open terminal/command prompt in the project folder
3. Create virtual environment:
   python -m venv venv
4. Activate environment:
   Windows: venv\Scripts\activate
   Linux/Mac: source venv/bin/activate
5. Install dependencies:
   pip install -r requirements.txt
6. Setup database:
   python manage.py migrate
7. Create administrator account:
   python manage.py createsuperuser
8. Start the development server:
   python manage.py runserver
9. Access the application:
   Open browser and go to: http://localhost:8000

4. PROJECT STRUCTURE
--------------------
si_project/        - Django project configuration
common/            - Shared data models (Client, Shipment, Invoice, etc.)
agent/             - Agent/Operator interface and functionality
client/            - Client interface and dashboard
driver/            - Driver interface and tour management
manager/           - Manager interface and reporting
authentication/    - User authentication and authorization
static/            - CSS, JavaScript, and image files
templates/         - HTML templates for all applications
manage.py          - Django management script
requirements.txt   - Python package dependencies
db.sqlite3         - Database file (development)

5. REQUIRED LIBRARIES
---------------------
Django==4.2.7      - Web framework
Pillow==10.0.0     - Image processing

6. DEMONSTRATION ACCOUNTS
-------------------------
Agent: agent@transport.com / agent123
Client: client@example.com / client123
Driver: driver@transport.com / driver123
Manager: manager@transport.com / manager123

7. TROUBLESHOOTING
------------------
Problem: "Module not found" error
Solution: Run: pip install -r requirements.txt

Problem: Database migration errors
Solution: Run: python manage.py migrate

Problem: Port 8000 is already in use
Solution: Use different port: python manage.py runserver 8001

Problem: Admin user not created
Solution: Run: python manage.py createsuperuser

8. TECHNICAL SPECIFICATIONS
---------------------------
- Framework: Django 4.2.7
- Database: SQLite (development)
- Frontend: HTML, CSS, Bootstrap
- Python Version: 3.8 or higher
- Architecture: MVT (Model-View-Template)

9. DATA MODELS IMPLEMENTED
--------------------------
- Client (client management with balance tracking)
- Shipment (package delivery with automatic pricing)
- Invoice (billing with automatic tax calculation)
- DeliveryTour (route and driver assignment)
- Incident (problem reporting and tracking)
- Claim (customer complaint management)
- Vehicle (fleet management)
- Driver (driver management and availability)

10. TEAM INFORMATION
--------------------
Team Members:
1. BOUZOUAD Mohamed Aymen
2. BAGHDAD Asma
3. ISSOLAH Mariane
4. OURADJ Aya

Project: SI2 - Transport & Delivery Management System
Supervisor: R. BOUDOUR
Submission Date: January 24, 2026

=================================================
END OF DOCUMENT
=================================================
