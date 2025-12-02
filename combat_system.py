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
    enemies = {
        "goblin": {"health": 50, "strength": 8, "magic": 2, "xp_reward": 25, "gold_reward": 10},
        "orc": {"health": 80, "strength": 12, "magic": 5, "xp_reward": 50, "gold_reward": 25},
        "dragon": {"health": 200, "strength": 25, "magic": 15, "xp_reward": 200, "gold_reward": 100}
    }

    if enemy_type not in enemies:
        raise InvalidTargetError(f"Enemy type '{enemy_type}' not recognized")
    
    stats = enemies[enemy_type]
    return {
        "name": enemy_type,
        "health": stats["health"],
        "max_health": stats["health"],
        "strength": stats["strength"],
        "magic": stats["magic"],
        "xp_reward": stats["xp_reward"],
        "gold_reward": stats["gold_reward"]
    }

def get_random_enemy_for_level(character_level):
    if character_level <= 2:
        enemy_type = "goblin"
    elif 3 <= character_level <= 5:
        enemy_type = "orc"
    else:
        enemy_type = "dragon"
    
    return create_enemy(enemy_type)

# ==========================
# HELPER FUNCTIONS
# ==========================
def display_battle_log(message):
    print(message)

def use_special_ability(character, enemy):
    damage = 10
    enemy['health'] -= damage
    return f"{character['name']} uses a special ability on {enemy['name']} for {damage} damage!"

# ==========================
# COMBAT SYSTEM
# ==========================
class SimpleBattle:
    def __init__(self, character, enemy=None):
        self.character = character
        if enemy is None:
            self.enemy = get_random_enemy_for_level(self.character['level'])
        else:
            self.enemy = enemy
        self.in_battle = True
        self.turn_count = 0

    def start_battle(self):
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
            if 'experience' not in self.character:
                self.character['experience'] = 0
            if 'gold' not in self.character:
                self.character['gold'] = 0
            self.character['experience'] += self.enemy['xp_reward']
            self.character['gold'] += self.enemy['gold_reward']
            return {'winner': 'player', 'xp_gained': self.enemy['xp_reward'], 'gold_gained': self.enemy['gold_reward']}
        else:
            return {'winner': 'enemy', 'xp_gained': 0, 'gold_gained': 0}

    def player_turn(self):
        if not self.in_battle:
            raise CombatNotActiveError("Cannot take a turn outside of battle")

        print("\nChoose your action:")
        print("1. Basic Attack")
        print("2. Special Ability")
        print("3. Try to Run")
        
        choice = input("Enter the number of your action: ").strip()

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
            return True
        return False

# ==========================
# TESTING BLOCK
# ==========================
if __name__ == "__main__":
    print("=== COMBAT SYSTEM TEST ===")
    
    try:
        goblin = create_enemy("goblin")
        print(f"Created {goblin['name']}")
    except InvalidTargetError as e:
        print(f"Invalid enemy: {e}")
    
    test_char = {
        'name': 'Hero',
        'class': 'Warrior',
        'level': 1,
        'health': 120,
        'max_health': 120,
        'strength': 15,
        'magic': 5,
        'experience': 0,
        'gold': 100
    }

    battle = SimpleBattle(test_char)
    try:
        result = battle.start_battle()
        print(f"Battle result: {result}")
    except CharacterDeadError:
        print("Character is dead!")