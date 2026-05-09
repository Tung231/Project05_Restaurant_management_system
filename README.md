# 🍽️ NEU Restaurant Management System (Project 05)

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange.svg)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)

## 📌 Introduction
The **NEU Restaurant Management System** is a digitized, highly normalized (BCNF) web-based ERP solution tailored for the Food and Beverage industry. Built with **FastAPI** and **MySQL**, the system focuses on resolving traditional operational bottlenecks such as table double-booking, billing errors, and unauthorized data access.

### ✨ Key Features
* **Intelligent Reservation Engine:** Implements a backend temporal validation algorithm (± 2-hour window) to autonomously prevent table booking conflicts.
* **Integrated Mini-POS:** A split-screen billing interface with dynamic Client-Side State Management (JS Cart) and 80mm thermal receipt generation.
* **Advanced Database Architecture:** Utilizes SQL Triggers for automated physical table state management and User-Defined Functions (UDFs) for absolute financial precision.
* **Multi-Layered RBAC:** Enforces strict Role-Based Access Control (Manager, Cashier, Waiter) simultaneously at the MySQL engine layer and the Frontend DOM.
* **Real-time Analytics:** Interactive Dashboard rendering business insights using `Chart.js`.

---

## 📂 Directory Structure

The project strictly adheres to a 3-Tier Architecture model:

```text
Project05_Restaurant_management_system/
├── app/
│   ├── core/           # ⚙️ Database configurations & Connection Pooling
│   ├── crud/           # 🛡️ Data Access Object (DAO) layer (MySQL queries)
│   ├── routers/        # 🛣️ FastAPI RESTful endpoints
│   ├── schemas/        # 🧱 Pydantic models for strict data validation
│   ├── scripts/        # 🤖 Utility scripts (Faker data generation)
│   ├── static/         # 🎨 CSS, JS, and Images (Client-side Cart Logic)
│   ├── templates/      # 🖥️ Jinja2 HTML Templates (UI & RBAC Views)
│   ├── main.py         # 🚀 FastAPI application entry point
│   └── master_seeder.py# 🏭 Automated data seeding script (500+ records)
├── database/           
│   ├── schema.sql              # Core DDL for 8 normalized tables
│   ├── advanced_objects.sql    # Views, Triggers, Procedures, UDFs
│   └── security_and_roles.sql  # DCL for database-level user roles
├── docs/               # ERD and Architectural diagrams
├── .env.example        # Environment variables template
├── .gitignore          
├── requirements.txt    # Python dependencies
└── README.md

## 🛠️ Installation & Setup Guide

Follow these steps to set up and run the project on your local machine.

---

### 1. Clone the Repository

```bash
git clone https://github.com/Tung231/Project05_Restaurant_management_system.git
cd Project05_Restaurant_management_system
```

---

### 2. Set Up Virtual Environment

It is recommended to use a virtual environment to manage dependencies.

```bash
python -m venv venv
```

- **Windows:** `venv\Scripts\activate`
- **macOS/Linux:** `source venv/bin/activate`

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Database Configuration

1. Open your MySQL client (e.g., MySQL Workbench).
2. Execute the SQL scripts located in the `database/` folder **in this exact order**:
   - `schema.sql` — Creates DB and Tables
   - `advanced_objects.sql` — Creates Views, UDFs, Triggers
   - `security_and_roles.sql` — Sets up roles and permissions
3. Create a `.env` file in the root directory (alongside `main.py`) and configure your MySQL credentials:

```ini
# .env file
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=RestaurantManagement
```

---

### 5. Generate Mock Data *(Highly Recommended)*

To test the analytical dashboards and reservation algorithms, populate the database with realistic mock data using the included Faker script:

```bash
python app/master_seeder.py
```

> **Note:** This will generate **500+ rows** of data including staff, customers, reservations, and invoices.

---

### 6. Run the Application

Start the FastAPI server using Uvicorn:

```bash
uvicorn app.main:app --reload
```

Once running, open your browser and navigate to:

| Portal | URL |
|--------|-----|
| 🌐 Customer Portal (Public) | `http://127.0.0.1:8000/` |
| 🔐 Staff Login Portal | `http://127.0.0.1:8000/login` |
