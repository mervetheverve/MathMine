"""Player inventory - stores collected number blocks."""
from settings import INVENTORY_MAX


class InventoryItem:
    """A single item in the inventory."""

    def __init__(self, value, tier=1):
        self.value = value
        self.tier = tier

    def __repr__(self):
        return f"Block({self.value})"


class Inventory:
    """Holds collected number blocks."""

    def __init__(self):
        self.items = []

    def add(self, value, tier=1):
        if len(self.items) >= INVENTORY_MAX:
            return False
        self.items.append(InventoryItem(value, tier))
        return True

    def remove(self, index):
        if 0 <= index < len(self.items):
            return self.items.pop(index)
        return None

    def is_full(self):
        return len(self.items) >= INVENTORY_MAX

    def count(self):
        return len(self.items)

    def clear(self):
        self.items.clear()

    def serialize(self):
        return [{"value": item.value, "tier": item.tier} for item in self.items]

    def deserialize(self, data):
        self.items = [InventoryItem(d["value"], d["tier"]) for d in data]
