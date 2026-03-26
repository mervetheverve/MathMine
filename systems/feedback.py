"""Feedback system - 3-level hint escalation."""


class FeedbackData:
    """Data for rendering feedback to the player."""

    def __init__(self, feedback_type, message, detail=None):
        self.feedback_type = feedback_type  # 'correct', 'wrong_show', 'wrong_decompose', 'wrong_example'
        self.message = message
        self.detail = detail or {}


def generate_feedback(result, target, attempt_number, operation='+'):
    """Generate feedback based on the attempt.

    attempt_number: 1, 2, or 3+
    Returns a FeedbackData object.
    """
    if result == target:
        return FeedbackData(
            'correct',
            'Correct!',
            {'target': target, 'result': result}
        )

    if attempt_number == 1:
        # Level 1: Show what was produced vs needed
        return FeedbackData(
            'wrong_show',
            f'You made {result}. The slot needs {target}.',
            {'result': result, 'target': target}
        )

    elif attempt_number == 2:
        # Level 2: Decomposition hint
        hint = _decomposition_hint(target, operation)
        return FeedbackData(
            'wrong_decompose',
            f'Hint: {hint}',
            {'result': result, 'target': target, 'hint': hint}
        )

    else:
        # Level 3: Worked example of a similar problem
        example = _worked_example(target, operation)
        return FeedbackData(
            'wrong_example',
            f'Let me show you: {example}',
            {'result': result, 'target': target, 'example': example}
        )


def _decomposition_hint(target, operation):
    """Generate a decomposition hint for a target value."""
    if operation == '+':
        if target <= 10:
            a = target // 2
            b = target - a
            return f'Try breaking {target} into {a} and {b}'
        else:
            a = 10
            b = target - 10
            return f'Think: {a} + {b} = {target}'
    elif operation == '-':
        a = target + 3
        return f'Try starting from {a} and taking away 3'
    elif operation == '*':
        # Find smallest factor pair
        for f in range(2, target + 1):
            if target % f == 0:
                return f'Think: {f} groups of {target // f} = {target}'
        return f'The answer is {target}'
    elif operation == '/':
        # target is the quotient — hint about sharing
        return f'Think about sharing equally to get {target}'
    return f'The answer is close to {target}'


def generate_penalty_feedback(charge_lost, charge_remaining):
    """Generate feedback for a wrong-answer penalty."""
    msg = f'Portal energy lost! (-{int(charge_lost)})'
    return FeedbackData(
        'penalty',
        msg,
        {'charge_lost': charge_lost, 'charge_remaining': charge_remaining}
    )


def _worked_example(target, operation):
    """Generate a worked example for a similar problem."""
    if operation == '+':
        similar = target + 1 if target > 2 else target + 2
        a = similar // 2
        b = similar - a
        return f'{a} + {b} = {similar}. Now try to make {target}!'
    elif operation == '-':
        a = target + 2
        b = 2
        return f'{a} - {b} = {target}. Now try your problem!'
    elif operation == '*':
        # Use a nearby easy product
        for f in range(2, 6):
            if target % f == 0:
                other = target // f
                return f'{f} x {other} = {target}. Can you find the right pair?'
        return f'2 x {target // 2} is close. Try different numbers!'
    elif operation == '/':
        # Show a clean division example
        easy_div = target * 2
        return f'{easy_div} ÷ 2 = {target}. Now try your problem!'
    return f'The answer is {target}'
