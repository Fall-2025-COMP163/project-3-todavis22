"""
COMP 163 - Project 3: Quest Chronicles
Quest Handler Module - Starter Code

Name: [Your Name Here]

AI Usage: [Document any AI assistance used]

This module handles quest management, dependencies, and completion.
"""

from custom_exceptions import (
    QuestNotFoundError,
    QuestRequirementsNotMetError,
    QuestAlreadyCompletedError,
    QuestNotActiveError,
    InsufficientLevelError
)

# ============================================================================
# QUEST MANAGEMENT
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

    quest_blocks = content.strip().split("\n\n")
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
                try:
                    value = int(value)
                except ValueError:
                    raise InvalidDataFormatError(f"Invalid numeric value for {key}")
            quest[key] = value
        if "quest_id" not in quest:
            raise InvalidDataFormatError("Missing quest_id in quest block")
    except Exception as e:
        raise InvalidDataFormatError(f"Error parsing quest block: {e}")
    return quest

# ==========================
# QUEST FUNCTIONS
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

    if "completed_quests" not in character:
        character["completed_quests"] = []
    if "active_quests" not in character:
        character["active_quests"] = []

    if quest_id not in character["active_quests"]:
        raise QuestNotActiveError(f"Quest '{quest_id}' not active")

    quest = quest_data_dict[quest_id]
    character["active_quests"].remove(quest_id)
    character["completed_quests"].append(quest_id)

    # Ensure character has experience and gold keys
    if "experience" not in character:
        character["experience"] = 0
    if "gold" not in character:
        character["gold"] = 0

    # Update character rewards
    character["experience"] += quest["reward_xp"]
    character["gold"] += quest["reward_gold"]

    return {"experience": quest["reward_xp"], "gold": quest["reward_gold"]}

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
    result = []
    for qid in character["active_quests"]:
        if qid in quest_data_dict:
            result.append(quest_data_dict[qid])
    return result

def get_completed_quests(character, quest_data_dict):
    if "completed_quests" not in character:
        character["completed_quests"] = []
    result = []
    for qid in character["completed_quests"]:
        if qid in quest_data_dict:
            result.append(quest_data_dict[qid])
    return result

def get_available_quests(character, quest_data_dict):
    if "active_quests" not in character:
        character["active_quests"] = []
    if "completed_quests" not in character:
        character["completed_quests"] = []

    available = []
    for qid, quest in quest_data_dict.items():
        if qid in character["completed_quests"]:
            continue
        if qid in character["active_quests"]:
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

    if quest_id in character["completed_quests"] or quest_id in character["active_quests"]:
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
        chain.append(current)
        current = quest_data_dict[current]["prerequisite"]
        if current != "NONE" and current not in quest_data_dict:
            raise QuestNotFoundError(f"Prerequisite '{current}' not found")
    
    chain.reverse()  # reverse at the end instead of inserting at the front
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
                total_xp += quest_data_dict[qid]["reward_xp"]
                total_gold += quest_data_dict[qid]["reward_gold"]
    return {"total_xp": total_xp, "total_gold": total_gold}

def get_quests_by_level(quest_data_dict, min_level, max_level):
    result = []
    for q in quest_data_dict.values():
        if min_level <= q["required_level"] <= max_level:
            result.append(q)
    return result