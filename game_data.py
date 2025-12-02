"""
COMP 163 - Project 3: Quest Chronicles
Game Data Module - Starter Code

Name: [Your Name Here]

AI Usage: [Document any AI assistance used]

This module handles loading and validating game data from text files.
"""

import os
from custom_exceptions import (
    InvalidDataFormatError,
    MissingDataFileError,
    CorruptedDataError
)

# ============================================================================
# DATA LOADING FUNCTIONS
# ============================================================================
def load_quests(filename="data/quests.txt"):
    """
    Load quest data from file
    
    Expected format per quest (separated by blank lines):
    QUEST_ID: unique_quest_name
    TITLE: Quest Display Title
    DESCRIPTION: Quest description text
    REWARD_XP: 100
    REWARD_GOLD: 50
    REQUIRED_LEVEL: 1
    PREREQUISITE: previous_quest_id (or NONE)
    
    Returns: Dictionary of quests {quest_id: quest_data_dict}
    Raises: MissingDataFileError, InvalidDataFormatError, CorruptedDataError
    """
    quests = {}
    
    try:
        with open(filename, "r") as f:
            content = f.read()
    except FileNotFoundError:
        raise MissingDataFileError(f"Quest file '{filename}' not found")
    except Exception as e:
        raise CorruptedDataError(f"Could not read quest file: {e}")
    
    quest_blocks = content.strip().split("\n\n")  # Each quest separated by blank lines
    
    for block in quest_blocks:
        lines = block.strip().split("\n")
        try:
            quest_data = parse_quest_block(lines)
            quests[quest_data['quest_id']] = quest_data
        except InvalidDataFormatError as e:
            raise e
        except Exception:
            raise CorruptedDataError("Quest block is corrupted")
    
    return quests


def load_items(filename="data/items.txt"):
    """
    Load item data from file
    
    Expected format per item (separated by blank lines):
    ITEM_ID: unique_item_name
    NAME: Item Display Name
    TYPE: weapon|armor|consumable
    EFFECT: stat_name:value (e.g., strength:5 or health:20)
    COST: 100
    DESCRIPTION: Item description
    
    Returns: Dictionary of items {item_id: item_data_dict}
    Raises: MissingDataFileError, InvalidDataFormatError, CorruptedDataError
    """
    items = {}
    
    try:
        with open(filename, "r") as f:
            content = f.read()
    except FileNotFoundError:
        raise MissingDataFileError(f"{filename} not found")
    except Exception as e:
        raise CorruptedDataError(f"Cannot read file: {e}")
    
    blocks = content.strip().split("\n\n")  # Each item separated by blank line
    
    for block in blocks:
        lines = block.strip().split("\n")
        try:
            item_data = parse_item_block(lines)
            items[item_data['item_id']] = item_data
        except InvalidDataFormatError as e:
            raise e
        except Exception:
            raise CorruptedDataError("Item block is corrupted")
    
    return items


def validate_quest_data(quest_dict):
    """
    Validate that quest dictionary has all required fields
    
    Required fields: quest_id, title, description, reward_xp, 
                    reward_gold, required_level, prerequisite
    
    Returns: True if valid
    Raises: InvalidDataFormatError if missing required fields
    """
    required_keys = [
        "quest_id", "title", "description", 
        "reward_xp", "reward_gold", "required_level", "prerequisite"
    ]
    
    for key in required_keys:
        if key not in quest_dict:
            raise InvalidDataFormatError(f"Missing required field: {key}")
    
    # Check numeric fields
    try:
        quest_dict["reward_xp"] = int(quest_dict["reward_xp"])
        quest_dict["reward_gold"] = int(quest_dict["reward_gold"])
        quest_dict["required_level"] = int(quest_dict["required_level"])
    except ValueError:
        raise InvalidDataFormatError("Numeric fields must be integers")
    
    return True


def validate_item_data(item_dict):
    """
    Validate that item dictionary has all required fields
    
    Required fields: item_id, name, type, effect, cost, description
    Valid types: weapon, armor, consumable
    
    Returns: True if valid
    Raises: InvalidDataFormatError if missing required fields or invalid type
    """
    required_keys = ["item_id", "name", "type", "effect", "cost", "description"]
    valid_types = ["weapon", "armor", "consumable"]
    
    for key in required_keys:
        if key not in item_dict:
            raise InvalidDataFormatError(f"Missing required field: {key}")
    
    if item_dict["type"].lower() not in valid_types:
        raise InvalidDataFormatError(f"Invalid item type: {item_dict['type']}")
    
    try:
        item_dict["cost"] = int(item_dict["cost"])
    except ValueError:
        raise InvalidDataFormatError("Cost must be an integer")
    
    return True


def create_default_data_files():
    """
    Create default data files if they don't exist
    This helps with initial setup and testing
    """
    os.makedirs("data", exist_ok=True)  # Create data/ folder if missing

    quests_file = "data/quests.txt"
    items_file = "data/items.txt"

    # Create default quests file if missing
    if not os.path.exists(quests_file):
        with open(quests_file, "w") as f:
            f.write(
                "QUEST_ID: quest_1\n"
                "TITLE: First Quest\n"
                "DESCRIPTION: Defeat 3 goblins\n"
                "REWARD_XP: 50\n"
                "REWARD_GOLD: 20\n"
                "REQUIRED_LEVEL: 1\n"
                "PREREQUISITE: NONE\n\n"
            )

    # Create default items file if missing
    if not os.path.exists(items_file):
        with open(items_file, "w") as f:
            f.write(
                "ITEM_ID: sword_1\n"
                "NAME: Wooden Sword\n"
                "TYPE: weapon\n"
                "EFFECT: strength:5\n"
                "COST: 10\n"
                "DESCRIPTION: A basic starter sword\n\n"
            )


def parse_quest_block(lines):
    """
    Parse a block of lines into a quest dictionary
    
    Args:
        lines: List of strings representing one quest
    
    Returns: Dictionary with quest data
    Raises: InvalidDataFormatError if parsing fails
    """
    quest = {}
    try:
        for line in lines:
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            key = key.strip().lower()
            value = value.strip()
            
            if key in ["reward_xp", "reward_gold", "required_level"]:
                value = int(value)
            
            quest[key] = value
        
        # Ensure quest_id exists
        if "quest_id" not in quest:
            raise InvalidDataFormatError("Missing quest_id")
    
    except Exception as e:
        raise InvalidDataFormatError(f"Error parsing quest: {e}")
    
    return quest


def parse_item_block(lines):
    """
    Parse a block of lines into an item dictionary
    
    Args:
        lines: List of strings representing one item
    
    Returns: Dictionary with item data
    Raises: InvalidDataFormatError if parsing fails
    """
    item = {}
    try:
        for line in lines:
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            key = key.strip().lower()
            value = value.strip()
            
            if key == "cost":
                value = int(value)
            
            item[key] = value
        
        if "item_id" not in item:
            raise InvalidDataFormatError("Missing item_id")
    
    except Exception as e:
        raise InvalidDataFormatError(f"Error parsing item: {e}")
    
    return item

# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== GAME DATA MODULE TEST ===")
    
    # Test creating default files
    # create_default_data_files()
    
    # Test loading quests
    try:
        quests = load_quests()
        print(f"Loaded {len(quests)} quests")
    except MissingDataFileError:
        print("Quest file not found")
    except InvalidDataFormatError as e:
        print(f"Invalid quest format: {e}")
    
    # Test loading items
    try:
        items = load_items()
        print(f"Loaded {len(items)} items")
    except MissingDataFileError:
        print("Item file not found")
    except InvalidDataFormatError as e:
        print(f"Invalid item format: {e}")

