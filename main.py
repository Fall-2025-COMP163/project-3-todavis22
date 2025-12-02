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
def load_game():
    """
    Load an existing saved game

    Shows list of saved characters
    Prompts user to select one
    """
    global current_character

    from character_manager import list_saved_characters, load_character

    # 1. Get list of saved characters
    saved_characters = list_saved_characters()

    if not saved_characters:
        print("No saved characters found.")
        return

    # 2. Display characters
    print("Saved Characters:")
    for idx, name in enumerate(saved_characters, 1):
        print(f"{idx}. {name}")

    # 3. Prompt user to select
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

    # 4. Attempt to load character
    try:
        current_character = load_character(character_name)
        print(f"Loaded character: {current_character['name']}")
    except CharacterNotFoundError:
        print("Error: Character not found.")
        return
    except SaveFileCorruptedError:
        print("Error: Save file is corrupted.")
        return

    # 5. Start game loop
    game_loop()


def display_stats(character, class_name=None, level=None):
    """Function to display character's stats"""
    if not character:
        print("No character loaded.")
        return
    print(f"{character['name']} - {class_name} (Level {level})")
    print(f"HP: {character['health']}/{character['max_health']} STR:{character['strength']} MAG:{character['magic']} Gold:{character['gold']}")


def display_inventory(character, item_data_dict):
    """Function to display character's inventory"""
    if not character or not character.get("inventory"):
        print("Inventory empty.")
        return
    for i, item_id in enumerate(character["inventory"], 1):
        info = item_data_dict.get(item_id, {"name": "Unknown"})
        print(f"{i}. {info.get('name','Unknown')} ({info.get('type','?')})")


def game_loop():
    """Main game loop - shows game menu and processes actions"""
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
            display_stats(current_character, current_character.get("class", "Unknown"),
                          current_character.get("level", 1))
        elif choice == 2:
            display_inventory(current_character, all_items)  # assuming all_items is loaded
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


def main():
    """Main game execution function"""

    # Display welcome message
    display_welcome()

    # Load game data
    try:
        load_game_data()
        print("Game data loaded successfully!")
    except MissingDataFileError:
        print("Creating default game data...")
        game_data.create_default_data_files()
        load_game_data()
    except InvalidDataFormatError as e:
        print(f"Error loading game data: {e}")
        print("Please check data files for errors.")
        return

    # Main menu loop
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
            print("Invalid choice. Please select 1-3.")


if __name__ == "__main__":
    main()
