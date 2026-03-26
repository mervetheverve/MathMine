"""Blueprint system - structures the player builds by solving math."""
import random
from dataclasses import dataclass


@dataclass
class Slot:
    """A single slot in a blueprint that needs a target value."""
    label: str
    target: int
    filled: bool = False


class Blueprint:
    """A structure to build, made up of slots that need target values."""

    def __init__(self, bp_id, name, slots_data):
        self.bp_id = bp_id
        self.name = name
        self.slots = [Slot(s['label'], s['target']) for s in slots_data]

    def fill_slot(self, value):
        """Try to fill the first unfilled slot matching the value.
        Returns the slot index if filled, or -1 if no match."""
        for i, slot in enumerate(self.slots):
            if not slot.filled and slot.target == value:
                slot.filled = True
                return i
        return -1

    def get_next_target(self):
        """Get the next unfilled slot's target value, or None."""
        for slot in self.slots:
            if not slot.filled:
                return slot.target
        return None

    def get_unfilled_slots(self):
        """Get all unfilled slots."""
        return [(i, s) for i, s in enumerate(self.slots) if not s.filled]

    def is_complete(self):
        return all(s.filled for s in self.slots)

    def reset(self):
        for slot in self.slots:
            slot.filled = False

    def serialize(self):
        return {
            'id': self.bp_id,
            'name': self.name,
            'slots': [{'label': s.label, 'target': s.target, 'filled': s.filled}
                      for s in self.slots],
        }

    @classmethod
    def deserialize(cls, data):
        bp = cls(data['id'], data['name'],
                 [{'label': s['label'], 'target': s['target']}
                  for s in data['slots']])
        for i, s in enumerate(data['slots']):
            bp.slots[i].filled = s.get('filled', False)
        return bp


# Blueprint TEMPLATES - targets are filled in dynamically by the difficulty system
STACKLANDS_TEMPLATES = [
    {'id': 'garden_wall',  'name': 'Garden Wall',  'labels': ['Stone', 'Stone', 'Post']},
    {'id': 'wooden_house', 'name': 'Wooden House', 'labels': ['Wall', 'Wall', 'Roof', 'Door']},
    {'id': 'watch_tower',  'name': 'Watch Tower',  'labels': ['Base', 'Pillar', 'Pillar', 'Top']},
    {'id': 'grand_bridge', 'name': 'Grand Bridge', 'labels': ['Plank', 'Plank', 'Support', 'Rail', 'Rail']},
    {'id': 'windmill',     'name': 'Windmill',     'labels': ['Base', 'Tower', 'Blade', 'Blade']},
    {'id': 'fountain',     'name': 'Fountain',     'labels': ['Basin', 'Pillar', 'Spout']},
]

CRUMBLE_CAVES_TEMPLATES = [
    {'id': 'cave_bridge',  'name': 'Cave Bridge',  'labels': ['Plank', 'Plank', 'Support']},
    {'id': 'lantern_post', 'name': 'Lantern Post', 'labels': ['Post', 'Hook', 'Lantern', 'Base']},
    {'id': 'mining_cart',  'name': 'Mining Cart',   'labels': ['Wheel', 'Wheel', 'Axle', 'Bed', 'Handle']},
    {'id': 'rock_arch',    'name': 'Rock Arch',     'labels': ['Pillar', 'Pillar', 'Keystone']},
    {'id': 'crystal_lamp', 'name': 'Crystal Lamp',  'labels': ['Base', 'Stem', 'Crystal']},
]

FACTOR_FOREST_TEMPLATES = [
    {'id': 'tree_house',   'name': 'Tree House',    'labels': ['Trunk', 'Trunk', 'Platform', 'Roof']},
    {'id': 'vine_bridge',  'name': 'Vine Bridge',   'labels': ['Vine', 'Vine', 'Plank']},
    {'id': 'forest_gate',  'name': 'Forest Gate',   'labels': ['Post', 'Post', 'Arch', 'Lock']},
    {'id': 'owl_perch',    'name': 'Owl Perch',     'labels': ['Branch', 'Branch', 'Nest']},
    {'id': 'mushroom_hut', 'name': 'Mushroom Hut',  'labels': ['Stem', 'Cap', 'Cap', 'Door', 'Window']},
]

DIVIDING_DESERT_TEMPLATES = [
    {'id': 'oasis_well',   'name': 'Oasis Well',    'labels': ['Stone', 'Stone', 'Bucket']},
    {'id': 'sand_tower',   'name': 'Sand Tower',    'labels': ['Base', 'Column', 'Column', 'Top']},
    {'id': 'shade_tent',   'name': 'Shade Tent',    'labels': ['Pole', 'Pole', 'Fabric', 'Rope']},
    {'id': 'cactus_fence', 'name': 'Cactus Fence',  'labels': ['Post', 'Post', 'Rail']},
    {'id': 'sun_dial',     'name': 'Sun Dial',      'labels': ['Base', 'Pillar', 'Pointer', 'Ring', 'Ring']},
]

# Map biome keys to their template lists
BIOME_TEMPLATES = {
    'stacklands': STACKLANDS_TEMPLATES,
    'crumble_caves': CRUMBLE_CAVES_TEMPLATES,
    'factor_forest': FACTOR_FOREST_TEMPLATES,
    'dividing_desert': DIVIDING_DESERT_TEMPLATES,
}


def create_blueprint_from_template(template, difficulty, operation='+'):
    """Create a Blueprint with targets generated from the difficulty system."""
    targets = difficulty.generate_blueprint_targets(
        len(template['labels']), operation)
    slots_data = [
        {'label': label, 'target': target}
        for label, target in zip(template['labels'], targets)
    ]
    return Blueprint(template['id'], template['name'], slots_data)
