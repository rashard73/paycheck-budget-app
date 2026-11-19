
from flask import Flask, render_template, request, redirect, url_for, abort

from database import (
    add_paycheck,
    get_paychecks,
    get_paycheck,
    add_bill,
    get_bills,
    get_bill,
    update_bill,
    delete_bill,
    get_savings,
    save_savings,
    update_paycheck,
    delete_paycheck
)

from decimal import Decimal, InvalidOperation
from datetime import date

app = Flask(__name__)

@app.route('/')
def home():
    return 'welcome to the Paycheck Budgeting App!'

@app.route("/paychecks")
def show_paychecks():
    paychecks = get_paychecks()

    return render_template(
        "paychecks.html",
        paychecks=paychecks
    )

@app.route("/add-paycheck", methods=["GET", "POST"])
def add_paycheck_form():
    if request.method == "POST":
        amount = request.form.get("amount")
        date_received = request.form.get("date_received")

        try:
            date.fromisoformat(date_received)
        except (ValueError, TypeError):
            return "Invalid paycheck date.", 400

        try:
            amount_decimal = Decimal(amount)
            amount_cents = amount_decimal * 100

            if (not amount_decimal.is_finite()
                    or amount_cents != amount_cents.to_integral_value()
                    or amount_cents <= 0):
                return "Enter a valid positive amount in dollars and cents.", 400

            add_paycheck(int(amount_cents), date_received)

        except (InvalidOperation, TypeError, ValueError):
            return "Invalid paycheck amount.", 400

        return redirect(url_for("show_paychecks"))

    return render_template("add_paycheck.html")



@app.route("/paychecks/<int:paycheck_id>/edit",
           methods=["GET", "POST"])
def edit_paycheck_form(paycheck_id):
    paycheck = get_paycheck(paycheck_id)

    if paycheck is None:
        abort(404)

    if request.method == "POST":
        amount = request.form.get("amount")
        date_received = request.form.get("date_received")

        try:
            amount_decimal = Decimal(amount)
            cents = amount_decimal * 100

            if (not amount_decimal.is_finite()
                    or cents <= 0
                    or cents != cents.to_integral_value()
                    or cents > 9223372036854775807):
                raise ValueError

            date.fromisoformat(date_received)

        except (ValueError, TypeError, InvalidOperation):
            return "Invalid paycheck amount or date.", 400

        update_paycheck(
            paycheck_id,
            int(cents),
            date_received
        )

        return redirect(url_for("show_paychecks"))

    return render_template(
        "edit_paycheck.html",
        paycheck=paycheck
    )



@app.route("/paychecks/<int:paycheck_id>/delete",
           methods=["POST"])
def delete_paycheck_route(paycheck_id):
    paycheck = get_paycheck(paycheck_id)

    if paycheck is None:
        abort(404)

    delete_paycheck(paycheck_id)

    return redirect(url_for("show_paychecks"))


@app.route("/paychecks/<int:paycheck_id>/add-bill",
           methods=["GET", "POST"])
def add_bill_form(paycheck_id):
    paycheck = get_paycheck(paycheck_id)

    if paycheck is None:
        abort(404)

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        amount = request.form.get("amount")
        due_date = request.form.get("due_date")

        try:
            amount_cents = validate_bill(name, amount, due_date)
        except ValueError as error:
            return str(error), 400

        add_bill(name, amount_cents, due_date, paycheck_id)

        return redirect(url_for(
            "show_bills", paycheck_id=paycheck_id
        ))

    return render_template(
        "bill_form.html",
        paycheck_id=paycheck_id,
        bill=None
    )


@app.route("/paychecks/<int:paycheck_id>/bills")
def show_bills(paycheck_id):
    paycheck = get_paycheck(paycheck_id)

    if paycheck is None:
        abort(404)

    bills = get_bills(paycheck_id)
    savings = get_savings(paycheck_id)

    paycheck_amount = paycheck[1]
    total_bills = sum(bill[2] for bill in bills)

    remaining_balance = (
        paycheck_amount - total_bills - savings
    )

    return render_template(
        "bills.html",
        paycheck=paycheck,
        bills=bills,
        total_bills=total_bills,
        savings=savings,
        remaining_balance=remaining_balance
    )


def validate_bill(name, amount, due_date):
    if not name.strip():
        raise ValueError("Bill name is required.")

    try:
        amount_decimal = Decimal(amount)

        if not amount_decimal.is_finite():
            raise ValueError("Invalid bill amount.")

        amount_cents = amount_decimal * 100

        if (amount_cents <= 0 or
                amount_cents != amount_cents.to_integral_value() or
                amount_cents > 9223372036854775807):
            raise ValueError("Invalid bill amount.")

    except (InvalidOperation, TypeError):
        raise ValueError("Invalid bill amount.")

    try:
        date.fromisoformat(due_date)
    except (ValueError, TypeError):
        raise ValueError("Invalid due date.")

    return int(amount_cents)


@app.route("/bills/<int:bill_id>/edit",
           methods=["GET", "POST"])
def edit_bill_form(bill_id):
    bill = get_bill(bill_id)

    if bill is None:
        abort(404)

    paycheck_id = bill[4]

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        amount = request.form.get("amount")
        due_date = request.form.get("due_date")

        try:
            amount_cents = validate_bill(name, amount, due_date)
        except ValueError as error:
            return str(error), 400

        update_bill(bill_id, name, amount_cents, due_date)

        return redirect(url_for(
            "show_bills", paycheck_id=paycheck_id
        ))

    return render_template(
        "bill_form.html",
        paycheck_id=paycheck_id,
        bill=bill
    )


@app.route("/bills/<int:bill_id>/delete", methods=["POST"])
def delete_bill_route(bill_id):
    bill = get_bill(bill_id)

    if bill is None:
        abort(404)

    paycheck_id = bill[4]

    delete_bill(bill_id)

    return redirect(url_for(
        "show_bills", paycheck_id=paycheck_id
    ))


@app.route("/paychecks/<int:paycheck_id>/savings",
           methods=["GET", "POST"])
def manage_savings(paycheck_id):
    paycheck = get_paycheck(paycheck_id)

    if paycheck is None:
        abort(404)

    if request.method == "POST":
        amount = request.form.get("amount")

        try:
            amount_decimal = Decimal(amount)
            amount_cents = amount_decimal * 100

            if (not amount_decimal.is_finite()
                    or amount_cents < 0
                    or amount_cents != amount_cents.to_integral_value()
                    or amount_cents > 9223372036854775807):
                raise ValueError

            save_savings(paycheck_id, int(amount_cents))

        except (InvalidOperation, ValueError, TypeError):
            return "Invalid savings amount.", 400

        return redirect(url_for(
            "show_bills", paycheck_id=paycheck_id
        ))

    savings = get_savings(paycheck_id)

    return render_template(
        "savings.html",
        paycheck=paycheck,
        savings=savings
    )

if __name__ == '__main__':
    app.run(debug=False)

