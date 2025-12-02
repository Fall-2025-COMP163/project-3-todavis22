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
    if "inventory" not in character:
        character["inventory"] = []
    if len(character["inventory"]) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory is full!")
    character["inventory"].append(item_id)
    return True

def remove_item_from_inventory(character, item_id):
    if "inventory" not in character or item_id not in character["inventory"]:
        raise ItemNotFoundError(f"Item '{item_id}' not found in inventory")
    character["inventory"].remove(item_id)
    return True

def has_item(character, item_id):
    if "inventory" not in character:
        return False
    return item_id in character["inventory"]

def count_item(character, item_id):
    if "inventory" not in character:
        return 0
    return character["inventory"].count(item_id)

def get_inventory_space_remaining(character):
    if "inventory" not in character:
        return MAX_INVENTORY_SIZE
    return MAX_INVENTORY_SIZE - len(character["inventory"])

def clear_inventory(character):
    if "inventory" not in character:
        character["inventory"] = []
        return []
    removed_items = character["inventory"]
    character["inventory"] = []
    return removed_items

# -------------------
# Item Usage / Equip
# -------------------

def parse_item_effect(effect_string):
    stat, value = effect_string.split(":")
    return stat, int(value)

def apply_stat_effect(character, stat, value):
    if stat not in character:
        character[stat] = 0
    character[stat] += value
    if stat == "health" and "max_health" in character and character["health"] > character["max_health"]:
        character["health"] = character["max_health"]

def use_item(character, item_id, item_data_dict):
    if "inventory" not in character or item_id not in character["inventory"]:
        raise ItemNotFoundError(f"{item_id} not in inventory")
    item = item_data_dict[item_id]
    if item["type"] != "consumable":
        raise InvalidItemTypeError(f"{item_id} cannot be used")
    stat, value = parse_item_effect(item["effect"])
    apply_stat_effect(character, stat, value)
    character["inventory"].remove(item_id)
    return f"Used {item['name']} (+{value} {stat})"

def equip_weapon(character, item_id, item_data_dict):
    if "inventory" not in character or item_id not in character["inventory"]:
        raise ItemNotFoundError(f"{item_id} not in inventory")
    item = item_data_dict[item_id]
    if item["type"] != "weapon":
        raise InvalidItemTypeError(f"{item_id} not a weapon")
    if "equipped_weapon" in character and character["equipped_weapon"] is not None:
        unequip_weapon(character)
    stat, value = parse_item_effect(item["effect"])
    if stat not in character:
        character[stat] = 0
    character[stat] += value
    character["equipped_weapon"] = item_id
    character["equipped_weapon_effect"] = item["effect"]
    character["inventory"].remove(item_id)
    return f"{character['name']} equipped {item['name']} (+{value} {stat})"

def unequip_weapon(character):
    if "equipped_weapon" not in character or character["equipped_weapon"] is None:
        return None
    item_id = character["equipped_weapon"]
    stat, value = parse_item_effect(character["equipped_weapon_effect"])
    character[stat] -= value
    if "inventory" not in character:
        character["inventory"] = []
    if len(character["inventory"]) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory full")
    character["inventory"].append(item_id)
    character["equipped_weapon"] = None
    character["equipped_weapon_effect"] = None
    return item_id

def equip_armor(character, item_id, item_data_dict):
    if "inventory" not in character or item_id not in character["inventory"]:
        raise ItemNotFoundError(f"{item_id} not in inventory")
    item = item_data_dict[item_id]
    if item["type"] != "armor":
        raise InvalidItemTypeError(f"{item_id} not armor")
    if "equipped_armor" in character and character["equipped_armor"] is not None:
        unequip_armor(character)
    stat, value = parse_item_effect(item["effect"])
    if stat not in character:
        character[stat] = 0
    character[stat] += value
    character["equipped_armor"] = item_id
    character["equipped_armor_effect"] = item["effect"]
    character["inventory"].remove(item_id)
    return f"{character['name']} equipped {item['name']} (+{value} {stat})"

def unequip_armor(character):
    if "equipped_armor" not in character or character["equipped_armor"] is None:
        return None
    item_id = character["equipped_armor"]
    stat, value = parse_item_effect(character["equipped_armor_effect"])
    character[stat] -= value
    if "inventory" not in character:
        character["inventory"] = []
    if len(character["inventory"]) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory full")
    character["inventory"].append(item_id)
    character["equipped_armor"] = None
    character["equipped_armor_effect"] = None
    return item_id

# -------------------
# Shop
# -------------------

def purchase_item(character, item_id, item_data_dict):
    if "inventory" not in character:
        character["inventory"] = []
    if "gold" not in character:
        character["gold"] = 0
    item = item_data_dict[item_id]
    cost = item["cost"] if "cost" in item else 0
    if character["gold"] < cost:
        raise InsufficientResourcesError("Not enough gold")
    if len(character["inventory"]) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory full")
    character["gold"] -= cost
    character["inventory"].append(item_id)
    return True

def sell_item(character, item_id, item_data_dict):
    if "inventory" not in character or item_id not in character["inventory"]:
        raise ItemNotFoundError("Item not in inventory")
    item = item_data_dict[item_id]
    sell_price = item["cost"] // 2 if "cost" in item else 0
    character["inventory"].remove(item_id)
    if "gold" not in character:
        character["gold"] = 0
    character["gold"] += sell_price
    return sell_price