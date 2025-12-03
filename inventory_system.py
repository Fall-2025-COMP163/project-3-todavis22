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
    """
    Add an item to character's inventory
    """
    # TODO: Implement adding items
    inventory = character.setdefault('inventory', [])
    if len(inventory) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Cannot add item, inventory is full.")
    inventory.append(item_id)  # Add item to inventory list
    return True


def remove_item_from_inventory(character, item_id):
    """
    Remove an item from character's inventory
    """
    # TODO: Implement item removal
    inventory = character.get('inventory', [])
    if item_id not in inventory:
        raise ItemNotFoundError(f"Item '{item_id}' not in inventory.")
    inventory.remove(item_id)  # Remove first occurrence
    return True


def has_item(character, item_id):
    """
    Check if character has a specific item
    """
    # TODO: Implement item check
    inventory = character.get('inventory', [])
    return item_id in inventory


def count_item(character, item_id):
    """
    Count how many of a specific item the character has
    """
    # TODO: Implement item counting
    inventory = character.get('inventory', [])
    return inventory.count(item_id)


def get_inventory_space_remaining(character):
    """
    Calculate how many more items can fit in inventory
    """
    # TODO: Implement space calculation
    inventory = character.get('inventory', [])
    return MAX_INVENTORY_SIZE - len(inventory)


def clear_inventory(character):
    """
    Remove all items from inventory
    """
    # TODO: Implement inventory clearing
    inventory = character.get('inventory', [])
    removed_items = inventory.copy()  # Save current items
    character['inventory'] = []       # Clear inventory
    return removed_items


# ============================================================================
# ITEM USAGE
# ============================================================================


def use_item(character, item_id, item_data):
    """
    Use a consumable item from inventory
    """
    # TODO: Implement item usage
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"Item '{item_id}' not in inventory.")
   
    if item_data['type'] != 'consumable':
        raise InvalidItemTypeError(f"Cannot use item type '{item_data['type']}'")
   
    # Parse effect
    stat, value = parse_item_effect(item_data['effect'])
    apply_stat_effect(character, stat, value)
   
    # Remove item after use
    remove_item_from_inventory(character, item_id)


    # FIXED: tests do NOT include item_data['name']
    return f"{character['name']} used {item_id} and {stat} changed by {value}."


def equip_weapon(character, item_id, item_data):
    """
    Equip a weapon
    """
    # TODO: Implement weapon equipping
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"Weapon '{item_id}' not in inventory.")
   
    if item_data['type'] != 'weapon':
        raise InvalidItemTypeError(f"Cannot equip item type '{item_data['type']}' as weapon.")
   
    # Unequip current weapon if exists
    if character.get('equipped_weapon'):
        unequip_weapon(character)
   
    # Apply weapon effect
    stat, value = parse_item_effect(item_data['effect'])
    apply_stat_effect(character, stat, value)
   
    # Store equipped weapon
    character['equipped_weapon'] = item_id
    remove_item_from_inventory(character, item_id)


    # FIXED: tests do NOT include item_data['name']
    return f"{character['name']} equipped weapon '{item_id}' (+{value} {stat})."


def equip_armor(character, item_id, item_data):
    """
    Equip armor
    """
    # TODO: Implement armor equipping
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"Armor '{item_id}' not in inventory.")
   
    if item_data['type'] != 'armor':
        raise InvalidItemTypeError(f"Cannot equip item type '{item_data['type']}' as armor.")
   
    # Unequip current armor if exists
    if character.get('equipped_armor'):
        unequip_armor(character)
   
    # Apply armor effect
    stat, value = parse_item_effect(item_data['effect'])
    apply_stat_effect(character, stat, value)
   
    # Store equipped armor
    character['equipped_armor'] = item_id
    remove_item_from_inventory(character, item_id)


    # FIXED: tests do NOT include item_data['name']
    return f"{character['name']} equipped armor '{item_id}' (+{value} {stat})."


def unequip_weapon(character):
    """
    Remove equipped weapon and return it to inventory
    """
    # TODO: Implement weapon unequipping
    weapon_id = character.get('equipped_weapon')
    if not weapon_id:
        return None  # Nothing equipped
   
    if get_inventory_space_remaining(character) <= 0:
        raise InventoryFullError("Cannot unequip weapon, inventory full.")
   
    character['equipped_weapon'] = None
    add_item_to_inventory(character, weapon_id)
    return weapon_id


def unequip_armor(character):
    """
    Remove equipped armor and return it to inventory
    """
    # TODO: Implement armor unequipping
    armor_id = character.get('equipped_armor')
    if not armor_id:
        return None
   
    if get_inventory_space_remaining(character) <= 0:
        raise InventoryFullError("Cannot unequip armor, inventory full.")
   
    character['equipped_armor'] = None
    add_item_to_inventory(character, armor_id)
    return armor_id


# ============================================================================
# SHOP SYSTEM
# ============================================================================


def purchase_item(character, item_id, item_data):
    """
    Purchase an item from a shop
    """
    # TODO: Implement purchasing
    if character.get('gold', 0) < item_data['cost']:
        raise InsufficientResourcesError(f"Not enough gold to buy {item_id}.")
   
    if get_inventory_space_remaining(character) <= 0:
        raise InventoryFullError("Cannot purchase item, inventory full.")
   
    character['gold'] -= item_data['cost']
    add_item_to_inventory(character, item_id)
    return True


def sell_item(character, item_id, item_data):
    """
    Sell an item for half its purchase cost
    """
    # TODO: Implement selling
    if not has_item(character, item_id):
        raise ItemNotFoundError(f"Cannot sell '{item_id}', not in inventory.")
   
    sell_price = item_data['cost'] // 2
    character['gold'] = character.get('gold', 0) + sell_price
    remove_item_from_inventory(character, item_id)
    return sell_price


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def parse_item_effect(effect_string):
    """
    Parse item effect string into stat name and value
    """
    # TODO: Implement effect parsing
    try:
        stat_name, value = effect_string.split(":")
        return stat_name.strip(), int(value.strip())
    except Exception as e:
        raise InvalidItemTypeError(f"Invalid effect format '{effect_string}': {e}")


def apply_stat_effect(character, stat_name, value):
    """
    Apply a stat modification to character
    """
    # TODO: Implement stat application
    if stat_name not in character:
        character[stat_name] = 0
   
    if stat_name == "health":
        character['health'] = min(
            character.get('max_health', character['health']),
            character.get('health', 0) + value
        )
    elif stat_name == "max_health":
        character['max_health'] = character.get('max_health', 0) + value
        character['health'] = min(character['health'], character['max_health'])
    else:
        character[stat_name] = character.get(stat_name, 0) + value


def display_inventory(character, item_data_dict):
    """
    Display character's inventory in formatted way
    """
    # TODO: Implement inventory display
    inventory = character.get('inventory', [])
    counted = {}
    for item_id in inventory:
        counted[item_id] = counted.get(item_id, 0) + 1
   
    print(f"{character['name']}'s Inventory:")
    for item_id, qty in counted.items():
        item_name = item_data_dict.get(item_id, {}).get('name', item_id)
        item_type = item_data_dict.get(item_id, {}).get('type', "unknown")
        print(f"- {item_name} ({item_type}) x{qty}")


# ============================================================================
# TESTING
# ============================================================================


if __name__ == "__main__":
    print("=== INVENTORY SYSTEM TEST ===")
   
    test_char = {'name': 'Hero', 'inventory': [], 'gold': 100, 'health': 80, 'max_health': 80, 'strength': 10}
   
    test_item = {'item_id': 'health_potion', 'name': 'Health Potion', 'type': 'consumable', 'effect': 'health:20', 'cost': 20}
    test_weapon = {'item_id': 'sword_001', 'name': 'Iron Sword', 'type': 'weapon', 'effect': 'strength:5', 'cost': 50}
   
    add_item_to_inventory(test_char, 'health_potion')
    print(f"Inventory after adding item: {test_char['inventory']}")
   
    print(use_item(test_char, 'health_potion', test_item))
   
    add_item_to_inventory(test_char, 'sword_001')
    print(equip_weapon(test_char, 'sword_001', test_weapon))
   
    display_inventory(test_char, {'health_potion': test_item, 'sword_001': test_weapon})
