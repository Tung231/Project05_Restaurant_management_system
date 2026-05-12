# NEU Restaurant Management System (Project 05)

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange.svg)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)

## Introduction
The **NEU Restaurant Management System** is a digitized, highly normalized (BCNF) web-based ERP solution tailored for the Food and Beverage industry. Built with **FastAPI** and **MySQL**, the system focuses on resolving traditional operational bottlenecks such as table double-booking, billing errors, and unauthorized data access.

## Tech Stack
* **Backend:** Python 3, FastAPI, Uvicorn
* **Database:** MySQL 8.0, mysql-connector-python
* **Frontend:** HTML5, CSS3, Vanilla JavaScript, Bootstrap 5
* **Libraries & Tools:** * *Data Validation:* Pydantic
  * *Mock Data Generation:* Faker
  * *Analytics & UI:* Chart.js, SweetAlert2, Jinja2

## System Screenshots

### Analytics Dashboard
*(Chèn ảnh Dashboard thực tế vào đây)*

### Integrated Mini-POS & Conflict-Free Reservations
*(Chèn ảnh POS và Đặt bàn vào đây)*

## Database Architecture
The system is built on a strictly normalized database schema containing 8 core entities, secured by Role-Based Access Control (RBAC) and automated SQL Triggers.

*(Chèn ảnh ER Diagram vào đây)*
*(Conceptual Entity-Relationship Diagram)*

## Directory Structure

The project strictly adheres to a 3-Tier Architecture model:

```text
Project05_Restaurant_management_system/
├── app/
│   ├── core/           # Database configurations & Connection Pooling
│   ├── crud/           # Data Access Object (DAO) layer (MySQL queries)
│   ├── routers/        # FastAPI RESTful endpoints
│   ├── schemas/        # Pydantic models for strict data validation
│   ├── scripts/        # Utility scripts (Faker data generation)
│   ├── static/         # CSS, JS, and Images
│   ├── templates/      # Jinja2 HTML Templates (UI & RBAC Views)
│   ├── main.py         # FastAPI application entry point
│   └── master_seeder.py# Automated data seeding script (500+ records)
├── database/           
│   ├── schema.sql              # Core DDL for 8 normalized tables
│   ├── advanced_objects.sql    # Views, Triggers, Procedures, UDFs
│   └── security_and_roles.sql  # DCL for database-level user roles
├── docs/               
│   ├── 01_ER_Diagram.png       # Entity Relationship Diagram
│   └── 02_Relational_Schema.png# Relational Schema Design
├── .env.example        # Environment variables template
├── .gitignore          
├── requirements.txt    # Python dependencies
└── README.md
```

## 🛠️ Installation & Setup Guide

Follow these steps to set up and run the project on your local machine.

### 1. Clone the Repository
```bash
git clone https://github.com/Tung231/Project05_Restaurant_management_system.git
cd Project05_Restaurant_management_system
```

### 2. Set Up Virtual Environment
It is recommended to use a virtual environment to manage dependencies.
```bash
python -m venv venv
```
* **Activate on Windows:** `venv\Scripts\activate`
* **Activate on macOS/Linux:** `source venv/bin/activate`

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Configuration
1. Open your MySQL client (e.g., MySQL Workbench).
2. Execute the SQL scripts located in the `database/` folder **in this exact order**:
   * `schema.sql` (Creates DB and Tables)
   * `advanced_objects.sql` (Creates Views, UDFs, Triggers)
   * `security_and_roles.sql` (Sets up roles and permissions)
3. Create a `.env` file in the root directory (alongside `main.py`) and configure your MySQL credentials:

```ini
# .env file
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=RestaurantManagement
```

### 5. Generate Mock Data (Highly Recommended)
To test the analytical dashboards and reservation algorithms, populate the database with realistic mock data using the included Faker script:
```bash
python app/master_seeder.py
```
*Note: This will generate over 500+ rows including staff, customers, reservations, and invoices.*

### 6. Run the Application
Start the FastAPI server using Uvicorn:
```bash
uvicorn app.main:app --reload
```
Once running, open your web browser and navigate to:
* **Staff Management Portal:** `http://127.0.0.1:8000/`
