"""Simple calculation utilities."""


def add(
    first_number: int,
    second_number: int,
    tax: int = 0,
) -> int:
    """Return the sum of two numbers and optional tax."""
    return first_number + second_number + tax


def divide(dividend: float, divisor: float) -> float:
    """Divide one number by another."""
    if divisor == 0:
        raise ValueError("Divisor cannot be zero.")
    return dividend / divisor
