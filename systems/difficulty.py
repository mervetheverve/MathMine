"""Adaptive difficulty system - confidence tracking and number generation."""
import random


# Tiers for addition/subtraction
TIER_DEFS = {
    1: {'addend': (1, 5),   'target': (2, 9),    'label': 'Easy'},
    2: {'addend': (1, 9),   'target': (5, 15),   'label': 'Single Digit'},
    3: {'addend': (2, 12),  'target': (10, 20),  'label': 'Bridging 10'},
    4: {'addend': (5, 25),  'target': (15, 40),  'label': 'Two Digit'},
    5: {'addend': (10, 50), 'target': (30, 80),  'label': 'Big Numbers'},
}

# Tiers for multiplication — factor ranges and product ranges
TIER_DEFS_MULT = {
    1: {'factor': (2, 5),   'target': (4, 25),   'label': 'Easy Tables'},
    2: {'factor': (2, 9),   'target': (6, 45),   'label': 'Single Digit'},
    3: {'factor': (3, 12),  'target': (12, 72),  'label': 'Harder Tables'},
    4: {'factor': (4, 12),  'target': (20, 100), 'label': 'Full Tables'},
    5: {'factor': (5, 15),  'target': (30, 144), 'label': 'Big Products'},
}

# Tiers for division — divisor and quotient ranges
TIER_DEFS_DIV = {
    1: {'divisor': (2, 5),  'quotient': (1, 5),  'label': 'Easy Sharing'},
    2: {'divisor': (2, 9),  'quotient': (2, 9),  'label': 'Single Digit'},
    3: {'divisor': (2, 12), 'quotient': (3, 12), 'label': 'Harder Division'},
    4: {'divisor': (3, 12), 'quotient': (5, 15), 'label': 'Full Division'},
    5: {'divisor': (4, 15), 'quotient': (6, 20), 'label': 'Big Quotients'},
}

# How many correct answers needed to advance (increases per tier)
ADVANCE_THRESHOLD = {1: 3, 2: 4, 3: 5, 4: 6, 5: 999}


def _get_tier_defs(operation):
    """Return the appropriate tier definitions for an operation."""
    if operation == '*':
        return TIER_DEFS_MULT
    elif operation == '/':
        return TIER_DEFS_DIV
    return TIER_DEFS


class AdaptiveDifficulty:
    """Tracks player confidence per tier and adapts difficulty."""

    def __init__(self):
        self.current_tier = 1
        self.max_tier = 5
        self.confidence = {}
        for tier in range(1, self.max_tier + 1):
            self.confidence[tier] = {
                'correct_streak': 0,
                'incorrect_streak': 0,
                'total_correct': 0,
                'total_incorrect': 0,
                'recent_answers': [],
            }

    def record_correct(self, answer_key=None):
        """Record a correct answer at the current tier."""
        tier = self.current_tier
        conf = self.confidence[tier]
        conf['correct_streak'] += 1
        conf['incorrect_streak'] = 0
        conf['total_correct'] += 1
        if answer_key:
            conf['recent_answers'].append(answer_key)
            conf['recent_answers'] = conf['recent_answers'][-10:]

        # Advance tier if enough correct with variety
        threshold = ADVANCE_THRESHOLD.get(tier, 5)
        if conf['correct_streak'] >= threshold and self._has_variety(tier):
            if self.current_tier < self.max_tier:
                self.current_tier += 1
                conf['correct_streak'] = 0

    def record_incorrect(self):
        """Record an incorrect answer at the current tier."""
        tier = self.current_tier
        conf = self.confidence[tier]
        conf['incorrect_streak'] += 1
        conf['correct_streak'] = max(0, conf['correct_streak'] - 1)
        conf['total_incorrect'] += 1

        # Drop tier after 3 incorrect in a row
        if conf['incorrect_streak'] >= 3:
            if self.current_tier > 1:
                self.current_tier -= 1
                conf['incorrect_streak'] = 0

    def _has_variety(self, tier):
        """Check if recent answers show variety."""
        answers = self.confidence[tier]['recent_answers']
        if len(answers) < 3:
            return True
        last_3 = answers[-3:]
        return len(set(last_3)) >= 2

    def generate_target(self, operation='+'):
        """Generate a single target value appropriate for current tier."""
        if operation == '*':
            tier_def = TIER_DEFS_MULT.get(self.current_tier, TIER_DEFS_MULT[1])
            f_lo, f_hi = tier_def['factor']
            a = random.randint(f_lo, f_hi)
            b = random.randint(f_lo, f_hi)
            return a * b
        elif operation == '/':
            tier_def = TIER_DEFS_DIV.get(self.current_tier, TIER_DEFS_DIV[1])
            d_lo, d_hi = tier_def['divisor']
            q_lo, q_hi = tier_def['quotient']
            quotient = random.randint(q_lo, q_hi)
            # Return the quotient as the target (what the player needs to produce)
            return quotient
        else:
            tier_def = TIER_DEFS.get(self.current_tier, TIER_DEFS[1])
            lo, hi = tier_def['target']
            return random.randint(lo, hi)

    def generate_pair_for_target(self, target, operation='+'):
        """Generate a valid (a, b) pair that produces the target."""
        if operation == '+':
            tier_def = TIER_DEFS.get(self.current_tier, TIER_DEFS[1])
            a_lo, a_hi = tier_def['addend']
            max_a = min(a_hi, target - 1)
            min_a = max(a_lo, target - a_hi)
            min_a = max(1, min(min_a, max_a))
            a = random.randint(min_a, max(min_a, max_a))
            b = target - a
            return a, b

        elif operation == '-':
            tier_def = TIER_DEFS.get(self.current_tier, TIER_DEFS[1])
            a_lo, a_hi = tier_def['addend']
            max_b = min(a_hi, a_hi)
            b = random.randint(max(1, a_lo), max_b)
            a = target + b
            return a, b

        elif operation == '*':
            # target is a product — find factor pairs within tier range
            tier_def = TIER_DEFS_MULT.get(self.current_tier, TIER_DEFS_MULT[1])
            f_lo, f_hi = tier_def['factor']
            # Find all factor pairs of target in range
            pairs = []
            for f in range(f_lo, f_hi + 1):
                if f != 0 and target % f == 0:
                    other = target // f
                    if f_lo <= other <= f_hi:
                        pairs.append((f, other))
            if pairs:
                return random.choice(pairs)
            # Fallback: generate a new product from two factors
            a = random.randint(f_lo, f_hi)
            b = target // a if a != 0 and target % a == 0 else random.randint(f_lo, f_hi)
            return a, b

        elif operation == '/':
            # target is the quotient — generate dividend and divisor
            tier_def = TIER_DEFS_DIV.get(self.current_tier, TIER_DEFS_DIV[1])
            d_lo, d_hi = tier_def['divisor']
            divisor = random.randint(d_lo, d_hi)
            dividend = target * divisor  # guarantees clean division
            return dividend, divisor

        return target, 0

    def generate_blueprint_targets(self, num_slots, operation='+'):
        """Generate target values for blueprint slots at current tier.
        Ensures variety — no more than 2 slots share the same target."""
        targets = []
        max_retries = 20
        for _ in range(num_slots):
            for attempt in range(max_retries):
                t = self.generate_target(operation)
                # Allow at most 2 of the same target
                if targets.count(t) < 2 or attempt == max_retries - 1:
                    targets.append(t)
                    break
        return targets

    def generate_blocks_for_blueprint(self, blueprint, operation='+'):
        """Generate number blocks that can solve the blueprint targets.
        Returns list of (value, tier) tuples for blocks to spawn."""
        blocks = []
        tier = self.current_tier

        for slot in blueprint.slots:
            if slot.filled:
                continue
            target = slot.target
            a, b = self.generate_pair_for_target(target, operation)
            blocks.append((a, tier))
            blocks.append((b, tier))

        # Add 2-3 distractor blocks
        defs = _get_tier_defs(operation)
        tier_def = defs.get(tier, defs[1])
        if operation == '*':
            d_lo, d_hi = tier_def['factor']
        elif operation == '/':
            d_lo, d_hi = tier_def['divisor']
        else:
            d_lo, d_hi = tier_def['addend']

        num_distractors = random.randint(2, 3)
        for _ in range(num_distractors):
            blocks.append((random.randint(d_lo, d_hi), tier))

        random.shuffle(blocks)
        return blocks

    def serialize(self):
        return {
            'current_tier': self.current_tier,
            'confidence': {
                str(k): {
                    'correct_streak': v['correct_streak'],
                    'incorrect_streak': v['incorrect_streak'],
                    'total_correct': v['total_correct'],
                    'total_incorrect': v['total_incorrect'],
                }
                for k, v in self.confidence.items()
            },
        }

    def deserialize(self, data):
        self.current_tier = data.get('current_tier', 1)
        for k, v in data.get('confidence', {}).items():
            tier = int(k)
            if tier in self.confidence:
                self.confidence[tier].update(v)
                self.confidence[tier].setdefault('recent_answers', [])
