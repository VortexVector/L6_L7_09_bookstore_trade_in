"""
Lab 6 - Part 2: Branch coverage tests for bookstore_trade_in.py
Run:
    coverage run --branch -m pytest BranchCoverageTest_bookstore_trade_in.py
    coverage report -m
Every decision is exercised both True and False, including loops that run
zero times and the default values used by dict.get().
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


# ---------- validation: `not isinstance(...) or bonus < 0` ----------

def test_single_paperback_good():
    result = process_book_buybacks([make_batch("paperback", [book("good")])], 5.0)
    assert result == {"total_payout": 8.0, "status": "COMPLETED"}


def test_batches_not_a_list_raises():
    with pytest.raises(ValueError):
        process_book_buybacks({"a": 1}, 1.0)


def test_negative_bonus_raises():
    with pytest.raises(ValueError):
        process_book_buybacks([], -0.01)


def test_zero_bonus_is_valid_and_empty_list_gives_zero_credit():
    # bonus == 0 is NOT < 0 ; empty list => outer loop runs zero times
    assert process_book_buybacks([], 0) == {"total_payout": 0.0, "status": "ZERO_CREDIT"}


# ---------- intake_approved ----------

def test_unapproved_batch_skipped():
    result = process_book_buybacks([make_batch(books=[book()], approved=False)], 0.0)
    assert result["status"] == "ZERO_CREDIT"


def test_missing_intake_key_defaults_to_not_approved():
    result = process_book_buybacks([{"format": "paperback", "books": [book()]}], 0.0)
    assert result["status"] == "ZERO_CREDIT"


# ---------- format branches (and .get defaults) ----------

def test_textbook_good():
    assert process_book_buybacks([make_batch("textbook", [book()])], 0.0)["total_payout"] == 40.0


def test_hardcover_good():
    assert process_book_buybacks([make_batch("hardcover", [book()])], 0.0)["total_payout"] == 15.0


def test_default_format_is_paperback_and_default_book_fields():
    # no "format" key -> paperback ; book dict is empty -> all defaults (good, 0 pages, genuine)
    batches = [{"intake_approved": True, "books": [{}]}]
    result = process_book_buybacks(batches, 0.0)
    assert result == {"total_payout": 8.0, "status": "COMPLETED"}


def test_unknown_format_rejected_and_skipped():
    result = process_book_buybacks([make_batch("magazine", [book()])], 0.0)
    assert result == {"total_payout": 0.0, "status": "ZERO_CREDIT"}


def test_batch_without_books_key_defaults_to_empty():
    batches = [{"intake_approved": True, "format": "paperback"}]
    assert process_book_buybacks(batches, 0.0)["status"] == "ZERO_CREDIT"


def test_batch_with_empty_books_loop_runs_zero_times():
    assert process_book_buybacks([make_batch("hardcover", [])], 0.0)["status"] == "ZERO_CREDIT"


# ---------- condition branches ----------

def test_mint_condition():
    assert process_book_buybacks([make_batch("textbook", [book("mint")])], 0.0)["total_payout"] == 50.0


def test_poor_condition():
    assert process_book_buybacks([make_batch("hardcover", [book("poor")])], 0.0)["total_payout"] == 6.0


def test_unrecognised_condition_treated_as_good():
    assert process_book_buybacks([make_batch("paperback", [book("fair")])], 0.0)["total_payout"] == 8.0


# ---------- missing pages / counterfeit ----------

def test_missing_pages_rejected_but_loop_continues():
    batches = [make_batch("paperback", [book(missing=2), book()])]
    assert process_book_buybacks(batches, 0.0) == {"total_payout": 8.0, "status": "COMPLETED"}


def test_counterfeit_textbook_resets_credit_and_breaks():
    batches = [make_batch("textbook", [book(), book(counterfeit=True), book("mint")])]
    assert process_book_buybacks(batches, 0.0) == {"total_payout": 0.0, "status": "ZERO_CREDIT"}


def test_counterfeit_non_textbook_continues():
    batches = [make_batch("hardcover", [book(counterfeit=True), book()])]
    assert process_book_buybacks(batches, 0.0) == {"total_payout": 15.0, "status": "COMPLETED"}


# ---------- payout_in_credit ----------

def test_credit_bonus_added_when_payout_in_credit():
    batches = [make_batch("paperback", [book()], credit=True)]
    assert process_book_buybacks(batches, 2.5)["total_payout"] == 10.5


def test_credit_bonus_not_added_when_not_in_credit():
    batches = [make_batch("paperback", [book()], credit=False)]
    assert process_book_buybacks(batches, 2.5)["total_payout"] == 8.0


def test_missing_payout_in_credit_key_defaults_false():
    batches = [{"intake_approved": True, "format": "paperback", "books": [book()]}]
    assert process_book_buybacks(batches, 9.0)["total_payout"] == 8.0


def test_multiple_batches_accumulate():
    batches = [make_batch("paperback", [book()]), make_batch("hardcover", [book()])]
    assert process_book_buybacks(batches, 0.0)["total_payout"] == 23.0


# ---------- final status: rejected_items > 4, total == 0 ----------

def test_exactly_four_rejections_is_not_audit():
    books = [book(missing=1) for _ in range(4)] + [book()]
    assert process_book_buybacks([make_batch("paperback", books)], 0.0)["status"] == "COMPLETED"


def test_five_rejections_triggers_audit_rejected():
    books = [book(missing=1) for _ in range(5)] + [book()]
    assert process_book_buybacks([make_batch("paperback", books)], 0.0) == {
        "total_payout": 8.0, "status": "AUDIT_REJECTED"}


def test_audit_rejected_takes_priority_over_zero_credit():
    books = [book(missing=1) for _ in range(5)]
    assert process_book_buybacks([make_batch("paperback", books)], 0.0)["status"] == "AUDIT_REJECTED"


# ---------- inspect_scanner_calibration ----------

def test_scanner_none_is_no_data():
    assert inspect_scanner_calibration(None) == "NO_DATA"


def test_scanner_empty_matrix_is_no_data():
    assert inspect_scanner_calibration([]) == "NO_DATA"


def test_scanner_two_consecutive_bad_readings_recalibrate():
    assert inspect_scanner_calibration([[1, 6, 7]]) == "RECALIBRATE"


def test_scanner_single_bad_reading_is_fine():
    assert inspect_scanner_calibration([[1, 6, 1]]) == "CALIBRATED"


def test_scanner_streak_resets_between_readings():
    assert inspect_scanner_calibration([[6, 1, 6, 1, 6]]) == "CALIBRATED"


def test_scanner_streak_resets_between_devices():
    # last bad of device 1 and first bad of device 2 must NOT combine
    assert inspect_scanner_calibration([[1, 6], [6, 1]]) == "CALIBRATED"


def test_scanner_second_device_triggers_recalibrate():
    assert inspect_scanner_calibration([[1, 2], [8, 9]]) == "RECALIBRATE"


def test_scanner_threshold_is_strictly_greater_than_five():
    assert inspect_scanner_calibration([[5, 5, 5]]) == "CALIBRATED"


def test_scanner_device_with_no_readings():
    assert inspect_scanner_calibration([[]]) == "CALIBRATED"
