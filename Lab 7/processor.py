import math

DIGITS = "0123456789"

CONDITION_MULTIPLIERS = {
    "MINT": 1.25,
    "LIKE_NEW": 1.00,
    "VERY_GOOD": 0.80,
    "GOOD": 0.60,
    "POOR": 0.30,
}


def verify_isbn10_format(isbn_str):
    """Return a description of a well-formed ISBN-10, or None if the input is invalid.

    Valid: 9 ASCII digits followed by a digit or 'X' (hyphens/outer spaces ignored).
    """
    if not isinstance(isbn_str, str):
        return None

    cleaned = isbn_str.replace('-', '').strip()

    if len(cleaned) != 10:
        return None
    # ASCII-only check: str.isdigit() also accepts characters like '²' that int() rejects
    if any(c not in DIGITS for c in cleaned[:9]):
        return None
    if cleaned[9] not in DIGITS and cleaned[9] not in "Xx":
        return None

    first_digit = int(cleaned[0])
    group_code = cleaned[1:4]
    check_char = cleaned[9].upper()
    return f"Group {group_code}: Starts {first_digit}, Checksum {check_char}"


def calculate_depreciation_factor(book_age_str):
    """Parse 'age/lifespan' and return a factor in [0.1, 1.0], or None if the input is invalid."""
    if not isinstance(book_age_str, str):
        return None

    parts = book_age_str.split('/')
    if len(parts) != 2:
        return None

    try:
        age = float(parts[0])
        life = float(parts[1])
    except (ValueError, OverflowError):
        return None

    # reject nan / inf, non-positive lifespan (avoids ZeroDivisionError) and negative age
    if not (math.isfinite(age) and math.isfinite(life)):
        return None
    if life <= 0 or age < 0:
        return None

    depreciation = 1.0 - (age / life)
    return round(max(0.1, depreciation), 2)


def lookup_condition_multiplier(condition_code):
    """Return the price multiplier for a condition code, or None if it is unknown/invalid."""
    if not isinstance(condition_code, str):
        return None

    grade = condition_code.strip().upper()
    return CONDITION_MULTIPLIERS.get(grade)


def main():
    print("==== Running verify_isbn10_format ====")
    isbn_in = input("Enter ISBN-10 (e.g. 0-306-40615-2): ")
    isbn_result = verify_isbn10_format(isbn_in)
    print(isbn_result if isbn_result is not None else "Invalid ISBN-10")

    print("\n==== Running calculate_depreciation_factor ====")
    age_in = input("Enter age/lifespan in years (e.g. 3/10): ")
    dep_result = calculate_depreciation_factor(age_in)
    if dep_result is not None:
        print("Depreciation Factor:", dep_result)
    else:
        print("Invalid age/lifespan input")

    print("\n==== Running lookup_condition_multiplier ====")
    cond_in = input("Enter condition (e.g. MINT, GOOD, POOR): ")
    mult_result = lookup_condition_multiplier(cond_in)
    if mult_result is not None:
        print("Multiplier:", mult_result)
    else:
        print("Unknown condition code")


if __name__ == "__main__":
    main()
