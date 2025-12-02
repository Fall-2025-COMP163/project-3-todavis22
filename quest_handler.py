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
        f = open(filename, "r")
        content = f.read()
        f.close()
    except FileNotFoundError:
        raise MissingDataFileError(f"Quest file '{filename}' not found")
    except Exception as e:
        raise CorruptedDataError(f"Could not read quest file: {e}")

    quest_blocks = content.strip().split("\n\n")
    for block in quest_blocks:
        lines = block.strip().split("\n")
        quest_data = parse_quest_block(lines)
        quests[quest_data["quest_id"]] = quest_data

    return quests

def parse_quest_block(lines):
    quest = {}
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
    if "prerequisite" not in quest:
        quest["prerequisite"] = "NONE"
    return quest

# -------------------
# Quest operations
# -------------------

def accept_quest(character, quest_id, quest_data_dict):
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError(f"Quest '{quest_id}' not found")

    if "active_quests" not in character:
        character["active_quests"] = []
    if "completed_quests" not in character:
        character["completed_quests"] = []

    if quest_id in character["completed_quests"]:
        raise QuestAlreadyCompletedError(f"Quest '{quest_id}' already completed")
    if quest_id in character["active_quests"]:
        raise QuestAlreadyCompletedError(f"Quest '{quest_id}' already active")

    quest = quest_data_dict[quest_id]

    if character["level"] < quest["required_level"]:
        raise InsufficientLevelError("Character level too low")

    prereq = quest["prerequisite"]
    if prereq != "NONE":
        prereq_met = False
        for q in character["completed_quests"]:
            if q == prereq:
                prereq_met = True
        if not prereq_met:
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

    if "experience" not in character:
        character["experience"] = 0
    if "gold" not in character:
        character["gold"] = 0

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
    for qid in quest_data_dict:
        quest = quest_data_dict[qid]
        if qid in character["active_quests"]:
            continue
        if qid in character["completed_quests"]:
            continue
        if character["level"] < quest["required_level"]:
            continue
        prereq = quest["prerequisite"]
        prereq_met = True
        if prereq != "NONE":
            prereq_met = False
            for q in character["completed_quests"]:
                if q == prereq:
                    prereq_met = True
        if not prereq_met:
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

    if quest_id in character["active_quests"]:
        return False
    if quest_id in character["completed_quests"]:
        return False
    if character["level"] < quest["required_level"]:
        return False

    prereq = quest["prerequisite"]
    if prereq != "NONE":
        prereq_met = False
        for q in character["completed_quests"]:
            if q == prereq:
                prereq_met = True
        if not prereq_met:
            return False

    return True

def get_quest_prerequisite_chain(quest_id, quest_data_dict):
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError(f"Quest '{quest_id}' not found")

    chain = []
    current = quest_id
    while current != "NONE":
        chain.append(current)
        prereq = quest_data_dict[current]["prerequisite"]
        if prereq != "NONE" and prereq not in quest_data_dict:
            raise QuestNotFoundError(f"Prerequisite '{prereq}' not found")
        current = prereq
    chain.reverse()
    return chain

def get_quest_completion_percentage(character, quest_data_dict):
    total = 0
    for _ in quest_data_dict:
        total += 1
    if total == 0:
        return 0.0
    completed = 0
    if "completed_quests" in character:
        for _ in character["completed_quests"]:
            completed += 1
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
    for qid in quest_data_dict:
        quest = quest_data_dict[qid]
        if min_level <= quest["required_level"] <= max_level:
            result.append(quest)
    return result