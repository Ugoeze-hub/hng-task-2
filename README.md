# Country Currency & Exchange API

A RESTful API that fetches country data from external APIs, stores it in a database, and provides CRUD operations with currency exchange rates and GDP calculations.

# Features

Fetch country data from RestCountries API

Get real-time exchange rates from ER API

Calculate estimated GDP based on population and exchange rates

Generate summary images with top GDP countries

MySQL database with proper caching

Filter and sort countries by various criteria

# Tech Stack
Framework: FastAPI

Database: MySQL (Aiven)

ORM: SQLAlchemy

Image Generation: Pillow (PIL)

HTTP Client: Requests

# Setup Instructions
## Prerequisites

Python 3.8+

MySQL database (Aiven recommended)

Aiven account for MySQL hosting

Installation
Clone the repository

bash
git clone <your-repo-url>
cd country-api
Create virtual environment

bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies

bash
pip install -r requirements.txt
Environment Configuration

Copy .env.example to .env

Configure your database connection:

env
DATABASE_URL=mysql+mysqlconnector://avnadmin:your_password@your-host.aivencloud.com:port/defaultdb
SSL Certificate

Download ca.pem from your Aiven dashboard

Place it in the project root directory

Run the application

bash
uvicorn main:app --reload
Database Schema
sql
countries
├── id (INT, PK, Auto Increment)
├── name (VARCHAR(255), Unique, Not Null)
├── capital (VARCHAR(255), Nullable)
├── region (VARCHAR(255), Nullable) 
├── population (BIGINT, Not Null)
├── currency_code (VARCHAR(10), Nullable)
├── exchange_rate (FLOAT, Nullable)
├── estimated_gdp (FLOAT, Nullable)
├── flag_url (VARCHAR(500), Nullable)
└── last_refreshed_at (DATETIME, Default: CURRENT_TIMESTAMP)
Usage Examples
Refresh Country Data
bash
curl -X POST "http://localhost:8000/countries/refresh"
Get African Countries
bash
curl "http://localhost:8000/countries?region=Africa"
Get Countries with USD Currency
bash
curl "http://localhost:8000/countries?currency=USD"
Get Top 5 GDP Countries
bash
curl "http://localhost:8000/countries?sort=gdp_desc"
Get Specific Country
bash
curl "http://localhost:8000/countries/Nigeria"
Get API Status
bash
curl "http://localhost:8000/status"
Get Summary Image
bash
curl "http://localhost:8000/countries/image" --output summary.png

# Author

Ugoeze Eluchie
Young tech enthusiast exploring backend development and data-driven innovation.

# License

MIT License © 2025 Ugoeze Eluchie