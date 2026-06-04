from typing import Optional


def ship_type_group_from_code(code: Optional[int]) -> Optional[str]:
    if code is None:
        return None

    first_digit = code // 10  # e.g. 60-69 -> 6

    if first_digit == 6:
        return "passenger"   # includes cruise & ferries
    if first_digit == 7:
        return "cargo"
    if first_digit == 8:
        return "tanker"
    if code == 30:
        return "fishing"
    if code in (31, 32, 33, 34, 35, 50, 51, 52, 53, 54, 55, 56):
        return "service"
    if code in (36, 37):
        return "pleasure"

    return "other"