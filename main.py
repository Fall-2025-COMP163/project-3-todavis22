"""
COMP 163 - Project 3: Quest Chronicles
Main Game Module - Starter Code

Name: [Your Name Here]

AI Usage: [Document any AI assistance used]

This is the main game file that ties all modules together.
Demonstrates module integration and complete game flow.
"""

# Import all our custom modules
import character_manager
import inventory_system
import quest_handler
import combat_system
import game_data
from custom_exceptions import *

# ============================================================================
# GAME STATE
# ============================================================================

# Global variables for game data
current_character = None
all_quests = {}
all_items = {}
game_running = False

# ============================================================================
# MAIN MENU
# ============================================================================

def load_game_data():
    """
    Load items and quests into the game.
    Here we use simplified default data for beginner-level RPG.
    """
    global all_quests, all_items
    # Default items
    all_items = {
        "potion": {"name": "Health Potion", "type": "consumable", "effect": "health:20", "cost": 10},
        "sword": {"name": "Iron Sword", "type": "weapon", "effect": "strength:5", "cost": 20},
        "armor": {"name": "Leather Armor", "type": "armor", "effect": "max_health:10", "cost": 15},
    }
    # Default quests
    all_quests = {
        "quest1": {"quest_id": "quest1", "title": "First Quest", "description": "Defeat 3 goblins", 
                   "reward_xp": 50, "reward_gold": 20, "required_level": 1, "prerequisite": "NONE"},
    }

# ----------------------------------------------------------------------
# CHARACTER MANAGEMENT (Simplified)
# ----------------------------------------------------------------------
def create_character(name, character_class):
    """
    Create a new character with basic stats and inventory.
    Raises InvalidCharacterClassError if class is invalid.
    """
    if character_class not in ["warrior", "mage", "rogue"]:
        raise InvalidCharacterClassError()
    character = {
        "name": name,
        "class": character_class,
        "level": 1,
        "xp": 0,
        "gold": 50,
        "health": 100,
        "max_health": 100,
        "strength": 5,
        "magic": 5,
        "inventory": [],
        "equipped_weapon": None,
        "equipped_weapon_effect": None,
        "equipped_armor": None,
        "equipped_armor_effect": None,
        "active_quests": [],
        "completed_quests": []
    }
    return character

def revive_character(character):
    """
    Revive a character by restoring health to maximum.
    """
    character["health"] = character["max_health"]
    return character

# ----------------------------------------------------------------------
# INVENTORY SYSTEM
# ----------------------------------------------------------------------
def add_item_to_inventory(character, item_id):
    """
    Add an item to the character's inventory.
    Raises InventoryFullError if inventory is at max capacity.
    """
    if len(character["inventory"]) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory is full")
    character["inventory"].append(item_id)

def remove_item_from_inventory(character, item_id):
    """
    Remove an item from the character's inventory.
    Raises ItemNotFoundError if item is not found.
    """
    if item_id not in character["inventory"]:
        raise ItemNotFoundError("Item not found")
    character["inventory"].remove(item_id)

def parse_item_effect(effect_string):
    """
    Parse an item effect string into a stat name and value.
    Example: "health:20" -> ("health", 20)
    """
    stat, value = effect_string.split(":")
    return stat, int(value)

def apply_stat_effect(character, stat, value):
    """
    Apply a stat modification to the character.
    Ensures health does not exceed max_health.
    """
    character[stat] += value
    if stat == "health" and character["health"] > character["max_health"]:
        character["health"] = character["max_health"]

# ----------------------------------------------------------------------
# ENEMIES AND COMBAT
# ----------------------------------------------------------------------
def create_enemy(enemy_type):
    """
    Create an enemy based on type
    Returns: Enemy dictionary
    Raises: InvalidTargetError if enemy_type not recognized
    """
    opp = {
        "goblin": {"health": 50, "strength": 8, "magic": 2, "xp_reward": 25, "gold_reward": 10},
        "orc": {"health": 80, "strength": 12, "magic": 5, "xp_reward": 50, "gold_reward": 25},
        "dragon": {"health": 200, "strength": 25, "magic": 15, "xp_reward": 200, "gold_reward": 100}
    }

    if enemy_type not in opp:
        raise InvalidTargetError(f"Enemy type '{enemy_type}' not recognized")
    
    stats = opp[enemy_type]
    
    enemy = {
        "name": enemy_type,
        "health": stats["health"],
        "max_health": stats["health"],
        "strength": stats["strength"],
        "magic": stats["magic"],
        "xp_reward": stats["xp_reward"],
        "gold_reward": stats["gold_reward"]
    }
    
    return enemy

def get_random_enemy_for_level(character_level):
    """
    Get an appropriate enemy for character's level
    Returns: Enemy dictionary
    """
    if character_level <= 2:
        enemy_type = "goblin"
    elif 3 <= character_level <= 5:
        enemy_type = "orc"
    else:
        enemy_type = "dragon"
    
    return create_enemy(enemy_type)

class SimpleBattle:
    """
    Simple turn-based combat system
    Manages combat between character and enemy
    """

    def __init__(self, character):
        """Initialize battle with character and enemy"""
        self.character = character
        self.enemy = get_random_enemy_for_level(self.character['level'])
        self.in_battle = True
        self.turn_count = 0

    def start_battle(self):
        """Start the combat loop and return results"""
        if self.character['health'] <= 0:
            raise CharacterDeadError("Cannot start battle: character is dead")
        
        while self.in_battle:
            self.player_turn()
            winner = self.check_battle_end()
            if winner:
                self.in_battle = False
                break
            self.enemy_turn()
            winner = self.check_battle_end()
            if winner:
                self.in_battle = False
                break
        
        if self.character['health'] > 0:
            result = {
                'winner': 'player',
                'xp_gained': self.enemy['xp_reward'],
                'gold_gained': self.enemy['gold_reward']
            }
            self.character['xp'] += self.enemy['xp_reward']
            self.character['gold'] += self.enemy['gold_reward']
        else:
            result = {
                'winner': 'enemy',
                'xp_gained': 0,
                'gold_gained': 0
            }
        return result

    def player_turn(self):
        """Handle player's turn"""
        if not self.in_battle:
            raise CombatNotActiveError("Cannot take a turn outside of battle")
        
        print(f"\nYour HP: {self.character['health']} / {self.character['max_health']}")
        print(f"Enemy {self.enemy['name']} HP: {self.enemy['health']} / {self.enemy['max_health']}")
        print("1. Attack  2. Try to Run")
        choice = input("Enter choice: ").strip()
        
        if choice == "1":
            damage = self.calculate_damage(self.character, self.enemy)
            self.apply_damage(self.enemy, damage)
            print(f"You attack the {self.enemy['name']} for {damage} damage!")
        elif choice == "2":
            if self.attempt_escape():
                print("You escaped successfully!")
            else:
                print("Escape failed!")
        else:
            print("Invalid choice, you lose your turn.")

    def enemy_turn(self):
        """Handle enemy's turn"""
        if not self.in_battle:
            raise CombatNotActiveError("Cannot take a turn outside of battle")
        damage = self.calculate_damage(self.enemy, self.character)
        self.apply_damage(self.character, damage)
        print(f"The {self.enemy['name']} attacks you for {damage} damage!")

    def calculate_damage(self, attacker, defender):
        """Damage formula"""
        damage = attacker['strength'] - (defender['strength'] // 4)
        if damage < 1:
            damage = 1
        return damage

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
            return True
        return False

# ----------------------------------------------------------------------
# MENUS
# ----------------------------------------------------------------------
def main_menu():
    """
    Display the main menu and get player's choice.
    """
    while True:
        print("\nMain Menu:")
        print("1. New Game")
        print("2. Load Game")
        print("3. Exit")
        choice = input("Enter choice (1-3): ").strip()
        if choice in ["1","2","3"]:
            return int(choice)
        print("Invalid input! Please enter 1, 2, or 3.")

def game_menu():
    """
    Display in-game menu
    """
    print("\nGame Menu:")
    print("1. View Character Stats")
    print("2. View Inventory")
    print("3. Quest Menu")
    print("4. Explore")
    print("5. Shop")
    print("6. Save and Quit")
    choice = input("Enter choice (1-6): ").strip()
    if choice in ["1","2","3","4","5","6"]:
        return int(choice)
    return 0

# ----------------------------------------------------------------------
# GAME ACTIONS
# ----------------------------------------------------------------------
def view_character_stats():
    c = current_character
    print("\n--- Character Stats ---")
    print(f"Name: {c['name']}, Class: {c['class']}, Level: {c['level']}")
    print(f"Health: {c['health']}/{c['max_health']}, Strength: {c['strength']}, Magic: {c['magic']}")
    print(f"Gold: {c['gold']}")
    print(f"Active Quests: {len(c['active_quests'])}, Completed Quests: {len(c['completed_quests'])}")

def view_inventory():
    c = current_character
    inv = c["inventory"]
    if not inv:
        print("Inventory is empty.")
        return
    counts = {}
    for i in inv:
        counts[i] = counts.get(i,0) + 1
    print("\n--- Inventory ---")
    for item_id, qty in counts.items():
        item = all_items[item_id]
        print(f"{item['name']} ({item['type']}) x{qty}")

def quest_menu():
    c = current_character
    print("\n--- Quest Menu ---")
    print("Active Quests:", c["active_quests"])
    print("Completed Quests:", c["completed_quests"])
    print("Available Quests:", [q for q in all_quests if q not in c["active_quests"] and q not in c["completed_quests"]])
    input("Press Enter to return...")

def explore():
    """
    Updated explore() to use SimpleBattle
    """
    print("\nExploring...")
    battle = SimpleBattle(current_character)
    result = battle.start_battle()
    if result['winner'] == 'player':
        print(f"Victory! Gained {result['xp_gained']} XP and {result['gold_gained']} gold.")
    else:
        handle_character_death()


