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
        return False
    return item_id in character["inventory"]

def count_item(character, item_id):
    if "inventory" not in character:
        return 0
    return character["inventory"].count(item_id)

def get_inventory_space_remaining(character):
    if "inventory" not in character:
        return MAX_INVENTORY_SIZE
    return MAX_INVENTORY_SIZE - len(character["inventory"])

def clear_inventory(character):
    if "inventory" not in character:
        character["inventory"] = []
        return []
    removed_items = character["inventory"]
    character["inventory"] = []
    return removed_items

# ==========================
# ITEM USAGE
# ==========================
def parse_item_effect(effect_string):
    stat_name, value = effect_string.split(":")
    return stat_name, int(value)

def apply_stat_effect(character, stat_name, value):
    if stat_name not in character:
        character[stat_name] = 0
    character[stat_name] += value

    if "health" in character and "max_health" in character:
        if stat_name == "health" and character["health"] > character["max_health"]:
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

def equip_weapon(character, item_id, item_data):
    if "inventory" not in character or item_id not in character["inventory"]:
        raise ItemNotFoundError(f"{item_id} not in inventory.")

    item = item_data[item_id]
    if item["type"] != "weapon":
        raise InvalidItemTypeError(f"{item_id} is not a weapon.")

    if "equipped_weapon" in character and character["equipped_weapon"] is not None:
        unequip_weapon(character)

    stat, value = parse_item_effect(item["effect"])
    if stat not in character:
        character[stat] = 0
    character[stat] += value
    character["equipped_weapon"] = item_id
    character["equipped_weapon_effect"] = item["effect"]
    character["inventory"].remove(item_id)
    return f"{character['name']} equipped {item['name']} (+{value} {stat})."

def equip_armor(character, item_id, item_data):
    if "inventory" not in character or item_id not in character["inventory"]:
        raise ItemNotFoundError(f"{item_id} not in inventory.")

    item = item_data[item_id]
    if item["type"] != "armor":
        raise InvalidItemTypeError(f"{item_id} is not armor.")

    if "equipped_armor" in character and character["equipped_armor"] is not None:
        unequip_armor(character)

    stat, value = parse_item_effect(item["effect"])
    if stat not in character:
        character[stat] = 0
    character[stat] += value
    character["equipped_armor"] = item_id
    character["equipped_armor_effect"] = item["effect"]
    character["inventory"].remove(item_id)
    return f"{character['name']} equipped {item['name']} (+{value} {stat})."

def unequip_weapon(character):
    if "equipped_weapon" not in character or character["equipped_weapon"] is None:
        return None

    weapon_id = character["equipped_weapon"]
    stat, value = parse_item_effect(character["equipped_weapon_effect"])
    character[stat] -= value

    if "inventory" not in character:
        character["inventory"] = []

    if len(character["inventory"]) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory is full.")

    character["inventory"].append(weapon_id)
    character["equipped_weapon"] = None
    character["equipped_weapon_effect"] = None
    return weapon_id

def unequip_armor(character):
    if "equipped_armor" not in character or character["equipped_armor"] is None:
        return None

    armor_id = character["equipped_armor"]
    stat, value = parse_item_effect(character["equipped_armor_effect"])
    character[stat] -= value

    if "inventory" not in character:
        character["inventory"] = []

    if len(character["inventory"]) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory is full.")

    character["inventory"].append(armor_id)
    character["equipped_armor"] = None
    character["equipped_armor_effect"] = None
    return armor_id

def display_inventory(character, item_data_dict):
    if "inventory" not in character:
        character["inventory"] = []

    inventory = character["inventory"]
    if not inventory:
        print("Inventory is empty")
        return

    counts = {}
    for item in inventory:
        if item not in counts:
            counts[item] = 0
        counts[item] += 1

    print("=== Inventory ===")
    for item_id, qty in counts.items():
        item_info = item_data_dict[item_id]
        print(f"{item_info['name']} ({item_info['type']}) x{qty}")

# ==========================
# SHOP SYSTEM
# ==========================
def purchase_item(character, item_id, item_data):
    cost = item_data[item_id]["cost"]

    if "gold" not in character:
        character["gold"] = 0
    if character["gold"] < cost:
        raise InsufficientResourcesError("Not enough gold")

    if "inventory" not in character:
        character["inventory"] = []

    if len(character["inventory"]) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory full")

    character["gold"] -= cost
    character["inventory"].append(item_id)
    return True

def sell_item(character, item_id, item_data):
    if "inventory" not in character or item_id not in character["inventory"]:
        raise ItemNotFoundError("Item not in inventory")

    sell_price = item_data[item_id]["cost"] // 2
    character["inventory"].remove(item_id)

    if "gold" not in character:
        character["gold"] = 0
    character["gold"] += sell_price
    return sell_price

# ==========================
# QUEST SYSTEM
# ==========================
def load_quests(quest_data):
    if type(quest_data) is not dict:
        raise InvalidDataFormatError("Quest data must be a dictionary")
    return quest_data

def start_quest(character, quest_id, quest_data):
    if quest_id not in quest_data:
        raise QuestNotFoundError(f"Quest '{quest_id}' not found")

    quest = quest_data[quest_id]

    if "level_required" in quest:
        if character["level"] < quest["level_required"]:
            raise InsufficientLevelError(f"Level {quest['level_required']} required")

    if "active_quests" not in character:
        character["active_quests"] = []
    if quest_id in character["active_quests"]:
        raise QuestAlreadyCompletedError("Quest already active or completed")

    character["active_quests"].append(quest_id)
    return True

def complete_quest(character, quest_id, quest_data):
    if "active_quests" not in character or quest_id not in character["active_quests"]:
        raise QuestNotActiveError(f"Quest '{quest_id}' not active")

    character["active_quests"].remove(quest_id)
    if "completed_quests" not in character:
        character["completed_quests"] = []
    character["completed_quests"].append(quest_id)
    return True

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

def display_battle_log(message):
    print(message)

def use_special_ability(character, enemy):
    damage = 10
    enemy['health'] -= damage
    return f"{character['name']} uses a special ability on {enemy['name']} for {damage} damage!"

class SimpleBattle:
    def __init__(self, character, enemy):
        self.character = character
        self.enemy = enemy
        self.in_battle = True
        self.combat_active = self.in_battle  # alias for tests
        self.turn_count = 0

    def start_battle(self):
        self.combat_active = self.in_battle
        if self.character['health'] <= 0:
            raise CharacterDeadError("Cannot start battle: character is dead")
        
        while self.in_battle:
            self.player_turn()
            winner = self.check_battle_end()
            if winner:
                self.in_battle = False
                self.combat_active = self.in_battle
                break
            self.enemy_turn()
            winner = self.check_battle_end()
            if winner:
                self.in_battle = False
                self.combat_active = self.in_battle
                break
        
        if self.character['health'] > 0:
            self.character['experience'] += self.enemy['xp_reward']
            self.character['gold'] += self.enemy['gold_reward']
            return {'winner': 'player', 'xp_gained': self.enemy['xp_reward'], 'gold_gained': self.enemy['gold_reward']}
        else:
            return {'winner': 'enemy', 'xp_gained': 0, 'gold_gained': 0}

    def player_turn(self):
        if not self.in_battle:
            raise CombatNotActiveError("Cannot take a turn outside of battle")
        self.combat_active = self.in_battle

        # Skipping input for testing environments
        choice = "1"  # default to basic attack

        if choice == "1":
            damage = self.calculate_damage(self.character, self.enemy)
            self.apply_damage(self.enemy, damage)
            display_battle_log(f"You attack the {self.enemy['name']} for {damage} damage!")
        elif choice == "2":
            log = use_special_ability(self.character, self.enemy)
            display_battle_log(log)
        elif choice == "3":
            if self.attempt_escape():
                display_battle_log("You escaped successfully!")
            else:
                display_battle_log("Escape failed!")
        else:
            display_battle_log("Invalid choice. You lose your turn.")

    def enemy_turn(self):
        if not self.in_battle:
            raise CombatNotActiveError("Cannot take a turn outside of battle")
        self.combat_active = self.in_battle

        damage = self.calculate_damage(self.enemy, self.character)
        self.apply_damage(self.character, damage)
        display_battle_log(f"The {self.enemy['name']} attacks you for {damage} damage!")

    def calculate_damage(self, attacker, defender):
        damage = attacker['strength'] - (defender['strength'] // 4)
        return max(damage, 1)

    def apply_damage(self, target, damage):
        target['health'] -= damage
        if target['health'] < 0:
            target['health'] = 0

    def check_battle_end(self):
        if self.enemy['health'] <= 0:
            return 'player'
        if self.character['health'] <= 0:
            return 'enemy'
        return None

    def attempt_escape(self):
        if random.random() < 0.5:
            self.in_battle = False
            self.combat_active = self.in_battle
            return True
        return False