# Pharma Industry Management System

A professional Pharmaceutical Management System built with Django.

## Features
- **Sales & Distribution Dashboard**: Track revenue, orders, and customer data.
- **HR & Payroll Management**: Manage employees, attendance, and payroll.
- **Inventory & Store Control**: Monitor medicine stocks, categories, and expiry dates.
- **Quality Control**: Integrated QC inspection and testing results.
- **Universal CRUD**: Flexible record management for all entities.

## Technology Stack
- **Backend**: Python 3.13, Django
- **Frontend**: HTML5, CSS3 (Bootstrap 5, FontAwesome, AOS animations)
- **Database**: SQLite

## Setup Instructions
1. Clone the repository.
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Install dependencies (if requirements.txt exists): `pip install -r requirements.txt`
5. Run migrations: `python manage.py migrate`
6. Start the server: `python manage.py runserver`

## License
MIT
