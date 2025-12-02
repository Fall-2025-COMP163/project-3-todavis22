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
    import os

    if not os.path.exists(filename):
        raise MissingDataFileError(f"Quest file not found: {filename}")

    quests = {}
    try:
        with open(filename, "r") as f:
            lines = f.read().splitlines()

        current_quest = {}
        for line in lines + [""]:
            line = line.strip()
            if line == "":
                if current_quest:
                    required_fields = ["QUEST_ID", "TITLE", "DESCRIPTION",
                                       "REWARD_XP", "REWARD_GOLD", "REQUIRED_LEVEL", "PREREQUISITE"]
                    for field in required_fields:
                        if field not in current_quest:
                            raise InvalidDataFormatError(f"Missing field '{field}' in quest")
                    quest_id = current_quest["QUEST_ID"]
                    # Normalize keys to lowercase (should match test case calls)
                    normalized_quest = {k.lower(): v for k, v in current_quest.items()}
                    quests[quest_id] = normalized_quest
                    current_quest = {}
                continue

            if ": " not in line:
                raise InvalidDataFormatError(f"Invalid line format: {line}")  # Custom exception

            key, value = line.split(": ", 1)
            key = key.strip()
            value = value.strip()
            if key in ["REWARD_XP", "REWARD_GOLD", "REQUIRED_LEVEL"]:
                try:
                    value = int(value)
                except ValueError:
                    raise InvalidDataFormatError(f"Expected integer for {key}, got '{value}'")
            current_quest[key] = value

    except InvalidDataFormatError:
        raise
    except Exception as e:
        raise CorruptedDataError(f"Could not read quest file: {e}")

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
    import os

    if not os.path.exists(filename):
        raise MissingDataFileError(f"Item file not found: {filename}")

    items = {}
    try:
        with open(filename, "r") as f:
            lines = f.read().splitlines()

        current_item = {}
        for line in lines + [""]:
            line = line.strip()
            if line == "":
                if current_item:
                    required_fields = ["ITEM_ID", "NAME", "TYPE", "EFFECT", "COST", "DESCRIPTION"]
                    for field in required_fields:
                        if field not in current_item:
                            raise InvalidDataFormatError(f"Missing field '{field}' in item")
                    item_id = current_item["ITEM_ID"]
                    # Normalize keys to lowercase
                    normalized_item = {k.lower(): v for k, v in current_item.items()}
                    items[item_id] = normalized_item
                    current_item = {}
                continue

            if ": " not in line:
