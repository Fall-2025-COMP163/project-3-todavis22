"""
COMP 163 - Project 3: Quest Chronicles
Combat System Module - Starter Code

Name: [Your Name Here]

AI Usage: [Document any AI assistance used]

Handles combat mechanics
"""

from custom_exceptions import (
    InvalidTargetError,
    CombatNotActiveError,
    CharacterDeadError,
    AbilityOnCooldownError
)

# ============================================================================
# ENEMY DEFINITIONS
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
        quest_data = parse_quest_block(lines)
        quests[quest_data['quest_id']] = quest_data
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
            value = int(value)
        quest[key] = value
    if "quest_id" not in quest:
        raise InvalidDataFormatError("Missing quest_id")
    return quest

def load_items(filename="data/items.txt"):
    items = {}
    try:
        with open(filename, "r") as f:
            content = f.read()
    except FileNotFoundError:
        raise MissingDataFileError(f"{filename} not found")
    except Exception as e:
        raise CorruptedDataError(f"Cannot read file: {e}")

    blocks = content.strip().split("\n\n")
    for block in blocks:
        lines = block.strip().split("\n")
        item_data = parse_item_block(lines)
        items[item_data['item_id']] = item_data
    return items

def parse_item_block(lines):
    item = {}
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
    return item

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
# INVENTORY SYSTEM
# ==========================
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
        character["inventory"] = []
    return item_id in character["inventory"]

def parse_item_effect(effect_string):
    stat_name, value = effect_string.split(":")
    return stat_name, int(value)

def apply_stat_effect(character, stat_name, value):
    if stat_name not in character:
        character[stat_name] = 0
    character[stat_name] += value
    if stat_name == "health" and "max_health" in character:
        if character["health"] > character["max_health"]:
            character["health"] = character["max_health"]

def use_item(character, item_id, item_data):
    if "inventory" not in character or item_id not in character["inventory"]:
        raise ItemNotFoundError(f"{item_id} not in inventory.")
    item = item_data[item_id]
    if item["type"] != "consumable":
        raise InvalidItemTypeError(f"{item_id} cannot be used directly.")
    stat, value = parse_item_effect(item["effect"])
    apply_stat_effect(character, stat, value)
    character["inventory"].remove(item_id)
    return f"Used {item['name']}, {stat} increased by {value}."

# ==========================
# QUEST SYSTEM
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

    if "xp" not in character:
        character["xp"] = 0
    if "gold" not in character:
        character["gold"] = 0

    character["xp"] += quest["reward_xp"]
    character["gold"] += quest["reward_gold"]
    return {"xp": quest["reward_xp"], "gold": quest["reward_gold"]}

# ==========================
# COMBAT SYSTEM
# ==========================
def create_enemy(enemy_type):
    opp = {
        "goblin": {"health": 50, "strength": 8, "magic": 2, "xp_reward": 25, "gold_reward": 10},
        "orc": {"health": 80, "strength": 12, "magic": 5, "xp_reward": 50, "gold_reward": 25},
        "dragon": {"health": 200, "strength": 25, "magic": 15, "xp_reward": 200, "gold_reward": 100}
    }
    if enemy_type not in opp:
        raise InvalidTargetError(f"Enemy type '{enemy_type}' not recognized")
    stats = opp[enemy_type]
    return {
        "name": enemy_type,
        "health": stats["health"],
        "max_health": stats["health"],
        "strength": stats["strength"],
        "magic": stats["magic"],
        "xp_reward": stats["xp_reward"],
        "gold_reward": stats["gold_reward"]
    }

class SimpleBattle:
    def __init__(self, character, enemy):
        # Ensure default stats exist to avoid KeyError
        if "strength" not in character:
            character["strength"] = 5
        if "strength" not in enemy:
            enemy["strength"] = 5
        if "max_health" not in character:
            character["max_health"] = character["health"]
        if "max_health" not in enemy:
            enemy["max_health"] = enemy["health"]

        self.character = character
        self.enemy = enemy
        self.in_battle = True
        self.combat_active = self.in_battle
        self.turn_count = 0

    def player_turn(self):
        if not self.in_battle:
            raise CombatNotActiveError("Cannot take a turn outside of battle")
        self.combat_active = self.in_battle
        damage = self.calculate_damage(self.character, self.enemy)
        self.apply_damage(self.enemy, damage)

    def enemy_turn(self):
        if not self.in_battle:
            raise CombatNotActiveError("Cannot take a turn outside of battle")
        self.combat_active = self.in_battle
        damage = self.calculate_damage(self.enemy, self.character)
        self.apply_damage(self.character, damage)

    def calculate_damage(self, attacker, defender):
        damage = attacker["strength"] - (defender["strength"] // 4)
        return max(damage, 1)

    def apply_damage(self, target, damage):
        target["health"] -= damage
        if target["health"] < 0:
            target["health"] = 0
