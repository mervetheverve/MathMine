from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum


class Operation(Enum):
    ADD = "+"
    SUBTRACT = "-"
    MULTIPLY = "*"
    DIVIDE = "/"

    def apply(self, left: int, right: int) -> int:
        if self is Operation.ADD:
            return left + right
        if self is Operation.SUBTRACT:
            return left - right
        if self is Operation.MULTIPLY:
            return left * right
        if self is Operation.DIVIDE:
            if right == 0:
                raise ValueError("Cannot divide by zero")
            return left // right
        raise ValueError("Unknown operation")


@dataclass(frozen=True)
class Equation:
    left: int
    right: int
    operation: Operation

    @property
    def target(self) -> int:
        return self.operation.apply(self.left, self.right)

    def describe(self) -> str:
        return f"Find: {self.target} from {self.left} {self.operation.value} {self.right}"


class EquationGenerator:
    def __init__(self, max_value: int = 9, seed: int | None = None) -> None:
        self.max_value = max_value
        self.random = random.Random(seed)
        self.allowed_operations = [Operation.ADD, Operation.SUBTRACT]

    def next_equation(self) -> Equation:
        operation = self.random.choice(self.allowed_operations)
        left = self.random.randint(0, self.max_value)
        right = self.random.randint(0, self.max_value)
        if operation is Operation.SUBTRACT and right > left:
            left, right = right, left
        return Equation(left=left, right=right, operation=operation)

    def increase_difficulty(self) -> None:
        self.max_value = min(self.max_value + 2, 20)

    def enable_multiplication(self) -> None:
        if Operation.MULTIPLY not in self.allowed_operations:
            self.allowed_operations.append(Operation.MULTIPLY)

    def enable_division(self) -> None:
        if Operation.DIVIDE not in self.allowed_operations:
            self.allowed_operations.append(Operation.DIVIDE)
