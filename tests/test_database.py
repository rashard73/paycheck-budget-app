
import pytest
import database


@pytest.fixture
def test_db(tmp_path, monkeypatch):
    test_path = tmp_path / "test_budget.db"

    monkeypatch.setattr(
        database, "DATABASE_PATH", test_path
    )

    database.initialize_database()

    return test_path


def test_add_and_retrieve_paycheck(test_db):
    database.add_paycheck(180000, "2026-11-19")

    paychecks = database.get_paychecks()

    assert len(paychecks) == 1
    assert paychecks[0][1] == 180000


def test_bill_crud(test_db):
    database.add_paycheck(180000, "2026-11-19")
    paycheck_id = database.get_paychecks()[0][0]

    database.add_bill(
        "Car Payment", 25000, "2026-11-25", paycheck_id
    )

    bills = database.get_bills(paycheck_id)

    assert len(bills) == 1
    assert bills[0][2] == 25000

    bill_id = bills[0][0]

    database.update_bill(
        bill_id, "Car Payment", 27500, "2026-11-25"
    )

    assert database.get_bill(bill_id)[2] == 27500

    database.delete_bill(bill_id)

    assert database.get_bills(paycheck_id) == []


def test_savings_updates_instead_of_duplicates(test_db):
    database.add_paycheck(180000, "2026-11-19")
    paycheck_id = database.get_paychecks()[0][0]

    database.save_savings(paycheck_id, 20000)
    database.save_savings(paycheck_id, 35000)

    assert database.get_savings(paycheck_id) == 35000

    connection = database.get_connection()
    try:
        count = connection.execute(
            "SELECT COUNT(*) FROM savings WHERE paycheck_id = ?",
            (paycheck_id,)
        ).fetchone()[0]
    finally:
        connection.close()

    assert count == 1


def test_delete_paycheck_removes_related_records(test_db):
    database.add_paycheck(180000, "2026-11-19")
    paycheck_id = database.get_paychecks()[0][0]

    database.add_bill(
        "Phone", 8500, "2026-11-25", paycheck_id
    )
    database.save_savings(paycheck_id, 20000)

    database.delete_paycheck(paycheck_id)

    assert database.get_paycheck(paycheck_id) is None
    assert database.get_bills(paycheck_id) == []

    connection = database.get_connection()
    try:
        savings_count = connection.execute(
            "SELECT COUNT(*) FROM savings WHERE paycheck_id = ?",
            (paycheck_id,)
        ).fetchone()[0]
    finally:
        connection.close()

    assert savings_count == 0
