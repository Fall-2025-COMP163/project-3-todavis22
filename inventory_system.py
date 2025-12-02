"""
COMP 163 - Project 3: Quest Chronicles
Inventory System Module - Starter Code

Name: [Your Name Here]

AI Usage: [Document any AI assistance used]

This module handles inventory management, item usage, and equipment.
"""

from custom_exceptions import (
    InventoryFullError,
    ItemNotFoundError,
    InsufficientResourcesError,
    InvalidItemTypeError
)

# Maximum inventory size
MAX_INVENTORY_SIZE = 20

# ============================================================================
# INVENTORY MANAGEMENT
# ============================================================================
def add_item_to_inventory(character, item_id):
    """Add an item to character's inventory"""
    if "inventory" not in character:
        character["inventory"] = []

    if len(character["inventory"]) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory is full!")

    character["inventory"].append(item_id)
    return True


def remove_item_from_inventory(character, item_id):
    """Remove an item from character's inventory"""
    if "inventory" not in character or item_id not in character["inventory"]:
        raise ItemNotFoundError(f"Item '{item_id}' not found in inventory")

    character["inventory"].remove(item_id)
    return True


def has_item(character, item_id):
    """Check if character has a specific item"""
    if "inventory" not in character:
        return False
    return item_id in character["inventory"]


def count_item(character, item_id):
    """Count how many of a specific item the character has"""
    if "inventory" not in character:
        return 0
    return character["inventory"].count(item_id)


def get_inventory_space_remaining(character):
    """Calculate how many more items can fit in inventory"""
    if "inventory" not in character:
        return MAX_INVENTORY_SIZE
    return MAX_INVENTORY_SIZE - len(character["inventory"])


def clear_inventory(character):
    """Remove all items from inventory"""
    if "inventory" not in character:
        character["inventory"] = []
        return []
    removed_items = character["inventory"]
    character["inventory"] = []
    return removed_items

# ============================================================================ 
# ITEM USAGE
# ============================================================================

def use_item(character, item_id, item_data):
    """Use a consumable item"""
    if "inventory" not in character or item_id not in character["inventory"]:
        raise ItemNotFoundError(f"{item_id} not in inventory.")

    if item_id in item_data:
        item = item_data[item_id]
    else:
        item = item_data

    if "type" not in item or item["type"] != "consumable":
        raise InvalidItemTypeError(f"{item_id} cannot be used directly.")

    if "effect" not in item:
        raise InvalidItemTypeError(f"{item_id} has no effect to apply.")

    stat, value = parse_item_effect(item["effect"])
    apply_stat_effect(character, stat, value)
    character["inventory"].remove(item_id)

    item_name = item["name"] if "name" in item else item_id
    return f"Used {item_name}, {stat} increased by {value}."


def equip_weapon(character, item_id, item_data):
    """Equip a weapon"""
    if "inventory" not in character or item_id not in character["inventory"]:
        raise ItemNotFoundError(f"{item_id} not in inventory.")

    if item_id in item_data:
        item = item_data[item_id]
    else:
        item = item_data

    if "type" not in item or item["type"] != "weapon":
        raise InvalidItemTypeError(f"{item_id} is not a weapon.")

    if "effect" not in item:
        raise InvalidItemTypeError(f"{item_id} has no effect to apply.")

    if "equipped_weapon" in character and character["equipped_weapon"] is not None:
        unequip_weapon(character)

    stat, value = parse_item_effect(item["effect"])
    if stat not in character:
        character[stat] = 0
    character[stat] += value

    character["equipped_weapon"] = item_id
    character["equipped_weapon_effect"] = item["effect"]
    character["inventory"].remove(item_id)

    item_name = item["name"] if "name" in item else item_id
    char_name = character["name"] if "name" in character else "Character"
    return f"{char_name} equipped {item_name} (+{value} {stat})."


def equip_armor(character, item_id, item_data):
    """Equip armor"""
    if "inventory" not in character or item_id not in character["inventory"]:
        raise ItemNotFoundError(f"{item_id} not in inventory.")

    if item_id in item_data:
        item = item_data[item_id]
    else:
        item = item_data

    if "type" not in item or item["type"] != "armor":
        raise InvalidItemTypeError(f"{item_id} is not armor.")

    if "effect" not in item:
        raise InvalidItemTypeError(f"{item_id} has no effect to apply.")

    if "equipped_armor" in character and character["equipped_armor"] is not None:
        unequip_armor(character)

    stat, value = parse_item_effect(item["effect"])
    if stat not in character:
        character[stat] = 0
    character[stat] += value

    character["equipped_armor"] = item_id
    character["equipped_armor_effect"] = item["effect"]
    character["inventory"].remove(item_id)

    item_name = item["name"] if "name" in item else item_id
    char_name = character["name"] if "name" in character else "Character"
    return f"{char_name} equipped {item_name} (+{value} {stat})."

# ============================================================================ 
# UNEQUIP FUNCTIONS
# ============================================================================

def unequip_weapon(character):
    """Unequip current weapon"""
    if "equipped_weapon" not in character or character["equipped_weapon"] is None:
        return None

    weapon_id = character["equipped_weapon"]
    stat, value = parse_item_effect(character["equipped_weapon_effect"])
    character[stat] -= value

    if "inventory" not in character:
        character["inventory"] = []

    if len(character["inventory"]) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory is full.")

    character["inventory"].append(weapon_id)
    character["equipped_weapon"] = None
    character["equipped_weapon_effect"] = None
    return weapon_id


def unequip_armor(character):
    """Unequip current armor"""
    if "equipped_armor" not in character or character["equipped_armor"] is None:
        return None

    armor_id = character["equipped_armor"]
    stat, value = parse_item_effect(character["equipped_armor_effect"])
    character[stat] -= value

    if "inventory" not in character:
        character["inventory"] = []

    if len(character["inventory"]) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory is full.")

    character["inventory"].append(armor_id)
    character["equipped_armor"] = None
    character["equipped_armor_effect"] = None
    return armor_id

# ============================================================================ 
# SHOP SYSTEM
# ============================================================================

def purchase_item(character, item_id, item_data):
    """Buy an item from the shop"""

    if item_id in item_data:
        item = item_data[item_id]
    else:
        item = item_data

    if "cost" not in item:
        cost = 0
    else:
        cost = item["cost"]

    if "gold" not in character:
        character["gold"] = 0

    if character["gold"] < cost:
        raise InsufficientResourcesError("Not enough gold")

    if "inventory" not in character:
        character["inventory"] = []

    if len(character["inventory"]) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory full")

    character["gold"] -= cost
    character["inventory"].append(item_id)
    return True


def sell_item(character, item_id, item_data):
    """Sell an item for half price"""

    if "inventory" not in character or item_id not in character["inventory"]:
        raise ItemNotFoundError("Item not in inventory")

    if item_id in item_data:
        item = item_data[item_id]
    else:
        item = item_data

    if "cost" not in item:
        sell_price = 0
    else:
        sell_price = item["cost"] // 2

    character["inventory"].remove(item_id)

    if "gold" not in character:
        character["gold"] = 0

    character["gold"] += sell_price
    return sell_price

# ============================================================================ 
# HELPERS
# ============================================================================

def parse_item_effect(effect_string):
    """Parse 'stat:value' string into stat and integer value"""
    parts = effect_string.split(":")
    return parts[0], int(parts[1])


def apply_stat_effect(character, stat_name, value):
    """Apply item effect to character"""
    if stat_name not in character:
        character[stat_name] = 0
    character[stat_name] += value

    if "health" in character and "max_health" in character:
        if stat_name == "health" and character["health"] > character["max_health"]:
            character["health"] = character["max_health"]


def display_inventory(character, item_data_dict):
    """Print inventory contents"""
    if "inventory" not in character:
        character["inventory"] = []

    inventory = character["inventory"]
    if len(inventory) == 0:
        print("Inventory is empty")
        return

    counts = {}
    for item in inventory:
        if item not in counts:
            counts[item] = 0
        counts[item] += 1

    print("=== Inventory ===")
    for item_id, qty in counts.items():
        if item_id in item_data_dict:
            item_info = item_data_dict[item_id]
            name = item_info["name"] if "name" in item_info else item_id
            type_ = item_info["type"] if "type" in item_info else "unknown"
        else:
            name = item_id
            type_ = "unknown"
        print(f"{name} ({type_}) x{qty}")