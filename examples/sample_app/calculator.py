"""Simple calculation utilities."""


def add(
    first_number: int,
    second_number: int,
    tax: int = 100,
) -> int:
    """Return the sum of two numbers and optional tax.

    Args:
        first_number (int): The first number to add.
        second_number (int): The second number to add.
        tax (int, optional): The tax amount. Defaults to 100.

    Returns:
        int: The sum of the two numbers and tax.
    """
    return first_number + second_number + tax


def divide(dividend: float, divisor: float) -> float:
    """Divide one number by another."""
    if divisor == 0:
        raise ValueError("Divisor cannot be zero.")
    return dividend / divisor


def multiply(first_number: float, second_number: float) -> float:
    """Multiply two numbers."""
    return first_number * second_number


def subtract(first_number: float, second_number: float) -> float:
    """Subtract one number from another."""
    return first_number - second_number
