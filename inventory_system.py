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
    return "inventory" in character and item_id in character["inventory"]


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
    removed_items = character.get("inventory", [])
    character["inventory"] = []
    return removed_items

# --------------------------
# ITEM USAGE
# --------------------------

def use_item(character, item_id, item_data):
    """Use a consumable item"""
    if item_id not in character.get("inventory", []):
        raise ItemNotFoundError(f"{item_id} not in inventory.")

    item = item_data[item_id]
    if item["type"] != "consumable":
        raise InvalidItemTypeError(f"{item_id} cannot be used directly.")

    stat, value = parse_item_effect(item["effect"])
    apply_stat_effect(character, stat, value)
    character["inventory"].remove(item_id)
    return f"Used {item['name']}, {stat} increased by {value}."


def equip_weapon(character, item_id, item_data):
    """Equip a weapon"""
    if item_id not in character.get("inventory", []):
        raise ItemNotFoundError(f"{item_id} not in inventory.")

    item = item_data[item_id]
    if item["type"] != "weapon":
        raise InvalidItemTypeError(f"{item_id} is not a weapon.")

    if character.get("equipped_weapon"):
        unequip_weapon(character)

    stat, value = parse_item_effect(item["effect"])
    character[stat] += value
    character["equipped_weapon"] = item_id
    character["equipped_weapon_effect"] = item["effect"]
    character["inventory"].remove(item_id)
    return f"{character['name']} equipped {item['name']} (+{value} {stat})."


def equip_armor(character, item_id, item_data):
    """Equip armor"""
    if item_id not in character.get("inventory", []):
        raise ItemNotFoundError(f"{item_id} not in inventory.")

    item = item_data[item_id]
    if item["type"] != "armor":
        raise InvalidItemTypeError(f"{item_id} is not armor.")

    if character.get("equipped_armor"):
        unequip_armor(character)

    stat, value = parse_item_effect(item["effect"])
    character[stat] += value
    character["equipped_armor"] = item_id
    character["equipped_armor_effect"] = item["effect"]
    character["inventory"].remove(item_id)
    return f"{character['name']} equipped {item['name']} (+{value} {stat})."


def unequip_weapon(character):
    """Unequip current weapon"""
    if not character.get("equipped_weapon"):
        return None

    weapon_id = character["equipped_weapon"]
    stat, value = parse_item_effect(character["equipped_weapon_effect"])
    character[stat] -= value

    if len(character.get("inventory", [])) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory is full.")

    character.setdefault("inventory", []).append(weapon_id)
    character["equipped_weapon"] = None
    character["equipped_weapon_effect"] = None
    return weapon_id


def unequip_armor(character):
    """Unequip current armor"""
    if not character.get("equipped_armor"):
        return None

    armor_id = character["equipped_armor"]
    stat, value = parse_item_effect(character["equipped_armor_effect"])
    character[stat] -= value

    if len(character.get("inventory", [])) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory is full.")

    character.setdefault("inventory", []).append(armor_id)
    character["equipped_armor"] = None
    character["equipped_armor_effect"] = None
    return armor_id

# --------------------------
# SHOP SYSTEM
# --------------------------

def purchase_item(character, item_id, item_data):
    """Buy an item from the shop"""
    cost = item_data[item_id]["cost"]

    if character["gold"] < cost:
        raise InsufficientResourcesError("Not enough gold")

    if len(character.get("inventory", [])) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory full")

    character["gold"] -= cost
    character.setdefault("inventory", []).append(item_id)
    return True


def sell_item(character, item_id, item_data):
    """Sell an item for half price"""
    if item_id not in character.get("inventory", []):
        raise ItemNotFoundError("Item not in inventory")

    sell_price = item_data[item_id]["cost"] // 2
    character["inventory"].remove(item_id)
    character["gold"] += sell_price
    return sell_price

# --------------------------
# HELPERS
# --------------------------

def parse_item_effect(effect_string):
    """Parse 'stat:value' string into stat and integer value"""
    stat_name, value = effect_string.split(":")
    return stat_name, int(value)


def apply_stat_effect(character, stat_name, value):
    """Apply item effect to character"""
    character[stat_name] = character.get(stat_name, 0) + value
    if stat_name == "health" and character["health"] > character["max_health"]:
        character["health"] = character["max_health"]


def display_inventory(character, item_data_dict):
    """Print inventory contents"""
    inventory = character.get("inventory", [])
    if not inventory:
        print("Inventory is empty")
        return

    counts = {}
    for item in inventory:
        counts[item] = counts.get(item, 0) + 1

    print("=== Inventory ===")
    for item_id, qty in counts.items():
        item_info = item_data_dict[item_id]
        print(f"{item_info['name']} ({item_info['type']}) x{qty}")