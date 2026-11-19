# Paycheck-to-Paycheck Budgeting App

A full-stack budgeting web application built with Python and Flask that helps users manage paychecks, organize bills, allocate savings, and calculate how much money remains between paydays.

## Overview

Managing finances between paychecks can be challenging, especially when accounting for upcoming bills and savings goals.

This application helps users create a budget for each paycheck and understand how much money remains after planned expenses and savings.

## Features

- **Paycheck Management:** Add, view, edit, and delete paychecks.
- **Bill Management:** Create, view, edit, and delete bills associated with individual paychecks.
- **Savings Allocation:** Set and update savings amounts for each paycheck.
- **Budget Dashboard:** View paycheck amounts, total bills, savings, and remaining balances.
- **Over-Budget Warnings:** Display an alert when planned expenses and savings exceed available income.
- **Input Validation:** Reject invalid monetary amounts and dates.
- **Persistent Storage:** Store records using SQLite.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Flask | Web framework and routing |
| SQLite | Relational database |
| HTML / Jinja | Dynamic webpage templates |
| Bootstrap | Responsive interface |
| pytest | Automated testing |

## Screenshots

### Paycheck Overview
<img width="1108" height="683" alt="Paycheck-Overview" src="https://github.com/user-attachments/assets/83ccee78-82e0-48c9-b407-cb94a80b2c46" />

### Budget Dashboard
<img width="1111" height="684" alt="Budget-Dashboard" src="https://github.com/user-attachments/assets/571ccd1c-554b-4b28-b99e-7049b80a5078" />


*Add screenshots of the paycheck overview and budget dashboard here.*

## Installation

1. Clone the repository.

   ```bash
   git clone https://github.com/rashard73/paycheck-budget-app.git
   cd paycheck-budget-app
   ```

2. Create a virtual environment.

   ```bash
   python -m venv .venv
   ```

3. Activate the environment.

   On Windows PowerShell:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

4. Install dependencies.

   ```bash
   python -m pip install -r requirements.txt
   ```

5. Initialize the database.

   ```bash
   python database.py
   ```

6. Start the application.

   ```bash
   python app.py
   ```

7. Open `http://127.0.0.1:5000/paychecks` in your browser.

## Testing

The application currently has **11 passing automated tests** covering input validation and database operations.

Additionally, 60 manual acceptance tests have been completed across paycheck management, bill management, savings, budget calculations, and interface functionality.

Run automated tests with:

```bash
python -m pytest -v
```

Tests involving SQLite use an isolated temporary database to avoid modifying application data.

## Database Design

The application uses three main tables:

- `paychecks` — Stores paycheck amounts and dates.
- `bills` — Stores bills associated
