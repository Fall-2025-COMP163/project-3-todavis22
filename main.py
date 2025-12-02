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
# main.py

# Global variables
current_character = None
all_items = {}
all_quests = {}
game_running = False

# =====================================================
# REQUIRED FUNCTIONS
# =====================================================

def main_menu():
    """Display main menu and return player choice"""
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
    name = input("Enter your character's name: ").strip()
    char_class = input("Choose your class (Warrior/Mage/Rogue): ").strip()
    
    from character_manager import create_character, save_character

    current_character = create_character(name, char_class)
    save_character(current_character)
    game_loop()


def load_game():
    """Load an existing saved game"""
    global current_character
    from character_manager import list_saved_characters, load_character, CharacterNotFoundError, SaveFileCorruptedError

    saved_characters = list_saved_characters()
    if not saved_characters:
        print("No saved characters found.")
        return

    print("Saved Characters:")
    for idx, name in enumerate(saved_characters, 1):
        print(f"{idx}. {name}")

    while True:
        try:
            choice = int(input(f"Select a character (1-{len(saved_characters)}): "))
            if 1 <= choice <= len(saved_characters):
                character_name = saved_characters[choice - 1]
                break
            else:
                print("Invalid choice, try again.")
        except ValueError:
            print("Please enter a number.")

    try:
        current_character = load_character(character_name)
        print(f"Loaded character: {current_character['name']}")
    except CharacterNotFoundError:
        print("Error: Character not found.")
        return
    except SaveFileCorruptedError:
        print("Error: Save file is corrupted.")
        return

    game_loop()


def game_loop():
    """Main game loop"""
    global game_running, current_character
    from character_manager import save_character

    game_running = True
    while game_running:
        print("\n=== GAME MENU ===")
        print("1. View Character Stats")
        print("2. View Inventory")
        print("3. Go on Quest / Battle")
        print("4. Save Game")
        print("5. Exit to Main Menu")

        try:
            choice = int(input("Select an option: "))
        except ValueError:
            print("Please enter a number.")
            continue

        if choice == 1:
            display_stats(current_character)
        elif choice == 2:
            display_inventory(current_character)
        elif choice == 3:
            print("Starting quest or battle... (placeholder)")
        elif choice == 4:
            try:
                save_character(current_character)
                print("Game saved successfully.")
            except Exception as e:
                print(f"Error saving game: {e}")
        elif choice == 5:
            print("Exiting to main menu...")
            game_running = False
        else:
            print("Invalid choice. Please select a number from 1-5.")


def save_game():
    """Save current game state"""
    global current_character
    from character_manager import save_character
    try:
        save_character(current_character)
        print("Game saved successfully.")
    except Exception as e:
        print(f"Error saving game: {e}")


def load_game_data():
    """Load all quests and items"""
    global all_quests, all_items
    import game_data
    try:
        all_quests = game_data.load_quests()
        all_items = game_data.load_items()
    except (game_data.MissingDataFileError, game_data.InvalidDataFormatError):
        print("Data missing or corrupted, creating default files...")
        game_data.create_default_data_files()
        all_quests = game_data.load_quests()
        all_items = game_data.load_items()


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def display_stats(character):
    if not character:
        print("No character loaded.")
        return
    print(f"Name: {character['name']} | Class: {character.get('class','Unknown')} | Level: {character.get('level',1)}")
    print(f"HP: {character.get('health',0)}/{character.get('max_health',0)} | STR: {character.get('strength',0)} | MAG: {character.get('magic',0)} | Gold: {character.get('gold',0)}")


def display_inventory(character):
    if not character or not character.get("inventory"):
        print("Inventory is empty.")
        return
    print("Inventory:")
    for i, item in enumerate(character["inventory"], 1):
        print(f"{i}. {item}")


# =====================================================
# MAIN EXECUTION
# =====================================================

def main():
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
        else:
            print("Invalid choice. Please select 1-3.")


def display_welcome():
    print("="*50)
    print(" QUEST CHRONICLES - A MODULAR RPG ADVENTURE ")
    print("="*50)


if __name__ == "__main__":
    main()
