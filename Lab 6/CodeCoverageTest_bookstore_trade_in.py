"""
Lab 6 - Part 1: Code (line) coverage tests for bookstore_trade_in.py
Run:
    coverage run -m pytest CodeCoverageTest_bookstore_trade_in.py
    coverage report -m
"""
import pytest
from bookstore_trade_in import process_book_buybacks, inspect_scanner_calibration


def make_batch(fmt="paperback", books=None, approved=True, credit=False):
    return {
        "intake_approved": approved,
        "format": fmt,
        "payout_in_credit": credit,
        "books": books if books is not None else [],
    }


def book(condition="good", missing=0, counterfeit=False):
    return {"missing_pages": missing, "condition": condition, "counterfeit": counterfeit}


# ---------------- process_book_buybacks ----------------

def test_single_paperback_good():
    batches = [make_batch("paperback", [book("good")])]
    result = process_book_buybacks(batches, 5.0)
    assert result["total_payout"] == 8.0
    assert result["status"] == "COMPLETED"


def test_invalid_batches_type_raises():
    with pytest.raises(ValueError):
        process_book_buybacks("not a list", 1.0)


def test_unapproved_batch_is_skipped():
    result = process_book_buybacks([make_batch(books=[book()], approved=False)], 0.0)
    assert result == {"total_payout": 0.0, "status": "ZERO_CREDIT"}


def test_textbook_mint_with_credit_bonus():
    # 40 * 1.25 = 50, + 5 bonus = 55
    batches = [make_batch("textbook", [book("mint")], credit=True)]
    result = process_book_buybacks(batches, 5.0)
    assert result == {"total_payout": 55.0, "status": "COMPLETED"}


def test_hardcover_poor_condition():
    # 15 * 0.40 = 6
    result = process_book_buybacks([make_batch("hardcover", [book("poor")])], 0.0)
    assert result == {"total_payout": 6.0, "status": "COMPLETED"}


def test_unknown_format_is_rejected():
    result = process_book_buybacks([make_batch("comic", [book()])], 0.0)
    assert result == {"total_payout": 0.0, "status": "ZERO_CREDIT"}


def test_missing_pages_book_is_rejected_others_paid():
    batches = [make_batch("paperback", [book(missing=3), book()])]
    result = process_book_buybacks(batches, 0.0)
    assert result == {"total_payout": 8.0, "status": "COMPLETED"}


def test_counterfeit_textbook_wipes_batch_credit():
    batches = [make_batch("textbook", [book(), book(counterfeit=True), book()])]
    result = process_book_buybacks(batches, 0.0)
    assert result == {"total_payout": 0.0, "status": "ZERO_CREDIT"}


def test_counterfeit_paperback_earns_nothing_but_batch_continues():
    batches = [make_batch("paperback", [book(counterfeit=True), book()])]
    result = process_book_buybacks(batches, 0.0)
    assert result == {"total_payout": 8.0, "status": "COMPLETED"}


def test_audit_rejected_when_more_than_four_rejections():
    books = [book(missing=1) for _ in range(5)] + [book()]
    result = process_book_buybacks([make_batch("paperback", books)], 0.0)
    assert result == {"total_payout": 8.0, "status": "AUDIT_REJECTED"}


# ---------------- inspect_scanner_calibration ----------------

def test_scanner_no_data():
    assert inspect_scanner_calibration([]) == "NO_DATA"


def test_scanner_recalibrate_on_two_consecutive_misreads():
    assert inspect_scanner_calibration([[1, 6, 7]]) == "RECALIBRATE"


def test_scanner_calibrated_when_streak_is_broken():
    assert inspect_scanner_calibration([[6, 1, 6, 2]]) == "CALIBRATED"
