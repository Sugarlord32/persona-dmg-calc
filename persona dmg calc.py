import math # janks ass code incoming
import random
import os

global mode, target_hp, damage_multiplier, party_members, shadows, advantage_mode

target_hp = None
damage_multiplier = 20
mode = "neutral"
party_members = []
shadows = []
advantage_mode = None

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_numeric_input(prompt, allow_float=True):
    while True:
        user_input = input(prompt).lower()
        if user_input == 'reset':
            reset()
            return None
        try:
            if allow_float:
                return float(user_input)
            else:
                return int(user_input)
        except ValueError:
            print("Invalid input. Please enter a numeric value.")

def get_element():
    elements = ['phys', 'fire', 'ice', 'elec', 'wind', 'psy', 'nuke', 'bless', 'curse', 'almighty']
    while True:
        element = input("Enter the element of the attack (Phys/Fire/Ice/Elec/Wind/Psy/Nuke/Bless/Curse/Almighty): ").lower()
        if element == 'reset':
            reset()
            return None
        if element in elements:
            return element
        print("Invalid element. Please try again.")

def calculate_damage(attack_input, element=None, character=None):
    if attack_input == 'melee':
        is_shadow = 'weapon_power' not in character
        if is_shadow:
            power = character['strength']  # use str as wpn pwr for shadows
        else:
            power = character['weapon_power']  # use wpn pwr for party members
        stat = character['strength']
    elif attack_input == 'skill':
        power = get_numeric_input("Enter the skill power: ")
        if element == 'phys':
            stat = character['strength']
        else:  # magical skill
            stat = character['magic']
    else:
        raise ValueError("Invalid attack input")

    damage = math.sqrt(power) * math.sqrt(stat)

    ailment = input("Enter target's ailment (burn, shock, freeze, dizzy, sleep, forget, confuse, fear, despair, rage, brainwash or none): ").lower()
    ailment = None if ailment == 'none' else ailment
    
    return damage, stat, ailment

def apply_defense(damage, endurance, armor_stat, ailment):
    if armor_stat is None: # if the bugfix works it works
        armor_stat = 0

    endurance += armor_stat / 10

    if ailment == 'dizzy':
        endurance = max(1, endurance - 10)  # prevents endurance from going below 1
        print(f"Target is dizzy. Endurance reduced to {endurance}")
    final_damage = damage / math.sqrt(endurance * 8)
    return final_damage

def apply_elemental_modifier(damage, element):
    while True:
        weakness = input(f"Is the target weak, strong, or neutral against {element}? (weak/strong/neutral): ").lower()
        if weakness == 'reset':
            reset()
            return None, None
        if weakness in ['weak', 'strong', 'neutral']:
            if weakness == 'weak':
                return damage * 1.4, weakness
            elif weakness == 'strong':
                return damage * 0.5, weakness
            else:
                return damage, weakness
        print("Invalid input. Please enter 'weak', 'strong', or 'neutral'.")

def apply_technical(damage, element, ailment, weakness):
    if weakness == 'weak':
        return damage  # weak overrides technical
    
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
        return damage * multiplier
    else:  # level_diff < -4
        multiplier = max(0.5, 1 - (abs(level_diff) - 4) * 0.05)
        return damage * multiplier

def setup_battle():
    global party_members, shadows, advantage_mode
    if mode in ["party", "shadow"]:
        num_party = get_numeric_input("Enter the number of party members: ", allow_float=False)
        if num_party is None:
            return False
        party_members = []
        for i in range(num_party):
            member = {
                'number': i+1,
                'level': get_numeric_input(f"Enter level for Party Member {i+1}: ", allow_float=False),
                'hp': get_numeric_input(f"Enter HP for Party Member {i+1}: "),
                'weapon_power': get_numeric_input(f"Enter weapon power for Party Member {i+1}: "),
                'endurance': get_numeric_input(f"Enter endurance for Party Member {i+1}: "),
                'strength': get_numeric_input(f"Enter strength stat for Party Member {i+1}: "),
                'magic': get_numeric_input(f"Enter magic stat for Party Member {i+1}: "),
                'agility': get_numeric_input(f"Enter agility stat for Party Member {i+1}: "),
                'armor_stat': get_numeric_input(f"Enter armor stat for Party Member {i+1}: "),
                'downed': False,
                'baton_pass_count': 0
            }
            party_members.append(member)
    
    if mode in ["party", "shadow"]:
        setup_shadows()
    
    advantage_mode = input("Which side should start first? (party/shadow/neutral): ").lower()
    if advantage_mode == "party":
        print("Party Advantage!")
    elif advantage_mode == "shadow":
        print("Shadow Advantage!")
    elif advantage_mode == "neutral":
        print("Neutral start. Turn order will be decided by agility.")
    else:
        print("Invalid input. Defaulting to neutral start.")
        advantage_mode = "neutral"
    
    return True


def setup_shadows():
    global shadows
    num_shadows = get_numeric_input("Enter the number of shadows: ", allow_float=False)
    if num_shadows is None:
        return False
    shadows = []
    for i in range(num_shadows):
        shadow = {
            'number': i+1,
            'level': get_numeric_input(f"Enter level for Shadow {i+1}: ", allow_float=False),
            'hp': get_numeric_input(f"Enter HP for Shadow {i+1}: "),
            'strength': get_numeric_input(f"Enter strength stat for Shadow {i+1}: "),
            'endurance': get_numeric_input(f"Enter endurance for Shadow {i+1}: "),
            'magic': get_numeric_input(f"Enter magic stat for Shadow {i+1}: "),
            'agility': get_numeric_input(f"Enter agility stat for Shadow {i+1}: "),
            'armor_stat': 0,
            'downed': False
        }
        shadows.append(shadow)
    return True

def check_battle_end():
    global mode, advantage_mode
    if all(shadow['hp'] <= 0 for shadow in shadows):
        print("Party Wins!")
        # Reset downed state for all shadows
        for shadow in shadows:
            shadow['downed'] = False
        if not setup_shadows():
            return False
    elif all(member['hp'] <= 0 for member in party_members):
        print("Shadows Win!")
        if not setup_battle():
            return False
    else:
        return True  # Battle continues

    # Ask for advantage mode for the next battle
    while True:
        next_advantage = input("Which side should start first for the next battle? (party/shadow/neutral): ").lower()
        if next_advantage in ['party', 'shadow', 'neutral']:
            advantage_mode = next_advantage
            if advantage_mode == "party":
                print("Party Advantage!")
            elif advantage_mode == "shadow":
                print("Shadow Advantage!")
            else:
                print("Neutral start. Turn order will be decided by agility.")
            break
        else:
            print("Invalid input. Please enter 'party', 'shadow', or 'neutral'.")

    return True

def get_turn_order():
    global advantage_mode
    all_characters = party_members + shadows
    if advantage_mode == "party":
        return party_members * 2 + sorted(all_characters, key=lambda x: x['agility'], reverse=True)
    elif advantage_mode == "shadow":
        return shadows + sorted(all_characters, key=lambda x: x['agility'], reverse=True)
    else:  # neutral
        return sorted(all_characters, key=lambda x: x['agility'], reverse=True)

def calculate_single_attack(attack_input, element, attacker, target, armor_stat, ailment=None, crit_chance=0,):
    damage, stat, ailment = calculate_damage(attack_input, element, attacker) # does stat even do anything
    
    damage = apply_defense(damage, target['endurance'], armor_stat, ailment)
    
    damage, weakness = apply_elemental_modifier(damage, element)
    if weakness is None:
        return None, None

    # crits gave me pain this is so jank FUCK if you're reading and want to fork please make everything better
    is_crit = False
    if (attack_input == 'melee' or (attack_input == 'skill' and element == 'phys')):
        if ailment in ['shock', 'freeze']:
            is_crit = True
        elif random.random() < (crit_chance / 100):
            is_crit = True
    
    if is_crit:
        damage *= 1.5
        print("Critical hit!")
    elif not is_crit:  # only apply technical if not a crit idk if this works
        damage = apply_technical(damage, element, ailment, weakness)
    
    damage = apply_level_difference(damage, attacker['level'], target['level'])
    
    return damage, weakness

def handle_one_more(attacker, is_party_member):
    print(f"One More! for {'Party Member' if is_party_member else 'Shadow'} {attacker['number']}")
    if is_party_member:
        action = input("Choose action (attack/baton pass): ").lower()
        if action == 'baton pass':
            return handle_baton_pass(attacker)
    return [attacker]

def handle_baton_pass(passer):
    while True:
        receiver_num = get_numeric_input("Enter the number of the party member to receive the baton: ", allow_float=False)
        if receiver_num is None:
            return None
        if 1 <= receiver_num <= len(party_members):
            receiver = party_members[receiver_num - 1]
            if receiver['number'] != passer['number']:
                receiver['baton_pass_count'] = min(passer['baton_pass_count'] + 1, 3)
                boost_percentage = min(receiver['baton_pass_count'] * 25 + 25, 100)
                print(f"Baton passed to Party Member {receiver['number']}. Damage boost: +{boost_percentage}%")
                return [receiver]
        print("Invalid party member number or same as passer. Please try again.")

def all_out_attack():
    total_damage = 0
    individual_damages = []
    for member in party_members:
        if member['hp'] > 0:
            member_damage, _, _ = calculate_damage('melee', 'phys', member)
            individual_damages.append(member_damage)
            total_damage += member_damage

    print("\nIndividual damages before multiplier:")
    for i, damage in enumerate(individual_damages, 1):
        print(f"Party Member {i}: {damage:.2f}")
    
    print(f"\nTotal damage before multiplier: {total_damage:.2f}")
    
    multiplied_damage = total_damage * damage_multiplier
    print(f"Final all-out attack damage (multiplied by {damage_multiplier}): {multiplied_damage:.2f}")
    
    for shadow in shadows:
        if shadow['hp'] > 0:
            damage = apply_defense(multiplied_damage, shadow['endurance'], 0, None)
            shadow['hp'] = max(0, round(shadow['hp'] - damage))
            print(f"Shadow {shadow['number']} took {round(damage)} damage. Remaining HP: {shadow['hp']}")
        shadow['downed'] = False  # reset downed after all-out

def change_multiplier():
    global damage_multiplier
    new_multiplier = get_numeric_input("Enter new damage multiplier: ")
    if new_multiplier is not None:
        damage_multiplier = new_multiplier
        print(f"Damage multiplier changed to {damage_multiplier}")

def reset():
    mode = "neutral" # will fix eventually look at those gray names
    party_members = []
    shadows = []
    target_hp = None
    damage_multiplier = 20
    print("Reset complete. All variables have been reset to their initial state.")
    clear_console()
    display_menu()

def display_menu():
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
    print(f"\nCurrent mode: {mode.capitalize()}")

def main():
    global mode, party_members, shadows, target_hp, is_crit, advantage_mode
    
    while True:
        display_menu()
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
            reset()
            continue
        
        if user_input in ['party', 'shadow', 'neutral']:
            mode = user_input
            if mode != 'neutral' and not setup_battle():
                continue
            print(f"Switched to {mode} mode.")
            continue
        
        if user_input == 'multi':
            change_multiplier()
            continue
        
        if mode in ["party", "shadow"]:
            turn_order = get_turn_order()
            i = 0
            while i < len(turn_order):
                character = turn_order[i]
                is_party_member = character in party_members
                is_shadow = character in shadows

                print(f"\nTurn for {'Party Member' if is_party_member else 'Shadow'} {character['number']}")
                
                character['downed'] = False
                
                attack_input = input("Enter attack type (melee/skill/all-out): ").lower()
                if attack_input == 'reset':
                    reset()
                    break
                
                if attack_input not in ['melee', 'skill', 'all-out']:
                    print("Invalid attack type. Please enter a valid command.")
                    continue

                if attack_input == 'all-out' and is_party_member:
                    if all(shadow['downed'] for shadow in shadows if shadow['hp'] > 0):
                        all_out_attack()
                        if not check_battle_end():
                            break
                        i += 1
                        continue
                    else:
                        print("Cannot perform All-Out Attack. Not all enemies are downed.")
                        continue

                # target selection
                if is_party_member:
                    while True:
                        target_input = input("Enter the number of the shadow to attack (or 0 for all): ")
                        if target_input == '0':
                            targets = [shadow for shadow in shadows if shadow['hp'] > 0]
                            if not targets:
                                print("All shadows have been defeated. Please end the battle.")
                                continue
                            break
                        elif target_input.isdigit() and 1 <= int(target_input) <= len(shadows):
                            target = shadows[int(target_input) - 1]
                            if target['hp'] <= 0:
                                print("This shadow has already been defeated. Please choose another target.")
                                continue
                            targets = [target]
                            break
                        else:
                            print("Invalid shadow number.")
                else:
                    while True:
                        target_input = input("Enter the number of the party member to attack (or 0 for all): ")
                        if target_input == '0':
                            targets = [member for member in party_members if member['hp'] > 0]
                            if not targets:
                                print("All party members have been defeated. Please end the battle.")
                                continue
                            break
                        elif target_input.isdigit() and 1 <= int(target_input) <= len(party_members):
                            target = party_members[int(target_input) - 1]
                            if target['hp'] <= 0:
                                print("This party member has already been defeated. Please choose another target.")
                                continue
                            targets = [target]
                            break
                        else:
                            print("Invalid party member number.")

                element = 'phys' if attack_input == 'melee' else get_element()
                if element is None:
                    break

                one_more = False
                for target in targets:
                    ailment = None

                    crit_chance = 0
                    if attack_input == 'melee' or (attack_input == 'skill' and element == 'phys'):
                        crit_chance = get_numeric_input("Enter critical hit chance (%): ")
                    
                    final_damage, weakness = calculate_single_attack(attack_input, element, character, target, target['armor_stat'], ailment, crit_chance)
                    if final_damage is None:
                        break

                    is_crit = False
                    if (attack_input == 'melee' or (attack_input == 'skill' and element == 'phys')):
                        if ailment in ['shock', 'freeze']:
                            is_crit = True
                        elif random.random() < (crit_chance / 100):
                            is_crit = True

                    if is_crit:
                        final_damage *= 1.5
                        print("Critical hit!")

                    if is_party_member:
                        baton_boost = 1 + min(character['baton_pass_count'] * 0.25 + 0.25, 1.0)
                        final_damage *= baton_boost

                    multiplied_damage = final_damage * damage_multiplier
                    rounded_damage = round(multiplied_damage)
                    print(f"Final damage against {target['number']}: {final_damage:.2f}")
                    print(f"Final damage (multiplied by {damage_multiplier} and rounded): {rounded_damage}")

                    target['hp'] = max(0, round(target['hp'] - rounded_damage))
                    print(f"Remaining HP for {'Shadow' if is_party_member else 'Party Member'} {target['number']}: {target['hp']}")

                    if target['hp'] <= 0:
                        turn_order = [char for char in turn_order if char != target]
                        
                    if (weakness == 'weak' or is_crit) and not all(shadow['hp'] <= 0 for shadow in shadows):
                        target['downed'] = True
                        one_more = True
                        print(f"{'Shadow' if is_party_member else 'Party Member'} {target['number']} is downed!")

                if one_more:
                    extra_turns = handle_one_more(character, is_party_member)
                    if extra_turns:
                        turn_order[i+1:i+1] = extra_turns
                
                i += 1

                # Reset advantage mode after the first round
                if advantage_mode in ["party", "shadow"] and i >= len(party_members) + len(shadows):
                    print("Advantage turn(s) completed. Returning to normal turn order.")
                    advantage_mode = "neutral"
                    turn_order = get_turn_order()
                    i = 0

            if not check_battle_end():
                continue
        
        else:  # neutral mode
            if user_input in ['melee', 'skill']:
                armor_stat = get_numeric_input("Enter target's armor stat: ")

                crit_chance = 0
                if user_input == 'melee':
                    crit_chance = get_numeric_input("Enter critical hit chance (%): ")
                
                if user_input == 'melee':
                    final_damage, _ = calculate_single_attack('melee', 'phys', 
                        {'number': 1, 'weapon_power': get_numeric_input("Enter weapon power: "), 
                         'strength': get_numeric_input("Enter strength stat: "), 
                         'level': get_numeric_input("Enter attacker level: ", allow_float=False)}, 
                        {'endurance': get_numeric_input("Enter target's endurance: "), 
                         'level': get_numeric_input("Enter target level: ", allow_float=False)},
                        armor_stat, ailment, crit_chance)
                elif user_input == 'skill':

                    element = get_element()
                    if element is None:
                        continue

                    crit_chance = 0
                    if element == 'phys':
                        crit_chance = get_numeric_input("Enter critical hit chance (%): ")

                    final_damage, _ = calculate_single_attack('skill', element,
                        {'number': 1, 'magic': get_numeric_input("Enter magic stat: "), 
                         'level': get_numeric_input("Enter attacker level: ", allow_float=False)}, 
                        {'endurance': get_numeric_input("Enter target's endurance: "), 
                         'level': get_numeric_input("Enter target level: ", allow_float=False)},
                        armor_stat, crit_chance)
                    
            elif user_input == 'all-out':
                num_party_members = get_numeric_input("Enter the number of party members: ", allow_float=False)
                total_damage = 0
                individual_damages = []
                for i in range(num_party_members):
                    member_damage, _ = calculate_single_attack('melee', 'phys',
                        {'number': i+1, 'weapon_power': get_numeric_input(f"Enter weapon power for member {i+1}: "),
                        'strength': get_numeric_input(f"Enter strength stat for member {i+1}: "),
                        'level': get_numeric_input(f"Enter level for member {i+1}: ", allow_float=False)},
                        {'endurance': 1, 'level': 1})  # dummy target for calculation
                    individual_damages.append(member_damage)
                    total_damage += member_damage

                print("\nIndividual damages before multiplier:")
                for i, damage in enumerate(individual_damages, 1):
                    print(f"Party Member {i}: {damage:.2f}")
                
                print(f"\nTotal damage before multiplier: {total_damage:.2f}")
                
                multiplied_damage = total_damage * damage_multiplier
                print(f"Total all-out attack damage (multiplied by {damage_multiplier}): {multiplied_damage:.2f}")

                target_endurance = get_numeric_input("Enter target's endurance: ")
                target_level = get_numeric_input("Enter target's level: ", allow_float=False)
                
                final_damage = apply_defense(multiplied_damage, target_endurance, 0, None)
                final_damage = apply_level_difference(final_damage, get_numeric_input("Enter average party level: ", allow_float=False), target_level)
                
                print(f"Final damage after applying target's defense: {final_damage:.2f}")

                continue

            else:
                print("Invalid attack type. Please enter a valid command number or name.")
                continue

            if final_damage is None:
                continue

            multiplied_damage = final_damage * damage_multiplier
            rounded_damage = round(multiplied_damage)
            print(f"Final damage: {final_damage:.2f}")
            print(f"Final damage (multiplied by {damage_multiplier} and rounded): {rounded_damage}")

            if target_hp is not None: # does this even do anything
                target_hp = max(0, round(target_hp - rounded_damage))
                if target_hp <= 0:
                    print("Target HP reduced to 0 or below.")
                    target_hp = get_numeric_input("Enter new target HP: ")
                else:
                    print(f"Remaining target HP: {target_hp}")

        input("\nPress enter key to continue...")

if __name__ == "__main__":
    main() # this script fucking sucks
