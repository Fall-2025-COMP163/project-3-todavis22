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
    """
    Accept a new quest

    Args:
        character: Character dictionary
        quest_id: Quest to accept
        quest_data_dict: Dictionary of all quest data

    Requirements to accept quest:
        - Character level >= quest required_level
        - Prerequisite quest completed (if any)
        - Quest not already completed
        - Quest not already active

    Returns: True if quest accepted
    Raises:
        QuestNotFoundError if quest_id not in quest_data_dict
        InsufficientLevelError if character level too low
        QuestRequirementsNotMetError if prerequisite not completed
        QuestAlreadyCompletedError if quest already done
    """
    # 1. Quest exists
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError(f"Quest '{quest_id}' does not exist.")

    quest = quest_data_dict[quest_id]

    # 2. Level requirement
    required_level = quest.get("required_level", 1)
    if character.get("level", 1) < required_level:
        raise InsufficientLevelError(
            f"Level {required_level} required to accept this quest."
        )

    # 3. Prerequisite requirement
    prereq = quest.get("prerequisite", "NONE")
    if prereq != "NONE" and prereq not in character["completed_quests"]:
        raise QuestRequirementsNotMetError(
            f"Prerequisite quest '{prereq}' not completed."
        )

    # 4. Not already completed
    if quest_id in character["completed_quests"]:
        raise QuestAlreadyCompletedError(
            f"Quest '{quest_id}' already completed."
        )

    # 5. Not already active
    if quest_id in character["active_quests"]:
        raise QuestRequirementsNotMetError(
            f"Quest '{quest_id}' is already active."
        )

    # 6. Accept quest
    character["active_quests"].append(quest_id)
    return True


def complete_quest(character, quest_id, quest_data_dict):
    """
    Complete an active quest and grant rewards

    Args:
        character: Character dictionary
        quest_id: Quest to complete
        quest_data_dict: Dictionary of all quest data

    Rewards:
        - Experience points (reward_xp)
        - Gold (reward_gold)

    Returns: Dictionary with reward information
    Raises:
        QuestNotFoundError if quest_id not in quest_data_dict
        QuestNotActiveError if quest not in active_quests
    """
    # 1. Quest exists
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError(f"Quest '{quest_id}' does not exist.")

    quest = quest_data_dict[quest_id]

    # 2. Must be active to complete
    if quest_id not in character["active_quests"]:
        raise QuestNotActiveError(
            f"Quest '{quest_id}' is not currently active."
        )

    # Remove from active, move to completed
    character["active_quests"].remove(quest_id)
    character["completed_quests"].append(quest_id)

    # Grant rewards
    xp = quest.get("reward_xp", 0)
    gold = quest.get("reward_gold", 0)

    # Use character manager systems
    from character_manager import gain_experience, add_gold
    gain_experience(character, xp)
    add_gold(character, gold)

    # Return what was awarded
    return {
        "quest_id": quest_id,
        "reward_xp": xp,
        "reward_gold": gold
    }


def abandon_quest(character, quest_id):
    """
    Remove a quest from active quests without completing it

    Returns: True if abandoned
    Raises: QuestNotActiveError if quest not active
    """
    if quest_id not in character["active_quests"]:
        raise QuestNotActiveError(
            f"Cannot abandon '{quest_id}' because it is not active."
        )

    character["active_quests"].remove(quest_id)
    return True


def get_active_quests(character, quest_data_dict):
    """
    Get full data for all active quests

    Returns: List of quest dictionaries for active quests
    """
    active_list = []

    for quest_id in character.get("active_quests", []):
        if quest_id in quest_data_dict:
            active_list.append(quest_data_dict[quest_id])

    return active_list


def get_completed_quests(character, quest_data_dict):
    """
    Get full data for all completed quests

    Returns: List of quest dictionaries for completed quests
    """
    completed_list = []

    for quest_id in character.get("completed_quests", []):
        if quest_id in quest_data_dict:
            completed_list.append(quest_data_dict[quest_id])

    return completed_list


def get_available_quests(character, quest_data_dict):
    """
    Get quests that character can currently accept

    Available = meets level req + prerequisite done + not completed + not active

    Returns: List of quest dictionaries
    """
    available = []
    level = character.get("level", 1)

    for quest_id, quest in quest_data_dict.items():
        required_level = quest.get("required_level", 1)
        prereq = quest.get("prerequisite", "NONE")

        # Skip if completed
        if quest_id in character["completed_quests"]:
            continue

        # Skip if already active
        if quest_id in character["active_quests"]:
            continue

        # Level requirement
        if level < required_level:
            continue

        # Prerequisite check
        if prereq != "NONE" and prereq not in character["completed_quests"]:
            continue

        # If all requirements met, it's available
        available.append(quest)

    return available


def is_quest_completed(character, quest_id):
    """Check if a specific quest has been completed"""
    return quest_id in character.get("completed_quests", [])


def is_quest_active(character, quest_id):
    """Check if a specific quest is currently active"""
    return quest_id in character.get("active_quests", [])


def can_accept_quest(character, quest_id, quest_data_dict):
    """
    Check if character meets all requirements to accept quest
    Returns: True if can accept, False otherwise
    Does NOT raise exceptions - just returns boolean
    """
    if quest_id not in quest_data_dict:
        return False

    quest = quest_data_dict[quest_id]

    if quest_id in character.get("completed_quests", []):
        return False

    if quest_id in character.get("active_quests", []):
        return False

    required_level = quest.get("required_level", 1)
    if character.get("level", 1) < required_level:
        return False

    prereq = quest.get("prerequisite", "NONE")
    if prereq != "NONE" and prereq not in character.get("completed_quests", []):
        return False

    return True


def get_quest_prerequisite_chain(quest_id, quest_data_dict):
    """
    Get the full chain of prerequisites for a quest

    Returns: List of quest IDs in order [earliest_prereq, ..., quest_id]
    Raises: QuestNotFoundError if quest doesn't exist
    """
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError(f"Quest '{quest_id}' not found.")

    chain = []
    current = quest_id

    while True:
        if current not in quest_data_dict:
            raise QuestNotFoundError(f"Quest '{current}' not found in chain tracing.")

        chain.append(current)
        prereq = quest_data_dict[current].get("prerequisite", "NONE")
        if prereq == "NONE":
            break

        current = prereq

    chain.reverse()
    return chain


def get_quest_completion_percentage(character, quest_data_dict):
    """Calculate what percentage of all quests have been completed"""
    total_quests = len(quest_data_dict)
    if total_quests == 0:
        return 0.0

    completed = len(character.get("completed_quests", []))
    return (completed / total_quests) * 100


def get_total_quest_rewards_earned(character, quest_data_dict):
    """Calculate total XP and gold earned from completed quests"""
    total_xp = 0
    total_gold = 0

    for quest_id in character.get("completed_quests", []):
        if quest_id in quest_data_dict:
            quest = quest_data_dict[quest_id]
            total_xp += quest.get("reward_xp", 0)
            total_gold += quest.get("reward_gold", 0)

    return {"total_xp": total_xp, "total_gold": total_gold}


def get_quests_by_level(quest_data_dict, min_level, max_level):
    """Get all quests within a level range"""
    results = []

    for quest_id, quest in quest_data_dict.items():
        lvl = quest.get("required_level", 1)
        if min_level <= lvl <= max_level:
            results.append(quest)

    return results


def display_quest_info(quest_data):
    """Display formatted quest information"""
    print("\n" + "=" * 40)
    print(f"=== {quest_data['title']} ===")
    print("=" * 40)
    print(f"Description: {quest_data['description']}")
    print(f"Required Level: {quest_data.get('required_level', 1)}")
    prereq = quest_data.get("prerequisite", "NONE")
    if prereq == "NONE":
        prereq = "None"
    print(f"Prerequisite: {prereq}")
    print(f"Reward XP: {quest_data.get('reward_xp', 0)}")
    print(f"Reward Gold: {quest_data.get('reward_gold', 0)}\n")


def display_quest_list(quest_list):
    """Display a list of quests in summary format"""
    if not quest_list:
        print("\n(No quests found.)")
        return

    print("\n=== QUEST LIST ===")
    for quest in quest_list:
        print(f"- {quest['title']} (Level {quest['required_level']})")
        print(f"  Rewards: {quest['reward_xp']} XP, {quest['reward_gold']} Gold\n")


def display_character_quest_progress(character, quest_data_dict):
    """Display character's quest statistics and progress"""
    print("\n=== QUEST PROGRESS ===")
    active = len(character.get("active_quests", []))
    completed = len(character.get("completed_quests", []))
    total = len(quest_data_dict)

    print(f"Active Quests: {active}")
    print(f"Completed Quests: {completed} / {total}")

    percentage = get_quest_completion_percentage(character, quest_data_dict)
    print(f"Completion: {percentage:.2f}%")

    rewards = get_total_quest_rewards_earned(character, quest_data_dict)
    print(f"Total XP Earned: {rewards['total_xp']}")
    print(f"Total Gold Earned: {rewards['total_gold']}")


def validate_quest_prerequisites(quest_data_dict):
    """Validate that all quest prerequisites exist"""
    for quest_id, quest in quest_data_dict.items():
        prereq = quest.get("prerequisite", "NONE")
        if prereq != "NONE" and prereq not in quest_data_dict:
            raise QuestNotFoundError(
                f"Quest '{quest_id}' has invalid prerequisite '{prereq}'."
            )
    return True
