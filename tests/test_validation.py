
import pytest

from app import validate_bill


def test_valid_bill():
    result = validate_bill(
        "Car Payment", "250.50", "2026-11-25"
    )
    assert result == 25050


def test_negative_bill_amount():
    with pytest.raises(ValueError):
        validate_bill(
            "Car Payment", "-100", "2026-11-25"
        )


def test_zero_bill_amount():
    with pytest.raises(ValueError):
        validate_bill(
            "Car Payment", "0", "2026-11-25"
        )


def test_empty_bill_name():
    with pytest.raises(ValueError):
        validate_bill(
            "", "250", "2026-11-25"
        )


def test_invalid_date():
    with pytest.raises(ValueError):
        validate_bill(
            "Car Payment", "250", "2026-02-30"
        )


def test_fractional_cents():
    with pytest.raises(ValueError):
        validate_bill(
            "Car Payment", "250.555", "2026-11-25"
        )


def test_non_numeric_amount():
    with pytest.raises(ValueError):
        validate_bill(
            "Car Payment", "hello", "2026-11-25"
        )
