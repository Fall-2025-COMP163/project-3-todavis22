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
    
    if character["level"] < quest.get("required_level", 1):
        raise InsufficientLevelError("Character level too low")
    
    prereq = quest.get("prerequisite", "NONE")
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
    
    if "xp" not in character:
        character["xp"] = 0
    if "gold" not in character:
        character["gold"] = 0

    character["xp"] += quest.get("reward_xp", 0)
    character["gold"] += quest.get("reward_gold", 0)
    
    return {"xp": quest.get("reward_xp", 0), "gold": quest.get("reward_gold", 0)}

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
    return [quest_data_dict[qid] for qid in character["active_quests"] if qid in quest_data_dict]

def get_completed_quests(character, quest_data_dict):
    if "completed_quests" not in character:
        character["completed_quests"] = []
    return [quest_data_dict[qid] for qid in character["completed_quests"] if qid in quest_data_dict]

def get_available_quests(character, quest_data_dict):
    if "active_quests" not in character:
        character["active_quests"] = []
    if "completed_quests" not in character:
        character["completed_quests"] = []

    available = []
    for quest_id, quest in quest_data_dict.items():
        if quest_id in character["completed_quests"]:
            continue
        if quest_id in character["active_quests"]:
            continue
        if character["level"] < quest.get("required_level", 0):
            continue
        prereq = quest.get("prerequisite", "NONE")
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
    if character["level"] < quest.get("required_level", 0):
        return False
    prereq = quest.get("prerequisite", "NONE")
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
        current = quest_data_dict[current].get("prerequisite", "NONE")
        if current != "NONE" and current not in quest_data_dict:
            raise QuestNotFoundError(f"Prerequisite '{current}' not found")
    return chain

def get_quest_completion_percentage(character, quest_data_dict):
    total = len(quest_data_dict)
    if total == 0:
        return 0.0
    completed = len(character.get("completed_quests", []))
    return (completed / total) * 100

def get_total_quest_rewards_earned(character, quest_data_dict):
    total_xp = 0
    total_gold = 0
    for qid in character.get("completed_quests", []):
        quest = quest_data_dict.get(qid)
        if quest:
            total_xp += quest.get("reward_xp", 0)
            total_gold += quest.get("reward_gold", 0)
    return {"total_xp": total_xp, "total_gold": total_gold}

def get_quests_by_level(quest_data_dict, min_level, max_level):
    return [q for q in quest_data_dict.values() if min_level <= q.get("required_level",0) <= max_level]