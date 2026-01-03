from __future__ import annotations

import sys

from mathmine.equations import Operation
from mathmine.game import MathMineGame


def parse_operation(value: str) -> Operation | None:
    for operation in Operation:
        if operation.value == value:
            return operation
    return None


def main() -> int:
    game = MathMineGame()
    print("Welcome to MathMine! Explore, collect blocks, and solve equations.")
    print("Commands: n/s/e/w (move), look, pickup, submit a b op, inventory, quit")
    while True:
        print("\n" + game.describe())
        command = input("> ").strip().lower()
        if not command:
            continue
        if command in {"quit", "exit"}:
            print("Thanks for playing!")
            return 0
        if command in {"n", "s", "e", "w"}:
            game.move(command)
            continue
        if command == "look":
            print(game.world.describe_area(game.player.position))
            continue
        if command == "pickup":
            print(game.pick_up())
            continue
        if command == "inventory":
            print(game.player.inventory.describe())
            continue
        if command.startswith("submit"):
            parts = command.split()
            if len(parts) != 4:
                print("Usage: submit <left> <right> <op>")
                continue
            try:
                left = int(parts[1])
                right = int(parts[2])
            except ValueError:
                print("Left and right must be numbers.")
                continue
            operation = parse_operation(parts[3])
            if not operation:
                print("Operation must be one of +, -, *, /.")
                continue
            print(game.submit_answer(left, right, operation))
            continue
        print("Unknown command.")
    

if __name__ == "__main__":
    sys.exit(main())
