"""Portal system - charge tracking and border problem generation."""
import random
from settings import PORTAL_CHARGE_MULTIPLIER, PORTAL_CHARGE_BASE


class PortalSystem:
    """Manages portal charging and transition logic."""

    CHARGE_MAX = 100.0

    def __init__(self):
        self.charge = 0.0

    def add_charge(self, tier, correct=True):
        """Add charge based on tier difficulty.
        Returns the amount of charge added."""
        if not correct:
            return 0
        multiplier = PORTAL_CHARGE_MULTIPLIER.get(tier, 1)
        amount = PORTAL_CHARGE_BASE * multiplier
        self.charge = min(self.CHARGE_MAX, self.charge + amount)
        return amount

    def get_charge_ratio(self):
        return self.charge / self.CHARGE_MAX

    def is_ready(self):
        return self.charge >= self.CHARGE_MAX

    def remove_charge(self, amount):
        """Remove charge as penalty. Returns actual amount removed."""
        old = self.charge
        self.charge = max(0.0, self.charge - amount)
        return old - self.charge

    def reset(self):
        self.charge = 0.0

    def generate_border_problem(self):
        """Generate a repeated-addition border problem for portal activation.
        Returns (base_number, repeat_count, target)."""
        base = random.randint(2, 5)
        repeats = random.randint(2, 4)
        target = base * repeats
        return base, repeats, target

    def serialize(self):
        return {'charge': self.charge}

    def deserialize(self, data):
        self.charge = data.get('charge', 0.0)
