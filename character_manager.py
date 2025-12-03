"""
COMP 163 - Project 3: Quest Chronicles
Character Manager Module - Starter Code

Name: [Your Name Here]

AI Usage: [Document any AI assistance used]

This module handles character creation, loading, and saving.
"""

import os
from custom_exceptions import (
    InvalidCharacterClassError,
    CharacterNotFoundError,
    SaveFileCorruptedError,
    InvalidSaveDataError,
    CharacterDeadError
)

# ============================================================================
# CHARACTER MANAGEMENT FUNCTIONS
# ============================================================================
def create_character(name, character_class):
    stats_classes = {
        "Warrior": {"health": 120, "strength": 15, "magic": 3},
        "Mage": {"health": 80, "strength": 5, "magic": 20},
        "Rogue": {"health": 100, "strength": 12, "magic": 8},
        "Cleric": {"health": 90, "strength": 8, "magic": 15}  # Added Cleric
    }

    # Check if the class exists
    if character_class not in stats_classes:
        raise InvalidCharacterClassError(f"Invalid class: {character_class}")

    stats = stats_classes[character_class]
    DEFAULT_STARTING_GOLD = 100  
    character = {
        "name": name,
        "class": character_class,
        "level": 1,
        "health": stats["health"],
        "max_health": stats["health"],
        "strength": stats["strength"],
        "magic": stats["magic"],
        "experience": 0,
        "gold": DEFAULT_STARTING_GOLD,
        "inventory": [],
        "active_quests": [],
        "completed_quests": []
    }

    return character

def save_character(character, save_directory="data/save_games"):
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    file_path = os.path.join(save_directory, f"{character['name']}.txt")

    inventory_csv = ",".join(character["inventory"])
    active_csv = ",".join(character["active_quests"])
    completed_csv = ",".join(character["completed_quests"])

    try:
        with open(file_path, "w") as f:
            f.write(f"NAME: {character['name']}\n")
            f.write(f"CLASS: {character['class']}\n")
            f.write(f"LEVEL: {character['level']}\n")
            f.write(f"HEALTH: {character['health']}\n")
            f.write(f"MAX_HEALTH: {character['max_health']}\n")
            f.write(f"STRENGTH: {character['strength']}\n")
            f.write(f"MAGIC: {character['magic']}\n")
            f.write(f"EXPERIENCE: {character['experience']}\n")
            f.write(f"GOLD: {character['gold']}\n")
            f.write(f"INVENTORY: {inventory_csv}\n")
            f.write(f"ACTIVE_QUESTS: {active_csv}\n")
            f.write(f"COMPLETED_QUESTS: {completed_csv}\n")
    except Exception as e:
        raise SaveFileCorruptedError(f"Failed to save character: {e}")

    return True
# ==========================
def load_character(character_name, save_directory="data/save_games"):
    file_path = os.path.join(save_directory, f"{character_name}.txt")

    if not os.path.exists(file_path):
        raise CharacterNotFoundError(f"Save file '{file_path}' not found.")

    try:
        with open(file_path, "r") as f:
            lines = f.readlines()
    except Exception as e:
        raise SaveFileCorruptedError(f"Cannot read save file: {e}")

    character = {}
    for line in lines:
        if ":" not in line:
            continue
        key_name, key_value = line.split(":", 1)
        key_name, key_value = key_name.strip(), key_value.strip()
        key_lower = key_name.lower()

        if key_lower in ["level","health","max_health","strength","magic","experience","gold"]:
            try:
                character[key_lower] = int(key_value)
            except:
                raise InvalidSaveDataError(f"{key_name} must be an integer")
        elif key_lower in ["inventory","active_quests","completed_quests"]:
            character[key_lower] = [item.strip() for item in key_value.split(",")] if key_value else []
        else:
            character[key_lower] = key_value

    return character

# ==========================
def list_saved_characters(save_directory="data/save_games"):
    if not os.path.exists(save_directory):
        return []
    return [f[:-4] for f in os.listdir(save_directory) if f.endswith(".txt")]

# ==========================
def delete_character(character_name, save_directory="data/save_games"):
    file_path = os.path.join(save_directory, f"{character_name}.txt")
    if not os.path.exists(file_path):
        raise CharacterNotFoundError(f"Save file '{file_path}' not found.")
    os.remove(file_path)
    return True

# ==========================
def gain_experience(character, xp_amount):
    if character['health'] <= 0:
        raise CharacterDeadError("Character has died")
    character['experience'] += xp_amount
    while character['experience'] >= character['level'] * 100:
        character['experience'] -= character['level'] * 100
        character['level'] += 1
        character['max_health'] += 10
        character['strength'] += 2
        character['magic'] += 2
        character['health'] = character['max_health']
    return True

# ==========================
def add_gold(character, amount):
    new_gold = character['gold'] + amount
    if new_gold < 0:
        raise ValueError("Not enough gold!")
    character['gold'] = new_gold
    return character['gold']

# ==========================
def heal_character(character, amount):
    actual_heal = min(amount, character['max_health'] - character['health'])
    character['health'] += actual_heal
    return actual_heal

# ==========================
def is_character_dead(character):
    return character['health'] <= 0

# ==========================
def revive_character(character):
    if character['health'] <= 0:
        character['health'] = character['max_health'] // 2
        return True
    return False

# ==========================
def validate_character_data(character):
    required = {
        "name": str, "class": str, "level": int, "health": int, "max_health": int,
        "strength": int, "magic": int, "experience": int, "gold": int,
        "inventory": list, "active_quests": list, "completed_quests": list
    }
    for key, typ in required.items():
        if key not in character:
            raise InvalidSaveDataError(f"Missing {key}")
        if not isinstance(character[key], typ):
            raise InvalidSaveDataError(f"{key} must be {typ}")
    return True

if __name__ == "__main__":
    print("=== CHARACTER MANAGER TEST ===")
    
    # Test character creation
    try:
        char = create_character("TestHero", "Warrior")
        print(f"Created: {char['name']} the {char['class']}")
        print(f"Stats: HP={char['health']}, STR={char['strength']}, MAG={char['magic']}")
    except InvalidCharacterClassError as e:
        print(f"Invalid class: {e}")
    
    # Test saving
    try:
        save_character(char)
        print("Character saved successfully")
    except Exception as e:
        print(f"Save error: {e}")
    
    # Test loading
    try:
        loaded = load_character("TestHero")
        print(f"Loaded: {loaded['name']}")
    except CharacterNotFoundError:
        print("Character not found")
    except SaveFileCorruptedError:
        print("Save file corrupted")