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
def create_enemy(enemy_type):
    """
    Create an enemy based on type

    Example enemy types and stats:
    - goblin: health=50, strength=8, magic=2, xp_reward=25, gold_reward=10
    - orc: health=80, strength=12, magic=5, xp_reward=50, gold_reward=25
    - dragon: health=200, strength=25, magic=15, xp_reward=200, gold_reward=100

    Returns: Enemy dictionary
    Raises: InvalidTargetError if enemy_type not recognized
    """
    enemies = {
        "goblin": {
            "name": "Goblin",
            "type": "Goblin",
            "health": 30,
            "max_health": 30,
            "strength": 5,
            "magic": 0,
            "xp_reward": 10,
            "gold_reward": 5
        },
        "orc": {
            "name": "Orc",
            "type": "Orc",
            "health": 50,
            "max_health": 50,
            "strength": 12,
            "magic": 2,
            "xp_reward": 20,
            "gold_reward": 12
        },
        "dragon": {
            "name": "Dragon",
            "type": "Dragon",
            "health": 200,
            "max_health": 200,
            "strength": 25,
            "magic": 15,
            "xp_reward": 200,
            "gold_reward": 100
        }
    }

    enemy_type = enemy_type.lower()  # normalize input

    if enemy_type not in enemies:
        raise InvalidTargetError(f"Unknown enemy: {enemy_type}")

    e = enemies[enemy_type]
    return {
        "name": e["name"],
        "type": e["type"],
        "health": e["health"],
        "max_health": e["max_health"],
        "strength": e["strength"],
        "magic": e["magic"],
        "xp_reward": e["xp_reward"],
        "gold_reward": e["gold_reward"]
    }


def get_random_enemy_for_level(character_level):
    """
    Get an appropriate enemy for character's level

    Level 1-2: Goblins
    Level 3-5: Orcs
    Level 6+: Dragons

    Returns: Enemy dictionary
    """
    if character_level in range(1, 3):
        return create_enemy("goblin")
    elif character_level in range(3, 6):
        return create_enemy("orc")
    elif character_level >= 6:
        return create_enemy("dragon")


# ============================================================================ 
# COMBAT SYSTEM
# ============================================================================ 

class SimpleBattle:
    """
    Simple turn-based combat system

    Manages combat between character and enemy
    """

    def __init__(self, character, enemy):
        """
        Initialize battle with character and enemy
        """
        self.character = character
        self.enemy = enemy
        self.combat_active = True
        self.turn_counter = 0
        self.battle_result = None

    def start_battle(self):
        """
        Start the combat loop

        Returns: Dictionary with battle results:
        {'winner': 'player'|'enemy', 'xp_gained': int, 'gold_gained': int}
        Raises: CharacterDeadError if character is already dead
        """
        from character_manager import is_character_dead

        if is_character_dead(self.character):
            raise CharacterDeadError("Character is already dead, cannot start battle.")

        self.turn_counter = 1
        battle_results = {"winner": None, "xp_gained": 0, "gold_gained": 0}

        # TODO: Implement actual battle loop
        return battle_results

    def player_turn(self):
        """
        Handle player's turn
        """
        if not self.combat_active:
            raise CombatNotActiveError("No battles active.")

        print("\n=== PLAYER TURN ===")
        print("1. Basic Attack")
        print("2. Special Ability")
        print("3. Run Away")

        player_choice = input(
            "Choose your move!:\n1: Basic Attack\n2: Heavy Attack (Special Ability)\n3: Run Away\n"
        )

        if player_choice == "1":  # Basic Attack
            damage = self.character["strength"]
            self.enemy["health"] -= damage
            print(f'{self.character["name"]} chose Basic Attack: Dealt {damage} damage.')

        elif player_choice == "2":  # Special Ability / Heavy Attack
            damage = self.character["strength"] + 5
            self.enemy["health"] -= damage
            print(f'{self.character["name"]} chose Heavy Attack: Dealt {damage} damage.')

        elif player_choice == "3":  # Run Away
            escape_chance = self.enemy["strength"] // 5
            if self.character["level"] >= escape_chance:
                print("You successfully ran away!")
                self.combat_active = False
                self.battle_result = {"winner": "none", "xp_gained": 0, "gold_gained": 0}
                return
            else:
                print("You were not strong enough to escape!")

        # Check for enemy death
        if self.enemy["health"] <= 0:
            print(f"The {self.enemy['type']} has been defeated!")
            self.combat_active = False
            self.battle_result = {
                "winner": "player",
                "xp_gained": self.enemy.get("xp_reward", 20),
                "gold_gained": self.enemy.get("gold_reward", 10)
            }

        self.turn_counter += 1

    def enemy_turn(self):
        """
        Handle enemy's turn - simple AI
        """
        if not self.combat_active:
            raise CombatNotActiveError("No battles active.")

        print("\n=== ENEMY TURN ===")
        damage = self.enemy["strength"]
        self.character["health"] -= damage
        print(f"The {self.enemy['type']} attacks you for {damage} damage!")

        if self.character["health"] <= 0:
            print("You have been defeated...")
            self.combat_active = False
            self.battle_result = {"winner": "enemy", "xp_gained": 0, "gold_gained": 0}

    def calculate_damage(self, attacker, defender):
        """
        Calculate damage from attack
        """
        damage_amount = attacker["strength"] - (defender["strength"] // 4)
        return max(int(damage_amount), 1)

    def apply_damage(self, target, damage):
        """
        Apply damage to a character or enemy
        """
        target["health"] -= damage
        if target["health"] < 0:
            target["health"] = 0

    def check_battle_end(self):
        """
        Check if battle is over
        """
        if self.character["health"] <= 0:
            return "enemy"
        if self.enemy["health"] <= 0:
            return "player"
        return None

    def attempt_escape(self):
        """
        Try to escape from battle
        """
        if self.character["magic"] > self.enemy["strength"]:
            self.combat_active = False
            return True
        return False


# ============================================================================ 
# SPECIAL ABILITIES
# ============================================================================ 

def use_special_ability(character, enemy):
    """
    Use character's class-specific special ability
    """
    if character["class"] == "Warrior":
        return warrior_power_strike(character, enemy)
    elif character["class"] == "Mage":
        return mage_fireball(character, enemy)
    elif character["class"] == "Rogue":
        return rogue_critical_strike(character, enemy)
    elif character["class"] == "Cleric":
        return cleric_heal(character)
    else:
        return "No special ability available."


def warrior_power_strike(character, enemy):
    damage = character["strength"] * 2
    enemy["health"] -= damage
    return f'{character["name"]} used Power Strike for {damage} damage!'


def mage_fireball(character, enemy):
    damage = character["magic"] * 2
    enemy["health"] -= damage
    return f'{character["name"]} cast Fireball for {damage} damage!'


def rogue_critical_strike(character, enemy):
    crit = (enemy["health"] % 2 == 0)
    if crit:
        damage = character["strength"] * 3
        enemy["health"] -= damage
        return f'{character["name"]} landed a CRITICAL STRIKE for {damage} damage!'
    else:
        damage = character["strength"]
        enemy["health"] -= damage
        return f'{character["name"]} attacked for {damage} damage.'


def cleric_heal(character):
    heal_amount = 30
    character["health"] = min(character["health"] + heal_amount, character["max_health"])
    return f'{character["name"]} healed for {heal_amount} HP!'


# ============================================================================ 
# COMBAT UTILITIES
# ============================================================================ 

def can_character_fight(character, combat_active):
    if character["health"] > 0 and not combat_active:
        print("Character is available for battle")
        return True
    return False


def get_victory_rewards(enemy):
    return {
        "xp": enemy.get("xp_reward", 0),
        "gold": enemy.get("gold_reward", 0)
    }


def display_combat_stats(character, enemy):
    print(f"\n{character['name']}: HP={character['health']}/{character['max_health']}")
    print(f"{enemy['name']}: HP={enemy['health']}/{enemy['max_health']}")


def display_battle_log(message):
    print(f">>> {message}")