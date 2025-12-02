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
# INVENTORY SYSTEM (simplified versions)
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
    character[stat] = character.get(stat, 0) + value
    if stat == "health" and character["health"] > character["max_health"]:
        character["health"] = character["max_health"]

# ----------------------------------------------------------------------
# MENUS
# ----------------------------------------------------------------------

def main_menu():
    """
    Display the main menu and get player's choice.
    Options:
        1. New Game
        2. Load Game
        3. Exit
    Returns: integer 1-3
    """
    while True:
        print("\nMain Menu:")
        print("1. New Game")
        print("2. Load Game")
        print("3. Exit")
        choice = input("Enter choice (1-3): ").strip()
        if choice in ["1", "2", "3"]:
            return int(choice)
        print("Invalid input! Please enter 1, 2, or 3.")

def game_menu():
    """
    Display the in-game menu and get player's choice.
    Options:
        1. View Character Stats
        2. View Inventory
        3. Quest Menu
        4. Explore
        5. Shop
        6. Save and Quit
    Returns: integer 1-6
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
    """
    Display all important stats of the current character.
    """
    c = current_character
    print("\n--- Character Stats ---")
    print(f"Name: {c['name']}, Class: {c['class']}, Level: {c['level']}")
    print(f"Health: {c['health']}/{c['max_health']}, Strength: {c['strength']}, Magic: {c['magic']}")
    print(f"Gold: {c['gold']}")
    print(f"Active Quests: {len(c['active_quests'])}, Completed Quests: {len(c['completed_quests'])}")

def view_inventory():
    """
    Display the character's inventory with quantities.
    """
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
    """
    Display quests menu with active, completed, and available quests.
    """
    c = current_character
    print("\n--- Quest Menu ---")
    print("Active Quests:", c["active_quests"])
    print("Completed Quests:", c["completed_quests"])
    print("Available Quests:", [q for q in all_quests if q not in c["active_quests"] and q not in c["completed_quests"]])
    input("Press Enter to return...")

def explore():
    """
    Randomly encounter enemies and allow combat.
    Basic attack or run options. Gain XP and gold for victories.
    """
    print("\nExploring...")
    enemy_hp = random.randint(20,50)
    enemy_str = random.randint(3,10)
    print(f"Encountered a goblin! HP: {enemy_hp}, Strength: {enemy_str}")
    c = current_character
    while enemy_hp > 0 and c["health"] > 0:
        print(f"Your HP: {c['health']}")
        action = input("Attack (a) or Run (r)? ").strip().lower()
        if action == "a":
            damage = c["strength"] + random.randint(0,5)
            enemy_hp -= damage
            print(f"You hit for {damage} damage! Enemy HP: {max(enemy_hp,0)}")
            if enemy_hp <= 0:
                print("Enemy defeated! You gain 20 XP and 10 gold.")
                c["xp"] += 20
                c["gold"] += 10
                break
            enemy_damage = enemy_str + random.randint(0,3)
            c["health"] -= enemy_damage
            print(f"Enemy hits you for {enemy_damage} damage!")
        else:
            print("You ran away safely!")
            break
    if c["health"] <= 0:
        handle_character_death()

def shop():
    """
    Simple shop menu to buy items using gold.
    Displays all available items and allows purchase if enough gold and space.
    """
    c = current_character
    print("\n--- Shop ---")
    for idx, (item_id, item) in enumerate(all_items.items(),1):
        print(f"{idx}. {item['name']} ({item['type']}), Cost: {item['cost']} gold")
    choice = input("Enter item number to buy or '0' to exit: ").strip()
    if choice == "0":
        return
    try:
        idx = int(choice) - 1
        item_id = list(all_items.keys())[idx]
        if c["gold"] < all_items[item_id]["cost"]:
            print("Not enough gold!")
        elif len(c["inventory"]) >= MAX_INVENTORY_SIZE:
            print("Inventory full!")
        else:
            add_item_to_inventory(c, item_id)
            c["gold"] -= all_items[item_id]["cost"]
            print(f"Purchased {all_items[item_id]['name']}!")
    except:
        print("Invalid choice.")

# ----------------------------------------------------------------------
# CHARACTER DEATH
# ----------------------------------------------------------------------

def handle_character_death():
    """
    Handles player death.
    Offers revive if enough gold, otherwise ends game.
    """
    global game_running
    c = current_character
    print("\nYou have died!")
    if c["gold"] >= 20:
        choice = input("Pay 20 gold to revive? (y/n) ").strip().lower()
        if choice == "y":
            c["gold"] -= 20
            revive_character(c)
            print("You are revived!")
            return
    print("Game Over.")
    game_running = False

# ----------------------------------------------------------------------
# NEW / LOAD GAME
# ----------------------------------------------------------------------

def new_game():
    """
    Start a new game.
    Prompts for character name and class, then starts the game loop.
    """
    global current_character, game_running
    name = input("Enter character name: ")
    print("Choose class: 1.Warrior 2.Mage 3.Rogue")
    cls = input("Class number: ").strip()
    classes = {"1":"warrior","2":"mage","3":"rogue"}
    if cls not in classes:
        print("Invalid class!")
        return
    current_character = create_character(name, classes[cls])
    print(f"Welcome {name} the {classes[cls]}!")
    game_loop()

def load_game():
    """
    Load an existing saved game.
    Currently simplified to start a new game instead.
    """
    global current_character
    print("Load game feature not implemented. Starting new game instead.")
    new_game()

# ----------------------------------------------------------------------
# GAME LOOP
# ----------------------------------------------------------------------

def game_loop():
    """
    Main game loop.
    Displays menu and processes player actions until quitting or death.
    """
    global game_running
    game_running = True
    while game_running:
        choice = game_menu()
        if choice == 1:
            view_character_stats()
        elif choice == 2:
            view_inventory()
        elif choice == 3:
            quest_menu()
        elif choice == 4:
            explore()
        elif choice == 5:
            shop()
        elif choice == 6:
            print("Game saved (not really, simplified). Goodbye!")
            break
        else:
            print("Invalid choice!")

# ----------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------

def display_welcome():
    """
    Display a welcome banner at the start of the game.
    """
    print("="*50)
    print("     QUEST CHRONICLES - BEGINNER RPG")
    print("="*50)

def main():
    """
    Main game execution function.
    Handles welcome, data loading, and main menu loop.
    """
    display_welcome()
    load_game_data()
    while True:
        choice = main_menu()
        if choice == 1:
            new_game()
        elif choice == 2:
            load_game()
        elif choice == 3:
            print("Thanks for playing!")
            break


if __name__ == "__main__":
    main()

