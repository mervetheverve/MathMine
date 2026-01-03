from __future__ import annotations

import random
from dataclasses import dataclass

from mathmine.blocks import Block, BlockType


@dataclass(frozen=True)
class Position:
    x: int
    y: int

    def neighbors(self, width: int, height: int) -> list[Position]:
        positions = []
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = self.x + dx, self.y + dy
            if 0 <= nx < width and 0 <= ny < height:
                positions.append(Position(nx, ny))
        return positions


class World:
    def __init__(self, width: int = 20, height: int = 20, seed: int | None = None) -> None:
        self.width = width
        self.height = height
        self.random = random.Random(seed)
        self.grid: dict[Position, Block] = {}

    def populate(self, number_duplicates: int = 8, include_operator_blocks: bool = False) -> None:
        self.grid.clear()
        for value in range(10):
            for _ in range(number_duplicates):
                self._place_block(Block(BlockType.NUMBER, value))
        if include_operator_blocks:
            for symbol in ("+", "-", "*", "/"):
                for _ in range(4):
                    self._place_block(Block(BlockType.OPERATOR, symbol))

    def _place_block(self, block: Block) -> None:
        for _ in range(1000):
            position = Position(
                self.random.randrange(self.width),
                self.random.randrange(self.height),
            )
            if position not in self.grid:
                self.grid[position] = block
                return
        raise RuntimeError("Unable to place block; grid may be full.")

    def block_at(self, position: Position) -> Block | None:
        return self.grid.get(position)

    def take_block(self, position: Position) -> Block | None:
        return self.grid.pop(position, None)

    def describe_area(self, position: Position) -> str:
        block = self.block_at(position)
        if block:
            return f"You see a block here: {block.display()}"
        return "The tile is empty."
