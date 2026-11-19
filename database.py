from multiprocessing import connection
import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).resolve().parent / "budget.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database():
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS paychecks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount_cents INTEGER Not NULL CHECK (amount_cents >= 0),
            date_received TEXT NOT NULL
            )
        """)

        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            amount_cents INTEGER NOT NULL CHECK (amount_cents >= 0),
            due_date TEXT NOT NULL,
            paycheck_id INTEGER NOT NULL,
            FOREIGN KEY (paycheck_id) REFERENCES paychecks(id)
        )
        """)


        cursor.execute("""
            CREATE TABLE IF NOT EXISTS savings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paycheck_id INTEGER NOT NULL UNIQUE,
            amount_cents INTEGER NOT NULL
            CHECK (amount_cents >= 0),
            FOREIGN KEY (paycheck_id)
            REFERENCES paychecks(id)
        )
        """)


        connection.commit()
        connection.close()


def add_paycheck(amount_cents, date_received):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO paychecks (amount_cents, date_received)
        VALUES (?, ?)
        """,
        (amount_cents, date_received)
    )

    connection.commit()
    connection.close()

def get_paychecks():
     connection = get_connection()
     cursor = connection.cursor()
     cursor.execute("SELECT * From Paychecks")
     paycheck = cursor.fetchall()
     connection.close()
     return paycheck


def update_paycheck(paycheck_id, amount_cents, date_received):
    connection = get_connection()

    try:
        connection.execute("""
            UPDATE paychecks
            SET amount_cents = ?, date_received = ?
            WHERE id = ?
        """, (amount_cents, date_received, paycheck_id))

        connection.commit()
    finally:
        connection.close()


def delete_paycheck(paycheck_id):
    connection = get_connection()

    try:
        # Delete related records first.
        connection.execute(
            "DELETE FROM bills WHERE paycheck_id = ?",
            (paycheck_id,)
        )

        connection.execute(
            "DELETE FROM savings WHERE paycheck_id = ?",
            (paycheck_id,)
        )

        connection.execute(
            "DELETE FROM paychecks WHERE id = ?",
            (paycheck_id,)
        )

        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def add_bill(name, amount_cents, due_date, paycheck_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO bills (name, amount_cents, due_date, paycheck_id)
        VALUES (?, ?, ?, ?)
    """, (name, amount_cents, due_date, paycheck_id))

    connection.commit()
    connection.close()


def get_bills(paycheck_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM bills WHERE paycheck_id = ?
    """, (paycheck_id,))

    bills = cursor.fetchall()
    connection.close()
    return bills


def update_bill(bill_id, name, amount_cents, due_date):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE bills
        SET name = ?, amount_cents = ?, due_date = ?
        WHERE id = ?
    """, (name, amount_cents, due_date, bill_id))

    connection.commit()
    connection.close()


def delete_bill(bill_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM bills WHERE id = ?
    """, (bill_id,))

    connection.commit()
    connection.close()


def get_paycheck(paycheck_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM paychecks WHERE id = ?",
        (paycheck_id,)
    )

    paycheck = cursor.fetchone()
    connection.close()
    return paycheck


def get_bill(bill_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM bills WHERE id = ?",
        (bill_id,)
    )

    bill = cursor.fetchone()
    connection.close()
    return bill


def get_savings(paycheck_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT amount_cents
        FROM savings
        WHERE paycheck_id = ?
    """, (paycheck_id,))

    result = cursor.fetchone()
    connection.close()

    return result[0] if result else 0


def save_savings(paycheck_id, amount_cents):
    connection = get_connection()

    try:
        connection.execute("""
            INSERT INTO savings (paycheck_id, amount_cents)
            VALUES (?, ?)
            ON CONFLICT(paycheck_id)
            DO UPDATE SET amount_cents = excluded.amount_cents
        """, (paycheck_id, amount_cents))

        connection.commit()
    finally:
        connection.close()


if __name__ == "__main__":
    initialize_database()
