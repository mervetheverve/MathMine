from __future__ import annotations

from dataclasses import dataclass

from mathmine.equations import Equation, EquationGenerator, Operation
from mathmine.player import Player
from mathmine.world import Position, World


@dataclass
class GameState:
    equation: Equation
    attempts: int = 0


class MathMineGame:
    def __init__(self, seed: int | None = None) -> None:
        self.world = World(seed=seed)
        self.world.populate()
        self.player = Player(position=Position(0, 0))
        self.generator = EquationGenerator(seed=seed)
        self.state = GameState(equation=self.generator.next_equation())

    def describe(self) -> str:
        return (
            f"{self.state.equation.describe()}\n"
            f"Score: {self.player.score} | Attempts: {self.state.attempts}\n"
            f"Location: ({self.player.position.x}, {self.player.position.y})\n"
            f"{self.world.describe_area(self.player.position)}\n"
            f"Inventory: {self.player.inventory.describe()}"
        )

    def pick_up(self) -> str:
        block = self.world.take_block(self.player.position)
        if not block:
            return "There is nothing to pick up."
        self.player.inventory.add(block)
        return f"Picked up: {block.display()}"

    def submit_answer(self, left: int, right: int, operation: Operation) -> str:
        self.state.attempts += 1
        if not self.player.inventory.remove_numbers([left, right]):
            return "You do not have the required numbers in your inventory."
        result = operation.apply(left, right)
        if result == self.state.equation.target:
            self.player.score += 1
            self.generator.increase_difficulty()
            self.state = GameState(equation=self.generator.next_equation())
            return "Correct! Score increased and a new equation appears."
        return f"Incorrect. {left} {operation.value} {right} = {result}. Try again."

    def move(self, direction: str) -> None:
        self.player.move(direction, self.world.width, self.world.height)
