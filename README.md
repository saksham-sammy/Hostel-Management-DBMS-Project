# PCU Hostel Manager — Smart Allocation & DBMS System

## 📥 Direct Download

[![Download ZIP](https://img.shields.io/badge/Download-Source_Code_(ZIP)-2ea44f?style=for-the-badge&logo=github)](https://github.com/saksham-sammy/Hostel-Management-DBMS-Project/archive/refs/heads/main.zip)

> **Quick Download**: Click the badge above to download the latest source code as a `.zip` archive directly from GitHub, or use **Code > Download ZIP**.

---


A dual-interface **Hostel Room & Student Allocation Management System** developed for Database Management Systems (DBMS). It includes both an **Interactive Web Allocation Portal** (`index.html` / `hostel.html`) ready for cloud deployment on Vercel and a **Python Tkinter + MySQL Desktop DBMS Engine** (`hostel_management1.py` & `hostel_management2.py`) featuring live SQL query logging, ACID transaction management, and relational schema enforcement.

---

## Key Features

### 1. Interactive Web Allocation Portal (`index.html` / `hostel.html`)
- **Real-Time Analytics Dashboard**: Instant metrics for Total Rooms, Available Rooms, Occupied Rooms, and Total Residents.
- **Smart Room Inventory**: Create and delete hostel rooms with custom capacities (1–10 beds), live occupancy progress, and automatic `Available` / `Full` status badges.
- **Transactional Student Allocation**: Allocate students (with Student Name and unique Student ID/PRN) to available rooms with automatic capacity validation and duplicate-ID prevention.
- **Live Search & Filter**: Instant filtering across room numbers, student names, and student PRNs/IDs.
- **Persistent Browser Storage**: State is persisted automatically in `localStorage` with one-click demo data reset.

### 2. Python Tkinter + MySQL Desktop DBMS Engine (`hostel_management1.py` & `hostel_management2.py`)
- **Relational MySQL Backend**: Automated database (`hostel_db`) and table provisioning (`rooms`, `students`, `allocations`) with Foreign Key constraints (`ON DELETE CASCADE`).
- **Live SQL Execution Console**: Built-in dark-themed SQL log (`ScrolledText`) that prints every `CREATE`, `SELECT`, `INSERT`, `UPDATE`, and `DELETE` statement along with bound parameters in real time.
- **ACID Transaction Safety**: Explicit `commit()` and `rollback()` handling ensuring room occupant counts and student allocation records remain strictly synchronized.
- **Enhanced UI (`hostel_management2.py`)**: Adds computed `Space Left` columns, horizontal/vertical scrollbars, status bar telemetry, and an **Execute Custom SQL** console for ad-hoc relational queries.

---

## Project Structure

```text
Hostel Management/
├── index.html              # Interactive Web Portal (Vercel entrypoint)
├── hostel.html             # Standalone copy of the Web Allocation Portal
├── hostel_management1.py   # Python Tkinter + MySQL DBMS Desktop App (v1)
├── hostel_management2.py   # Enhanced Python Tkinter + MySQL DBMS App (v2 with SpaceLeft & Status Bar)
├── vercel.json             # Vercel static deployment configuration
├── .gitignore              # Git ignore rules
└── README.md               # Project documentation
```

---

## Getting Started

### Running the Web Portal
1. Open `index.html` directly in any modern web browser, or serve locally:
   ```bash
   npx serve .
   ```
2. Deploy directly to Vercel with zero configuration (`vercel.json` included).

### Running the Python + MySQL Desktop App
1. **Prerequisites**:
   - Python 3.8+
   - MySQL Server running on `localhost`
   - Install the MySQL connector:
     ```bash
     pip install mysql-connector-python
     ```
2. **Configure Database Credentials**:
   Update `DB_CONFIG` in `hostel_management1.py` / `hostel_management2.py` with your MySQL username and password:
   ```python
   DB_CONFIG = {
       'host': 'localhost',
       'user': 'root',
       'password': 'your_password',
       'database': 'hostel_db',
       'autocommit': False
   }
   ```
3. **Launch the Application**:
   ```bash
   python hostel_management2.py
   ```