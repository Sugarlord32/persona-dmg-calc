import math
import random
import os

class GameState:
    def __init__(self):
        self.mode = "neutral"
        self.damage_multiplier = 20
        self.party_members = []
        self.shadows = []

    def reset(self):
        self.__init__()

class Character:
    def __init__(self, number, level, hp, strength, endurance, magic, agility, armor_stat=0, weapon_power=None):
        self.number = number
        self.level = level
        self.hp = hp
        self.strength = strength
        self.endurance = endurance
        self.magic = magic
        self.agility = agility
        self.armor_stat = armor_stat
        self.weapon_power = weapon_power
        self.downed = False
        self.baton_pass_count = 0

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_numeric_input(prompt, allow_float=True):
    while True:
        user_input = input(prompt).lower()
        if user_input == 'reset':
            return None
        try:
            return float(user_input) if allow_float else int(user_input)
        except ValueError:
            print("Invalid input. Please enter a numeric value.")

def get_element():
    elements = ['phys', 'fire', 'ice', 'elec', 'wind', 'psy', 'nuke', 'bless', 'curse', 'almighty']
    while True:
        element = input("Enter the element of the attack (Phys/Fire/Ice/Elec/Wind/Psy/Nuke/Bless/Curse/Almighty): ").lower()
        if element == 'reset':
            return None
        if element in elements:
            return element
        print("Invalid element. Please try again.")

def calculate_damage(attack_type, element, character):
    if attack_type == 'melee' or (attack_type == 'skill' and element == 'phys'):
        power = character.strength if isinstance(character, Character) else character['strength']
        stat = character.strength if isinstance(character, Character) else character['strength']
    else:
        power = get_numeric_input("Enter the skill power: ")
        stat = character.magic if isinstance(character, Character) else character['magic']
    
    damage = math.sqrt(power) * math.sqrt(stat)
    ailment = input("Enter target's ailment (burn/shock/freeze/dizzy/sleep/forget/confuse/fear/despair/rage/brainwash/none): ").lower()
    ailment = None if ailment == 'none' else ailment
    
    return damage, stat, ailment

def apply_defense(damage, endurance, armor_stat, ailment):
    endurance += (armor_stat or 0) / 10
    if ailment == 'dizzy':
        endurance = max(1, endurance - 10)
        print(f"Target is dizzy. Endurance reduced to {endurance}")
    return damage / math.sqrt(endurance * 8)

def apply_elemental_modifier(damage, element):
    while True:
        weakness = input(f"Is the target weak, strong, or neutral against {element}? (weak/strong/neutral): ").lower()
        if weakness == 'reset':
            return None, None
        if weakness in ['weak', 'strong', 'neutral']:
            modifiers = {'weak': 1.4, 'strong': 0.5, 'neutral': 1}
            return damage * modifiers[weakness], weakness
        print("Invalid input. Please enter 'weak', 'strong', or 'neutral'.")

def apply_technical(damage, element, ailment, weakness):
    if weakness == 'weak':
        return damage
    
    technical_map = {
        'burn': ['nuke', 'wind'],
        'shock': ['nuke', 'phys'],
        'freeze': ['nuke', 'phys'],
        'dizzy': ['any'],
        'sleep': ['any'],
        'forget': ['psy', 'elec'],
        'confuse': ['psy', 'wind'],
        'fear': ['psy', 'ice'],
        'despair': ['psy', 'curse'],
        'rage': ['psy', 'fire'],
        'brainwash': ['psy', 'bless']
    }
    
    if ailment in technical_map and (element in technical_map[ailment] or 'any' in technical_map[ailment]):
        print("Technical hit!")
        return damage * 1.4
    return damage

def apply_level_difference(damage, attacker_level, target_level):
    level_diff = attacker_level - target_level
    if -4 <= level_diff <= 1:
        return damage
    elif level_diff > 1:
        multiplier = min(1.5, 1 + (level_diff - 1) * 0.05)
    else:
        multiplier = max(0.5, 1 - (abs(level_diff) - 4) * 0.05)
    return damage * multiplier

def setup_battle(game_state):
    num_party = get_numeric_input("Enter the number of party members: ", allow_float=False)
    if num_party is None:
        return False
    
    game_state.party_members = [
        Character(
            i+1,
            get_numeric_input(f"Enter level for Party Member {i+1}: ", allow_float=False),
            get_numeric_input(f"Enter HP for Party Member {i+1}: "),
            get_numeric_input(f"Enter strength stat for Party Member {i+1}: "),
            get_numeric_input(f"Enter endurance for Party Member {i+1}: "),
            get_numeric_input(f"Enter magic stat for Party Member {i+1}: "),
            get_numeric_input(f"Enter agility stat for Party Member {i+1}: "),
            get_numeric_input(f"Enter armor stat for Party Member {i+1}: "),
            get_numeric_input(f"Enter weapon power for Party Member {i+1}: ")
        ) for i in range(num_party)
    ]
    
    setup_shadows(game_state)
    return True

def setup_shadows(game_state):
    num_shadows = get_numeric_input("Enter the number of shadows: ", allow_float=False)
    if num_shadows is None:
        return False
    
    game_state.shadows = [
        Character(
            i+1,
            get_numeric_input(f"Enter level for Shadow {i+1}: ", allow_float=False),
            get_numeric_input(f"Enter HP for Shadow {i+1}: "),
            get_numeric_input(f"Enter strength stat for Shadow {i+1}: "),
            get_numeric_input(f"Enter endurance for Shadow {i+1}: "),
            get_numeric_input(f"Enter magic stat for Shadow {i+1}: "),
            get_numeric_input(f"Enter agility stat for Shadow {i+1}: ")
        ) for i in range(num_shadows)
    ]
    return True

def check_battle_end(game_state):
    if all(shadow.hp <= 0 for shadow in game_state.shadows):
        print("Party Wins!")
        game_state.mode = get_side_input("Which side should start first for the next battle? (party/shadow): ")
        return setup_shadows(game_state)
    elif all(member.hp <= 0 for member in game_state.party_members):
        print("Shadows Win!")
        game_state.mode = get_side_input("Which side should start first for the next battle? (party/shadow): ")
        return setup_battle(game_state)
    return True

def get_side_input(prompt):
    while True:
        side = input(prompt).lower()
        if side in ['party', 'shadow']:
            return side
        print("Invalid input. Please enter 'party' or 'shadow'.")

def get_turn_order(game_state):
    return sorted(game_state.party_members + game_state.shadows, key=lambda x: x.agility, reverse=True)

def calculate_single_attack(attack_input, element, attacker, target, ailment=None, crit_chance=0):
    damage, stat, ailment = calculate_damage(attack_input, element, attacker)
    damage = apply_defense(damage, target.endurance, target.armor_stat, ailment)
    damage, weakness = apply_elemental_modifier(damage, element)
    if weakness is None:
        return None, None

    is_crit = (ailment in ['shock', 'freeze'] or random.random() < (crit_chance / 100))
    if is_crit:
        damage *= 1.5
        print("Critical hit!")
    elif not is_crit:
        damage = apply_technical(damage, element, ailment, weakness)
    
    damage = apply_level_difference(damage, attacker.level, target.level)
    return damage, weakness

def handle_one_more(attacker, is_party_member):
    print(f"One More! for {'Party Member' if is_party_member else 'Shadow'} {attacker.number}")
    if is_party_member:
        action = input("Choose action (attack/baton pass): ").lower()
        if action == 'baton pass':
            return handle_baton_pass(attacker)
    return [attacker]

def handle_baton_pass(passer, game_state):
    while True:
        receiver_num = get_numeric_input("Enter the number of the party member to receive the baton: ", allow_float=False)
        if receiver_num is None:
            return None
        if 1 <= receiver_num <= len(game_state.party_members):
            receiver = game_state.party_members[receiver_num - 1]
            if receiver.number != passer.number:
                receiver.baton_pass_count = min(passer.baton_pass_count + 1, 3)
                boost_percentage = min(receiver.baton_pass_count * 25 + 25, 100)
                print(f"Baton passed to Party Member {receiver.number}. Damage boost: +{boost_percentage}%")
                return [receiver]
        print("Invalid party member number or same as passer. Please try again.")

def all_out_attack(game_state):
    total_damage = sum(calculate_damage('melee', 'phys', member)[0] for member in game_state.party_members if member.hp > 0)
    print(f"\nTotal damage before multiplier: {total_damage:.2f}")
    
    multiplied_damage = total_damage * game_state.damage_multiplier
    print(f"Final all-out attack damage (multiplied by {game_state.damage_multiplier}): {multiplied_damage:.2f}")
    
    for shadow in game_state.shadows:
        if shadow.hp > 0:
            damage = apply_defense(multiplied_damage, shadow.endurance, 0, None)
            shadow.hp = max(0, round(shadow.hp - damage))
            print(f"Shadow {shadow.number} took {round(damage)} damage. Remaining HP: {shadow.hp}")
        shadow.downed = False

def change_multiplier(game_state):
    new_multiplier = get_numeric_input("Enter new damage multiplier: ")
    if new_multiplier is not None:
        game_state.damage_multiplier = new_multiplier
        print(f"Damage multiplier changed to {game_state.damage_multiplier}")

def display_menu(game_state):
    print("\nPersona Damage Calculator")
    print("Attack types:")
    print("  1. Melee")
    print("  2. Skill")
    print("  3. All-out")
    print("Modes:")
    print("  4. Party")
    print("  5. Shadow")
    print("  6. Neutral")
    print("Other commands:")
    print("  7. Multi (Change damage multiplier)")
    print("  8. Reset")
    print(f"\nCurrent mode: {game_state.mode.capitalize()}")

def handle_neutral_mode(game_state, attack_type):
    if attack_type in ['melee', 'skill']:
        armor_stat = get_numeric_input("Enter target's armor stat: ")
        crit_chance = get_numeric_input("Enter critical hit chance (%): ") if attack_type == 'melee' else 0
        element = 'phys' if attack_type == 'melee' else get_element()
        if element is None:
            return

        attacker = Character(1, 
                             get_numeric_input("Enter attacker level: ", allow_float=False),
                             100,  # dummy HP
                             get_numeric_input("Enter strength stat: "),
                             1,  # dummy endurance
                             get_numeric_input("Enter magic stat: "),
                             1,  # dummy agility
                             weapon_power=get_numeric_input("Enter weapon power: ") if attack_type == 'melee' else None)
        
        target = Character(1,
                           get_numeric_input("Enter target level: ", allow_float=False),
                           100,  # dummy HP
                           1,  # dummy strength
                           get_numeric_input("Enter target's endurance: "),
                           1,  # dummy magic
                           1,  # dummy agility
                           armor_stat)

        final_damage, _ = calculate_single_attack(attack_type, element, attacker, target, crit_chance=crit_chance)
        
    elif attack_type == 'all-out':
        num_party_members = get_numeric_input("Enter the number of party members: ", allow_float=False)
        total_damage = 0
        for i in range(num_party_members):
            member = Character(i+1,
                               get_numeric_input(f"Enter level for member {i+1}: ", allow_float=False),
                               100,  # dummy HP
                               get_numeric_input(f"Enter strength stat for member {i+1}: "),
                               1,  # dummy endurance
                               1,  # dummy magic
                               1,  # dummy agility
                               weapon_power=get_numeric_input(f"Enter weapon power for member {i+1}: "))
            member_damage, _ = calculate_single_attack('melee', 'phys', member, Character(1, 1, 100, 1, 1, 1, 1))
            total_damage += member_damage
            print(f"Party Member {i+1}: {member_damage:.2f}")
        
        print(f"\nTotal damage before multiplier: {total_damage:.2f}")
        final_damage = total_damage * game_state.damage_multiplier
        print(f"Total all-out attack damage (multiplied by {game_state.damage_multiplier}): {final_damage:.2f}")

        target_endurance = get_numeric_input("Enter target's endurance: ")
        target_level = get_numeric_input("Enter target's level: ", allow_float=False)
        avg_party_level = get_numeric_input("Enter average party level: ", allow_float=False)
        
        final_damage = apply_defense(final_damage, target_endurance, 0, None)
        final_damage = apply_level_difference(final_damage, avg_party_level, target_level)
        
    else:
        print("Invalid attack type. Please enter a valid command.")
        return

    if final_damage is not None:
            multiplied_damage = final_damage * game_state.damage_multiplier
            rounded_damage = round(multiplied_damage)
            print(f"Final damage: {final_damage:.2f}")
            print(f"Final damage (multiplied by {game_state.damage_multiplier} and rounded): {rounded_damage}")

def main():
    game_state = GameState()
    
    while True:
        display_menu(game_state)
        user_input = input("Enter command number or name: ").lower()
        
        command_map = {
            '1': 'melee', 'melee': 'melee',
            '2': 'skill', 'skill': 'skill',
            '3': 'all-out', 'all-out': 'all-out',
            '4': 'party', 'party': 'party',
            '5': 'shadow', 'shadow': 'shadow',
            '6': 'neutral', 'neutral': 'neutral',
            '7': 'multi', 'multi': 'multi',
            '8': 'reset', 'reset': 'reset'
        }
        
        user_input = command_map.get(user_input, user_input)
        
        if user_input == 'reset':
            game_state.reset()
            clear_console()
            continue
        
        if user_input in ['party', 'shadow', 'neutral']:
            game_state.mode = user_input
            if game_state.mode != 'neutral' and not setup_battle(game_state):
                continue
            print(f"Switched to {game_state.mode} mode.")
            continue
        
        if user_input == 'multi':
            change_multiplier(game_state)
            continue
        
        if game_state.mode in ["party", "shadow"]:
            turn_order = get_turn_order(game_state)
            i = 0
            while i < len(turn_order):
                character = turn_order[i]
                is_party_member = character in game_state.party_members

                print(f"\nTurn for {'Party Member' if is_party_member else 'Shadow'} {character.number}")

                if character.hp <= 0:
                    print(f"{'Party Member' if is_party_member else 'Shadow'} {character.number} is defeated and skips their turn.")
                    i += 1
                    continue
                
                character.downed = False
                
                attack_input = input("Enter attack type (melee/skill/all-out): ").lower()
                if attack_input == 'reset':
                    game_state.reset()
                    break
                
                if attack_input not in ['melee', 'skill', 'all-out']:
                    print("Invalid attack type. Please enter a valid command.")
                    continue

                if attack_input == 'all-out' and is_party_member:
                    if all(shadow.downed for shadow in game_state.shadows):
                        all_out_attack(game_state)
                        if not check_battle_end(game_state):
                            break
                        i += 1
                        continue
                    else:
                        print("Cannot perform All-Out Attack. Not all enemies are downed.")
                        continue

                # target selection
                targets = []
                if is_party_member:
                    target_input = input("Enter the number of the shadow to attack (or 0 for all): ")
                    if target_input == '0':
                        targets = game_state.shadows
                    elif target_input.isdigit() and 1 <= int(target_input) <= len(game_state.shadows):
                        targets = [game_state.shadows[int(target_input) - 1]]
                    else:
                        print("Invalid shadow number.")
                        continue
                else:
                    target_input = input("Enter the number of the party member to attack (or 0 for all): ")
                    if target_input == '0':
                        targets = game_state.party_members
                    elif target_input.isdigit() and 1 <= int(target_input) <= len(game_state.party_members):
                        targets = [game_state.party_members[int(target_input) - 1]]
                    else:
                        print("Invalid party member number.")
                        continue

                element = 'phys' if attack_input == 'melee' else get_element()
                if element is None:
                    break

                crit_chance = 0
                if attack_input == 'melee' or (attack_input == 'skill' and element == 'phys'):
                    crit_chance = get_numeric_input("Enter critical hit chance (%): ")

                one_more = False
                for target in targets:
                    final_damage, weakness = calculate_single_attack(attack_input, element, character, target, crit_chance=crit_chance)
                    if final_damage is None:
                        break

                    if is_party_member:
                        baton_boost = 1 + min(character.baton_pass_count * 0.25 + 0.25, 1.0)
                        final_damage *= baton_boost

                    multiplied_damage = final_damage * game_state.damage_multiplier
                    rounded_damage = round(multiplied_damage)
                    print(f"Final damage against {target.number}: {final_damage:.2f}")
                    print(f"Final damage (multiplied by {game_state.damage_multiplier} and rounded): {rounded_damage}")

                    target.hp = max(0, round(target.hp - rounded_damage))
                    print(f"Remaining HP for {'Shadow' if is_party_member else 'Party Member'} {target.number}: {target.hp}")

                    if not check_battle_end(game_state):
                        break

                    if target.hp <= 0:
                        turn_order = [char for char in turn_order if char != target]
                        
                    if weakness == 'weak' or (attack_input == 'melee' or (attack_input == 'skill' and element == 'phys')) and random.random() < (crit_chance / 100):
                        target.downed = True
                        one_more = True
                        print(f"{'Shadow' if is_party_member else 'Party Member'} {target.number} is downed!")

                if one_more:
                    extra_turns = handle_one_more(character, is_party_member)
                    if extra_turns:
                        turn_order[i+1:i+1] = extra_turns
                
                i += 1

            if not check_battle_end(game_state):
                continue
        
        else:  # neutral mode
            handle_neutral_mode(game_state, user_input)

        input("\nPress enter key to continue...")

if __name__ == "__main__":
    main()
