from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class BlockType(Enum):
    NUMBER = "number"
    OPERATOR = "operator"


@dataclass(frozen=True)
class Block:
    block_type: BlockType
    value: int | str

    def display(self) -> str:
        if self.block_type is BlockType.NUMBER:
            return str(self.value)
        return str(self.value)
