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
    """Display main menu and get choice"""
    while True:
        print("\n=== Main Menu ===")
        print("1. New Game")
        print("2. Load Game")
        print("3. Exit")
        choice = input("Enter choice (1-3): ").strip()
        if choice in ["1","2","3"]:
            return int(choice)
        print("Invalid input! Enter 1, 2, or 3.")

def new_game():
    """Start a new game"""
    global current_character
    print("\n--- New Game ---")
    name = input("Enter character name: ").strip()
    print("Choose a class: Warrior, Mage, Rogue")
    char_class = input("Enter class: ").strip().title()
    try:
        current_character = character_manager.create_character(name, char_class)
        character_manager.save_character(current_character)
        print(f"Character {name} the {char_class} created!")
        game_loop()
    except character_manager.InvalidCharacterClassError as e:
        print(f"Error: {e}")
        return

def load_game():
    """Load existing saved game"""
    global current_character
    saves = character_manager.list_saved_characters()
    if not saves:
        print("No saved characters found.")
        return
    print("\n--- Saved Characters ---")
    for i, name in enumerate(saves, start=1):
        print(f"{i}. {name}")
    try:
        choice = int(input("Select character by number: ").strip())
        if 1 <= choice <= len(saves):
            current_character = character_manager.load_character(saves[choice-1])
            print(f"Loaded character {current_character['name']}")
            game_loop()
        else:
            print("Invalid selection")
    except ValueError:
        print("Invalid input")
    except (character_manager.CharacterNotFoundError, character_manager.SaveFileCorruptedError) as e:
        print(f"Error loading character: {e}")

# ============================================================================

def game_menu():
    """Display in-game menu"""
    print("\n=== Game Menu ===")
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
            print("Game saved. Exiting...")
            break
        else:
            print("Invalid choice!")

# ============================================================================

def view_character_stats():
    """Show character stats"""
    c = current_character
    print("\n--- Character Stats ---")
    print(f"Name: {c['name']}, Class: {c['class']}, Level: {c['level']}")
    print(f"HP: {c['health']}/{c['max_health']}, STR: {c['strength']}, MAG: {c['magic']}")
    print(f"XP: {c['experience']}, Gold: {c['gold']}")
    print(f"Active Quests: {len(c['active_quests'])}, Completed Quests: {len(c['completed_quests'])}")

def view_inventory():
    """Show inventory"""
    c = current_character
    if not c["inventory"]:
        print("Inventory empty.")
        return
    print("\n--- Inventory ---")
    counts = {}
    for i in c["inventory"]:
        counts[i] = counts.get(i,0) + 1
    for item_id, qty in counts.items():
        item = all_items.get(item_id, {"name": item_id, "type":"Unknown"})
        print(f"{item['name']} ({item['type']}) x{qty}")

def quest_menu():
    """Quest management menu"""
    c = current_character
    print("\n--- Quest Menu ---")
    print("Active:", c["active_quests"])
    print("Completed:", c["completed_quests"])
    available = [q for q in all_quests if q not in c["active_quests"] and q not in c["completed_quests"]]
    print("Available:", available)
    input("Press Enter to return...")

# ============================================================================

def explore():
    """Random battles"""
    c = current_character
    print("\nExploring...")
    enemy = create_enemy_for_level(c['level'])
    print(f"You encounter a {enemy['name']}!")
    battle_result = simple_battle(c, enemy)
    if battle_result['winner'] == 'player':
        print(f"Victory! Gained {battle_result['xp']} XP and {battle_result['gold']} gold.")
        character_manager.gain_experience(c, battle_result['xp'])
        character_manager.add_gold(c, battle_result['gold'])
    else:
        handle_character_death()

def create_enemy_for_level(level):
    """Create enemy based on level"""
    types = [("Goblin", 50, 8, 2), ("Orc", 80, 12, 5), ("Dragon", 200, 25, 15)]
    if level <= 2: e = types[0]
    elif level <= 5: e = types[1]
    else: e = types[2]
    return {"name": e[0], "health": e[1], "max_health": e[1], "strength": e[2], "magic": e[3], "xp": e[2]*5, "gold": e[2]*3}

def simple_battle(character, enemy):
    """Simple turn-based combat"""
    in_battle = True
    while in_battle:
        print(f"\nYour HP: {character['health']}/{character['max_health']}")
        print(f"{enemy['name']} HP: {enemy['health']}/{enemy['max_health']}")
        action = input("1.Attack 2.Run: ").strip()
        if action == "1":
            dmg = max(character['strength'] - enemy['strength']//4,1)
            enemy['health'] -= dmg
            print(f"You hit {enemy['name']} for {dmg} damage!")
        elif action == "2":
            if random.random()<0.5:
                print("Escaped!")
                return {'winner':'player','xp':0,'gold':0}
            else:
                print("Escape failed!")
        if enemy['health'] <= 0:
            return {'winner':'player','xp':enemy['xp'],'gold':enemy['gold']}
        # Enemy turn
        dmg = max(enemy['strength'] - character['strength']//4,1)
        character['health'] -= dmg
        print(f"{enemy['name']} hits you for {dmg} damage!")
        if character_manager.is_character_dead(character):
            return {'winner':'enemy','xp':0,'gold':0}

def shop():
    """Buy/sell items"""
    c = current_character
    print("\n--- Shop ---")
    print(f"Gold: {c['gold']}")
    for i, item in enumerate(all_items.values(), start=1):
        print(f"{i}. {item['name']} ({item['type']}) - {item['cost']} gold")
    print("0. Back")
    choice = input("Choose item to buy: ").strip()
    if choice=="0": return
    try:
        idx = int(choice)-1
        item_id = list(all_items.keys())[idx]
        item = all_items[item_id]
        if c['gold'] >= item['cost']:
            c['gold'] -= item['cost']
            c['inventory'].append(item_id)
            print(f"Bought {item['name']}")
        else:
            print("Not enough gold!")
    except:
        print("Invalid choice")

# ============================================================================

def save_game():
    """Save current character"""
    try:
        character_manager.save_character(current_character)
        print("Game saved.")
    except Exception as e:
        print(f"Error saving: {e}")

def handle_character_death():
    """Handle death"""
    global game_running
    print("\nYou have died!")
    choice = input("Revive for half max HP? (y/n): ").strip().lower()
    if choice=="y":
        character_manager.revive_character(current_character)
        print("You are revived!")
    else:
        print("Game over.")
        game_running = False

def display_welcome():
    print("="*50)
    print("   QUEST CHRONICLES - A MODULAR RPG ADVENTURE")
    print("="*50)
    print("\nWelcome! Build your character, complete quests, and become a legend!\n")

# ============================================================================

def main():
    display_welcome()
    load_game_data()
    while True:
        choice = main_menu()
        if choice==1:
            new_game()
        elif choice==2:
            load_game()
        elif choice==3:
            print("Thanks for playing!")
            break

if __name__=="__main__":
    main()