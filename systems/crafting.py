"""Crafting system - combines number blocks with operations."""


def compute(value_a, value_b, operation):
    """Compute the result of combining two values with an operation.
    Returns the result or None if invalid."""
    if operation == '+':
        return value_a + value_b
    elif operation == '-':
        result = value_a - value_b
        if result < 0:
            return None  # no negative results
        return result
    elif operation == '*':
        return value_a * value_b
    elif operation == '/':
        if value_b == 0:
            return None
        if value_a % value_b != 0:
            return None  # no remainders for this age
        return value_a // value_b
    return None


def compute_multi(values, operation):
    """Compute the result of combining 2-4 values with an operation.
    Applies left-to-right evaluation. Returns the result or None if invalid."""
    if len(values) < 2:
        return None
    result = values[0]
    for v in values[1:]:
        result = compute(result, v, operation)
        if result is None:
            return None
    return result


def check_against_blueprint(result, blueprint):
    """Check if a crafting result matches any unfilled blueprint slot.
    Returns the slot index if matched, -1 otherwise."""
    if result is None:
        return -1
    return blueprint.fill_slot(result)
