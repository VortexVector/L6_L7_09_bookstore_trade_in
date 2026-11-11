from hypothesis import given, strategies as st
from processor import (
    verify_isbn10_format,
    calculate_depreciation_factor,
    lookup_condition_multiplier,
)

VALID_MULTIPLIERS = {1.25, 1.00, 0.80, 0.60, 0.30}


@given(st.text() | st.none())
def test_verify_isbn10_format_no_crash(s):
    try:
        verify_isbn10_format(s)
    except Exception as e:
        assert False, f"verify_isbn10_format crashed with: {e!r} for input {s!r}"


@given(st.text() | st.none())
def test_calculate_depreciation_factor_safe(s):
    try:
        calculate_depreciation_factor(s)
    except Exception as e:
        assert False, f"calculate_depreciation_factor crashed with: {e!r} for input {s!r}"


@given(st.text() | st.none())
def test_lookup_condition_multiplier_safe(s):
    try:
        lookup_condition_multiplier(s)
    except Exception as e:
        assert False, f"lookup_condition_multiplier crashed with: {e!r} for input {s!r}"


@given(st.one_of(st.none(), st.integers(), st.floats(), st.lists(st.integers()), st.booleans()))
def test_all_functions_handle_non_string_input(x):
    for func in (verify_isbn10_format, calculate_depreciation_factor, lookup_condition_multiplier):
        try:
            func(x)
        except Exception as e:
            assert False, f"{func.__name__} crashed with: {e!r} for input {x!r}"


@given(st.text() | st.none())
def test_depreciation_result_is_none_or_within_bounds(s):
    result = calculate_depreciation_factor(s)
    assert result is None or 0.1 <= result <= 1.0


@given(st.text() | st.none())
def test_condition_result_is_none_or_known_multiplier(s):
    result = lookup_condition_multiplier(s)
    assert result is None or result in VALID_MULTIPLIERS


@given(st.text() | st.none())
def test_isbn_result_is_none_or_formatted_string(s):
    result = verify_isbn10_format(s)
    assert result is None or (isinstance(result, str) and result.startswith("Group "))


@given(st.text(alphabet="0123456789", min_size=9, max_size=9), st.sampled_from("0123456789Xx"))
def test_well_formed_isbn_is_accepted(nine_digits, check):
    assert verify_isbn10_format(nine_digits + check) is not None


@given(st.integers(min_value=0, max_value=200), st.integers(min_value=1, max_value=200))
def test_valid_age_and_lifespan_returns_number(age, life):
    result = calculate_depreciation_factor(f"{age}/{life}")
    assert isinstance(result, float)
    assert 0.1 <= result <= 1.0


@given(st.sampled_from(["MINT", "LIKE_NEW", "VERY_GOOD", "GOOD", "POOR"]))
def test_known_conditions_return_multiplier(code):
    assert lookup_condition_multiplier(code) in VALID_MULTIPLIERS


def test_known_good_examples():
    assert verify_isbn10_format("0-306-40615-2") == "Group 306: Starts 0, Checksum 2"
    assert calculate_depreciation_factor("3/10") == 0.7
    assert lookup_condition_multiplier(" mint ") == 1.25


def test_edge_cases_do_not_crash():
    assert verify_isbn10_format("") is None
    assert verify_isbn10_format("12345") is None
    assert verify_isbn10_format("abcdefghij") is None
    assert calculate_depreciation_factor("5/0") is None
    assert calculate_depreciation_factor("abc") is None
    assert calculate_depreciation_factor("1/2/3") is None
    assert calculate_depreciation_factor("nan/inf") is None
    assert lookup_condition_multiplier("") is None
    assert lookup_condition_multiplier("BROKEN") is None
