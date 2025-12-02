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
def main_menu():
    """Display main menu and get player choice"""
    while True:
        print("\n=== MAIN MENU ===")
        print("1. New Game")
        print("2. Load Game")
        print("3. Exit")
        choice = input("Enter choice (1-3): ").strip()
        if choice in ("1", "2", "3"):
            return int(choice)
        print("Invalid input. Please enter 1, 2, or 3.")


def new_game():
    """Start a new game"""
    global current_character
    while True:
        name = input("Enter your character's name: ").strip()
        if name:
            break
        print("Name cannot be empty.")
    
    while True:
        char_class = input("Choose your class (Warrior/Mage/Rogue): ").strip().lower()
        try:
            current_character = create_character(name, char_class)
            print(f"Character {name} the {char_class.title()} created!")
            save_character(current_character)
            game_loop()
            break
        except InvalidCharacterClassError:
            print("Invalid class. Choose Warrior, Mage, or Rogue.")


def load_game():
    """Load an existing saved game"""
    global current_character
    try:
        saved_chars = game_data.list_saved_characters()
        if not saved_chars:
            print("No saved characters found. Starting new game.")
            new_game()
            return
        print("\nSaved Characters:")
        for idx, char_name in enumerate(saved_chars, 1):
            print(f"{idx}. {char_name}")
        while True:
            choice = input(f"Select a character (1-{len(saved_chars)}): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(saved_chars):
                char_name = saved_chars[int(choice) - 1]
                current_character = load_character(char_name)
                print(f"Loaded character {char_name}.")
                game_loop()
                break
            print("Invalid selection.")
    except (CharacterNotFoundError, SaveFileCorruptedError) as e:
        print(f"Error loading character: {e}")


# ===================== GAME LOOP & MENUS =====================

def game_loop():
    """Main game loop"""
    global game_running, current_character
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
            save_game()
            print("Game saved. Exiting to main menu.")
            game_running = False
        else:
            print("Invalid choice.")
        if current_character is None:
            game_running = False  # character died


def game_menu():
    """Display game menu and get player choice"""
    print("\n=== GAME MENU ===")
    print("1. View Character Stats")
    print("2. View Inventory")
    print("3. Quest Menu")
    print("4. Explore (Find Battles)")
    print("5. Shop")
    print("6. Save and Quit")
    while True:
        choice = input("Enter choice (1-6): ").strip()
        if choice in [str(i) for i in range(1, 7)]:
            return int(choice)
        print("Invalid input. Enter a number between 1 and 6.")


# ===================== CHARACTER & INVENTORY =====================

def view_character_stats():
    """Display character information"""
    global current_character
    if not current_character:
        print("No character loaded.")
        return
    print("\n=== CHARACTER STATS ===")
    for key, value in current_character.stats().items():
        print(f"{key}: {value}")
    print(f"Gold: {current_character.gold}")
    print("Active Quests:", [q['name'] for q in get_active_quests(current_character)])


def view_inventory():
    """Display and manage inventory"""
    global current_character
    if not current_character:
        print("No character loaded.")
        return
    while True:
        print("\n=== INVENTORY ===")
        show_inventory(current_character)
        print("Options: 1. Use Item 2. Equip Item 3. Drop Item 4. Back")
        choice = input("Enter choice: ").strip()
        try:
            if choice == "1":
                item = input("Enter item to use: ")
                use_item(current_character, item)
            elif choice == "2":
                item = input("Enter item to equip: ")
                equip_item(current_character, item)
            elif choice == "3":
                item = input("Enter item to drop: ")
                drop_item(current_character, item)
            elif choice == "4":
                break
            else:
                print("Invalid choice.")
        except InventoryError as e:
            print(f"Inventory error: {e}")


# ===================== QUESTS =====================

def quest_menu():
    """Quest management menu"""
    global current_character
    if not current_character:
        print("No character loaded.")
        return
    while True:
        print("\n=== QUEST MENU ===")
        print("1. View Active Quests")
        print("2. View Available Quests")
        print("3. View Completed Quests")
        print("4. Accept Quest")
        print("5. Abandon Quest")
        print("6. Complete Quest")
        print("7. Back")
        choice = input("Enter choice (1-7): ").strip()
        if choice == "1":
            for q in get_active_quests(current_character):
                print(f"{q['name']}: {q['description']}")
        elif choice == "2":
            for q in get_available_quests(current_character):
                print(f"{q['name']}: {q['description']}")
        elif choice == "3":
            for q in get_completed_quests(current_character):
                print(f"{q['name']}: {q['description']}")
        elif choice == "4":
            q_name = input("Enter quest name to accept: ")
            accept_quest(current_character, q_name)
        elif choice == "5":
            q_name = input("Enter quest name to abandon: ")
            abandon_quest(current_character, q_name)
        elif choice == "6":
            q_name = input("Enter quest name to complete (for testing): ")
            complete_quest(current_character, q_name)
        elif choice == "7":
            break
        else:
            print("Invalid choice.")


# ===================== EXPLORING & BATTLE =====================

def explore():
    """Find and fight random enemies"""
    global current_character
    if not current_character:
        print("No character loaded.")
        return
    enemy = game_data.create_enemy(level=current_character.level)
    print(f"You encountered a {enemy['type']}!")
    result = SimpleBattle(current_character, enemy).fight()
    if result == "dead":
        handle_character_death()
    elif result == "victory":
        print(
            f"You defeated the {enemy['type']}! "
            f"Gained {enemy['xp_reward']} XP and {enemy['gold_reward']} gold."
        )
        current_character.xp += enemy['xp_reward']
        current_character.gold += enemy['gold_reward']


# ===================== SHOP =====================

def shop():
    """Shop menu for buying/selling items"""
    global current_character, all_items
    if not current_character:
        print("No character loaded.")
        return
    if not all_items:
        print("Shop is currently empty. No items to buy or sell.")
        return
    while True:
        print("\n=== SHOP ===")
        print(f"Gold: {current_character.gold}")
        for idx, item in enumerate(all_items.values(), 1):
            print(f"{idx}. {item['name']} ({item['type']}) - {item['cost']} gold")
        print("Options: Buy <num>, Sell <item>, Back")
        choice = input("Enter choice: ").strip().lower()
        if choice.startswith("buy"):
            try:
                idx = int(choice.split()[1]) - 1
                item_key = list(all_items.keys())[idx]
                purchase_item(current_character, item_key, all_items)
            except (ValueError, IndexError, InventoryError) as e:
                print(f"Cannot buy item: {e}")
        elif choice.startswith("sell"):
            try:
                item_name = " ".join(choice.split()[1:])
                sell_item(current_character, item_name, all_items)
            except InventoryError as e:
                print(f"Cannot sell item: {e}")
        elif choice == "back":
            break
        else:
            print("Invalid choice.")


# ===================== SAVE / LOAD DATA =====================

def save_game():
    """Save current game state"""
    global current_character
    try:
        save_character(current_character)
        print("Game saved successfully.")
    except Exception as e:
        print(f"Error saving game: {e}")


def load_game_data():
    """Load all quest and item data from files"""
    global all_quests, all_items
    try:
        all_quests = game_data.load_quests()
        all_items = game_data.load_items()
    except (MissingDataFileError, InvalidDataFormatError):
        print("Game data missing or corrupted. Creating default data files...")
        game_data.create_default_data_files()
        all_quests = game_data.load_quests()
        all_items = game_data.load_items()


# ===================== DEATH & WELCOME =====================

def handle_character_death():
    """Handle character death"""
    global current_character, game_running
    print(f"\n{current_character.name} has died!")
    while True:
        choice = input("Revive for 50 gold or Quit? (revive/quit): ").strip().lower()
        if choice == "revive":
            if current_character.gold >= 50:
                revive_character(current_character)
                current_character.gold -= 50
                print("You have been revived!")
                return
            else:
                print("Not enough gold to revive.")
        elif choice == "quit":
            current_character = None
            game_running = False
            return
        else:
            print("Invalid choice.")


def display_welcome():
    """Display welcome message"""
    print("=" * 50)
    print("     QUEST CHRONICLES - A MODULAR RPG ADVENTURE")
    print("=" * 50)
    print("\nWelcome to Quest Chronicles!")
    print("Build your character, complete quests, and become a legend!")
    print()


# ===================== ENTRY POINT =====================

def main():
    """Main game execution function"""
    display_welcome()
    try:
        load_game_data()
        print("Game data loaded successfully!")
    except (MissingDataFileError, InvalidDataFormatError) as e:
        print(f"Error loading game data: {e}")
        return
    
    while True:
        choice = main_menu()
        if choice == 1:
            new_game()
        elif choice == 2:
            load_game()
        elif choice == 3:
            print("\nThanks for playing Quest Chronicles!")
            break
        else:
            # This should never hit because main_menu only returns 1-3
            print("Invalid choice. Please select 1-3.")


if __name__ == "__main__":
    main()
