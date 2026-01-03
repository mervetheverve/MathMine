from __future__ import annotations

from dataclasses import dataclass, field

from mathmine.blocks import Block, BlockType
from mathmine.world import Position


@dataclass
class Inventory:
    numbers: list[int] = field(default_factory=list)
    operators: list[str] = field(default_factory=list)

    def add(self, block: Block) -> None:
        if block.block_type is BlockType.NUMBER:
            self.numbers.append(int(block.value))
        elif block.block_type is BlockType.OPERATOR:
            self.operators.append(str(block.value))

    def describe(self) -> str:
        number_display = ", ".join(str(value) for value in self.numbers) or "(none)"
        operator_display = ", ".join(self.operators) or "(none)"
        return f"Numbers: {number_display} | Operators: {operator_display}"

    def remove_numbers(self, values: list[int]) -> bool:
        temp = list(self.numbers)
        for value in values:
            if value not in temp:
                return False
            temp.remove(value)
        self.numbers = temp
        return True


@dataclass
class Player:
    position: Position
    inventory: Inventory = field(default_factory=Inventory)
    score: int = 0

    def move(self, direction: str, width: int, height: int) -> None:
        dx, dy = 0, 0
        if direction == "n":
            dy = -1
        elif direction == "s":
            dy = 1
        elif direction == "e":
            dx = 1
        elif direction == "w":
            dx = -1
        nx = max(0, min(width - 1, self.position.x + dx))
        ny = max(0, min(height - 1, self.position.y + dy))
        self.position = Position(nx, ny)
