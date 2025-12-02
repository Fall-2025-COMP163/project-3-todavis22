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
            validate_quest_data(quest_data)
            quests[quest_data['quest_id']] = quest_data
        except InvalidDataFormatError as e:
            raise e
        except Exception:
            raise CorruptedDataError("Quest block is corrupted")
    return quests

def load_items(filename="data/items.txt"):
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
            validate_item_data(item_data)
            items[item_data['item_id']] = item_data
        except InvalidDataFormatError as e:
            raise e
        except Exception:
            raise CorruptedDataError("Item block is corrupted")
    return items

def validate_quest_data(quest_dict):
    required_keys = [
        "quest_id", "title", "description", 
        "reward_xp", "reward_gold", "required_level", "prerequisite"
    ]
    for key in required_keys:
        if key not in quest_dict:
            raise InvalidDataFormatError(f"Missing required field: {key}")
    try:
        quest_dict["reward_xp"] = int(quest_dict["reward_xp"])
        quest_dict["reward_gold"] = int(quest_dict["reward_gold"])
        quest_dict["required_level"] = int(quest_dict["required_level"])
    except ValueError:
        raise InvalidDataFormatError("Numeric fields must be integers")
    return True

def validate_item_data(item_dict):
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
    os.makedirs("data", exist_ok=True)
    quests_file = "data/quests.txt"
    items_file = "data/items.txt"

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

# ==========================
# PARSING FUNCTIONS
# ==========================
def parse_quest_block(lines):
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
        if "quest_id" not in quest:
            raise InvalidDataFormatError("Missing quest_id")
    except Exception as e:
        raise InvalidDataFormatError(f"Error parsing quest: {e}")
    return quest

def parse_item_block(lines):
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

# ==========================
# QUEST SYSTEM FUNCTIONS
# ==========================
def accept_quest(character, quest_id, quest_data_dict):
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError(f"Quest '{quest_id}' not found")
    quest = quest_data_dict[quest_id]

    if "completed_quests" not in character:
        character["completed_quests"] = []
    if "active_quests" not in character:
        character["active_quests"] = []

    if quest_id in character["completed_quests"]:
        raise QuestAlreadyCompletedError(f"Quest '{quest_id}' already completed")
    if quest_id in character["active_quests"]:
        raise QuestAlreadyCompletedError(f"Quest '{quest_id}' already active")
    if character["level"] < quest["required_level"]:
        raise InsufficientLevelError("Character level too low")

    prereq = quest["prerequisite"]
    if prereq != "NONE" and prereq not in character["completed_quests"]:
        raise QuestRequirementsNotMetError(f"Prerequisite '{prereq}' not completed")

    character["active_quests"].append(quest_id)
    return True

def complete_quest(character, quest_id, quest_data_dict):
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError(f"Quest '{quest_id}' not found")
    if "active_quests" not in character:
        character["active_quests"] = []
    if "completed_quests" not in character:
        character["completed_quests"] = []
    if quest_id not in character["active_quests"]:
        raise QuestNotActiveError(f"Quest '{quest_id}' not active")

    quest = quest_data_dict[quest_id]
    character["active_quests"].remove(quest_id)
    character["completed_quests"].append(quest_id)

    if "xp" not in character:
        character["xp"] = 0
    if "gold" not in character:
        character["gold"] = 0

    character["xp"] += quest["reward_xp"]
    character["gold"] += quest["reward_gold"]

    return {"xp": quest["reward_xp"], "gold": quest["reward_gold"]}

def abandon_quest(character, quest_id):
    if "active_quests" not in character:
        character["active_quests"] = []
    if quest_id not in character["active_quests"]:
        raise QuestNotActiveError(f"Quest '{quest_id}' not active")
    character["active_quests"].remove(quest_id)
    return True

def get_active_quests(character, quest_data_dict):
    if "active_quests" not in character:
        character["active_quests"] = []
    quests = []
    for qid in character["active_quests"]:
        if qid in quest_data_dict:
            quests.append(quest_data_dict[qid])
    return quests

def get_completed_quests(character, quest_data_dict):
    if "completed_quests" not in character:
        character["completed_quests"] = []
    quests = []
    for qid in character["completed_quests"]:
        if qid in quest_data_dict:
            quests.append(quest_data_dict[qid])
    return quests

def get_available_quests(character, quest_data_dict):
    if "active_quests" not in character:
        character["active_quests"] = []
    if "completed_quests" not in character:
        character["completed_quests"] = []
    available = []
    for quest_id in quest_data_dict:
        quest = quest_data_dict[quest_id]
        if quest_id in character["completed_quests"]:
            continue
        if quest_id in character["active_quests"]:
            continue
        if character["level"] < quest["required_level"]:
            continue
        prereq = quest["prerequisite"]
        if prereq != "NONE" and prereq not in character["completed_quests"]:
            continue
        available.append(quest)
    return available

def can_accept_quest(character, quest_id, quest_data_dict):
    if quest_id not in quest_data_dict:
        return False
    quest = quest_data_dict[quest_id]

    if "active_quests" not in character:
        character["active_quests"] = []
    if "completed_quests" not in character:
        character["completed_quests"] = []

    if quest_id in character["completed_quests"]:
        return False
    if quest_id in character["active_quests"]:
        return False
    if character["level"] < quest["required_level"]:
        return False
    prereq = quest["prerequisite"]
    if prereq != "NONE" and prereq not in character["completed_quests"]:
        return False
    return True

def get_quest_prerequisite_chain(quest_id, quest_data_dict):
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError(f"Quest '{quest_id}' not found")
    chain = []
    current = quest_id
    while current != "NONE":
        chain.insert(0, current)
        current = quest_data_dict[current]["prerequisite"]
        if current != "NONE" and current not in quest_data_dict:
            raise QuestNotFoundError(f"Prerequisite '{current}' not found")
    return chain

def get_quest_completion_percentage(character, quest_data_dict):
    total = len(quest_data_dict)
    if total == 0:
        return 0.0
    completed = len(character["completed_quests"]) if "completed_quests" in character else 0
    return (completed / total) * 100

def get_total_quest_rewards_earned(character, quest_data_dict):
    total_xp = 0
    total_gold = 0
    if "completed_quests" in character:
        for qid in character["completed_quests"]:
            if qid in quest_data_dict:
                quest = quest_data_dict[qid]
                total_xp += quest["reward_xp"]
                total_gold += quest["reward_gold"]
    return {"total_xp": total_xp, "total_gold": total_gold}

def get_quests_by_level(quest_data_dict, min_level, max_level):
    quests = []
    for qid in quest_data_dict:
        quest = quest_data_dict[qid]
        if min_level <= quest["required_level"] <= max_level:
            quests.append(quest)
    return quests

# ==========================
# TESTING
# ==========================
if __name__ == "__main__":
    print("=== GAME DATA MODULE TEST ===")
    create_default_data_files()

    try:
        quests = load_quests()
        print(f"Loaded {len(quests)} quests")
    except MissingDataFileError:
        print("Quest file not found")
    except InvalidDataFormatError as e:
        print(f"Invalid quest format: {e}")

    try:
        items = load_items()
        print(f"Loaded {len(items)} items")
    except MissingDataFileError:
        print("Item file not found")
    except InvalidDataFormatError as e:
        print(f"Invalid item format: {e}")