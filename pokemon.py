import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import numpy as np
import random
import pokebase as pb
from collections import deque
from fetch_functions import fetch_banned_pokemon, fetch_type_chart, fetch_natures
from utils import get_random_nature

type_chart = fetch_type_chart()
banned_pokemon = fetch_banned_pokemon()
natures = fetch_natures()

class Pokemon:
    banned_pokemon = banned_pokemon

    def __init__(self, number, name, form, type1, type2, moveset, hp, attack, defense, sp_attack, sp_defense, speed, nature, battle_rules, item=None, level=50, ivs=None, evs=None, *args, **kwargs):
        self.number = number
        self.name = name
        self.form = form
        self.type1 = type1
        self.type2 = type2
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.sp_attack = sp_attack
        self.sp_defense = sp_defense
        self.speed = speed
        self.nature = nature
        self.battle_rules = battle_rules
        self.moveset = moveset
        self.q_table = {}  # Tabela Q para aprendizado por reforço
        self.selected_move = None
        self.item = item
        self.model = None
        self.level = level  # Set default level to 50
        self.ivs = ivs if ivs else self.generate_random_ivs()
        self.evs = evs if evs else self.generate_random_evs()
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95  # discount rate
        self.epsilon = 1.0  # exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.model = self.build_model(input_dim=6, output_dim=len(moveset))
    
    def build_model(self, input_dim, output_dim):
        model = Sequential()
        model.add(Dense(64, input_dim=input_dim, activation='relu'))
        model.add(Dense(64, activation='relu'))
        model.add(Dense(output_dim, activation='linear'))
        model.compile(optimizer='adam', loss='mse')
        return model
    
    def train_model(self):
        X, y = self.prepare_data()
        if X.shape[0] == 0 or y.shape[0] == 0:
            print("Not enough data to train the model.")
            return
        self.model.fit(X, y, epochs=100, verbose=1)
    
    def prepare_data(self):
        X = []
        y = []
        for state, actions in self.q_table.items():
            state_list = list(state)
            for action, reward in actions.items():
                move_index = self.moveset.index(action)
                X.append(state_list)
                y.append([reward if i == move_index else 0 for i in range(len(self.moveset))])
        X = np.array(X)
        y = np.array(y)
        # Verificar se a forma dos dados está correta
        print("Shape of X:", X.shape)
        print("Shape of y:", y.shape)
        return X, y

    def generate_random_ivs(self):
        return {
            'hp': random.randint(0, 31),
            'attack': random.randint(0, 31),
            'defense': random.randint(0, 31),
            'sp_attack': random.randint(0, 31),
            'sp_defense': random.randint(0, 31),
            'speed': random.randint(0, 31)
        }
    
    def generate_random_evs(self):
        # Inicializa todos os EVs com 0
        evs = {
            'hp': 0,
            'attack': 0,
            'defense': 0,
            'sp_attack': 0,
            'sp_defense': 0,
            'speed': 0
        }

        # Escolhe duas estatísticas aleatórias para receber 252 EVs
        stats = list(evs.keys())
        stat1, stat2 = random.sample(stats, 2)
        evs[stat1] = 252
        evs[stat2] = 252

        # Remove as estatísticas que já receberam 252 EVs da lista
        stats.remove(stat1)
        stats.remove(stat2)

        # Distribui os 6 EVs restantes entre as outras estatísticas
        remaining_evs = 6
        while remaining_evs > 0:
            stat = random.choice(stats)
            increment = min(remaining_evs, 4)
            evs[stat] += increment
            remaining_evs -= increment

        return evs

    def apply_nature_effects(self, stat_name):
        nature_increase, nature_decrease = natures[self.nature]
        stat_value = getattr(self, stat_name)
        if nature_increase == stat_name:
            stat_value *= 1.1
        elif nature_decrease == stat_name:
            stat_value *= 0.9
        return int(stat_value)


    def calculate_stat(self, base, iv, evs, level):
        return ((((2 * base + iv + (evs // 4)) * level) // 100) + 5)

    def calculate_hp_stat(self, base, iv, evs, level):
        return ((((2 * base + iv + (evs // 4)) * level) // 100) + level + 10)

    def calculate_final_stats(self):
        self.hp = self.calculate_hp_stat(self.hp, self.ivs['hp'], self.evs['hp'], self.level)
        self.attack = self.calculate_stat(self.attack, self.ivs['attack'], self.evs['attack'], self.level)
        self.attack = self.apply_nature_effects('attack')
        self.defense = self.calculate_stat(self.defense, self.ivs['defense'], self.evs['defense'], self.level)
        self.defense = self.apply_nature_effects('defense')
        self.sp_attack = self.calculate_stat(self.sp_attack, self.ivs['sp_attack'], self.evs['sp_attack'], self.level)
        self.sp_attack = self.apply_nature_effects('sp_attack')
        self.sp_defense = self.calculate_stat(self.sp_defense, self.ivs['sp_defense'], self.evs['sp_defense'], self.level)
        self.sp_defense = self.apply_nature_effects('sp_defense')
        self.speed = self.calculate_stat(self.speed, self.ivs['speed'], self.evs['speed'], self.level)
        self.speed = self.apply_nature_effects('speed')
        
    def get_type_effectiveness(move_type, defender_types):
        effectiveness = 1.0
        for defender_type in defender_types:
            if defender_type in type_chart[move_type]['advantages']:
                effectiveness *= 2
            if defender_type in type_chart[move_type]['weaknesses']:
                effectiveness *= 0.5
            if defender_type in type_chart[move_type]['immunities']:
                effectiveness *= 0
        return effectiveness

    def is_banned(self):
        return self.name in Pokemon.banned_pokemon

    def auto_level(self):
        self.level = 50  # Auto-level to 50 during battle
        self.calculate_final_stats()

    def check_play_restrictions(self, team):
        # Check item clause
        item_count = sum(1 for pokemon in team if pokemon.item == self.item)
        if item_count > 1:
            return False

        # Check species clause
        species_count = sum(1 for pokemon in team if pokemon.name == self.name)
        if species_count > 1:
            return False

        return True

    @staticmethod
    def get_pokemon_info(pokemon_name):
        try:
            poke = pb.pokemon(pokemon_name.lower())
            if poke:
                name = poke.name.capitalize()
                types = [t.type.name.capitalize() for t in poke.types] if poke.types else []
                moveset = [move.move.name.capitalize() for move in poke.moves] if poke.moves else []
                hp = poke.stats[0].base_stat
                attack = poke.stats[1].base_stat
                defense = poke.stats[2].base_stat
                sp_attack = poke.stats[3].base_stat
                sp_defense = poke.stats[4].base_stat
                speed = poke.stats[5].base_stat
                return name, types, moveset, hp, attack, defense, sp_attack, sp_defense, speed
        except Exception as e:
            print(f"Error retrieving Pokémon info from API: {e}")
            
        print(f"Não foi possível obter dados para o Pokémon {pokemon_name}")
        return None

    def select_move(self, opponent):
        state = self.get_state(self, opponent)
        if np.random.rand() <= self.epsilon:
            # Escolha um movimento aleatório (exploração)
            move_index = random.randint(0, len(self.moveset) - 1)
        else:
            # Escolha o melhor movimento predito pela rede neural (exploração)
            q_values = self.model.predict(np.array(state).reshape(1, -1))
            move_index = np.argmax(q_values[0])

        self.selected_move = self.moveset[move_index]
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

        print(f"{self.name} selected move: {self.selected_move}")
        self.show_move_info(self.selected_move)
        self.confirm_attack(opponent)

    def select_random_move(self, opponent):
        self.selected_move = random.choice(self.moveset)
        print(f"{self.name} randomly selected move: {self.selected_move}")
        self.show_move_info(self.selected_move)
        self.confirm_attack(opponent)

    def use_move(self, opponent):
        if self.selected_move:
            move_info = self.get_move_info(self.selected_move)
            if move_info:
                move_name, move_type, move_power, move_accuracy, damage_class = move_info
                print(f"{self.name} used {self.selected_move}!")
                print(f"Move info: Name={move_name}, Type={move_type}, Power={move_power}, Accuracy={move_accuracy}, Class={damage_class}")

                if move_power:  # Verifica se há poder (dano) para o movimento
                    damage = self.calculate_damage(self, opponent, move_info)
                    print(f"Damage calculated: {damage:.2f}")
                    
                    opponent.hp -= damage
                    if opponent.hp < 0:
                        opponent.hp = 0
                    print(f"{opponent.name}'s HP dropped to {opponent.hp}")

                    # Atualiza a tabela Q com o dano causado
                    self.update_q_table(opponent, damage)
                else:
                    print("Move has no power (might be a status move).")
            else:
                print(f"Could not retrieve move info for {self.selected_move}")
        else:
            print("No move selected.")

    @staticmethod
    def calculate_damage(attacker, defender, move_info):
        level = attacker.level
        move_power = move_info[2] if move_info[2] else 0
        damage_class = move_info[4].lower()

        if damage_class == "physical":
            attack_stat = attacker.attack
            defense_stat = defender.defense
        elif damage_class == "special":
            attack_stat = attacker.sp_attack
            defense_stat = defender.sp_defense
        else:
            return 0  # Caso o movimento não cause dano, retorna 0

        # Fórmula simplificada de cálculo de dano
        damage = (((2 * level / 5 + 2) * move_power * (attack_stat / defense_stat)) / 50) + 2

        # Considera STAB (Same Type Attack Bonus)
        if move_info[1].capitalize() in [attacker.type1, attacker.type2]:
            damage *= 1.5

        # Considera as fraquezas e resistências do oponente
        defender_types = [defender.type1, defender.type2] if defender.type2 else [defender.type1]
        type_effectiveness = Pokemon.get_type_effectiveness(move_info[1].capitalize(), defender_types)

        damage *= type_effectiveness

        is_critical = random.random() < 0.0625  # Probabilidade de crítico (6.25% por exemplo)
        critical = 1.5 if is_critical else 1.0
        damage *= critical
        
        # Considera um fator aleatório entre 85% e 100%
        damage *= random.uniform(0.85, 1.0)

        return damage   

    def confirm_attack(self, opponent):
        while True:
            user_input = input(f"Do you want to use {self.selected_move}? (Y/N): ").strip().lower()
            if user_input == 'y':
                self.use_move(opponent)
                break
            elif user_input == 'n':
                self.select_move(opponent)
                break
            else:
                print("Invalid input. Please enter Y or N.")

    def get_move_info(self, move):
        try:
            move_data = pb.move(move.lower())
            if move_data:
                move_name = move_data.name.capitalize()
                move_type = move_data.type.name.capitalize()
                move_power = move_data.power if move_data.power else 0
                move_accuracy = move_data.accuracy if move_data.accuracy else 100
                damage_class = move_data.damage_class.name.capitalize() if move_data.damage_class else "Status"
                return move_name, move_type, move_power, move_accuracy, damage_class
        except Exception as e:
            print(f"Error retrieving move info: {e}")
        return None

    def show_move_info(self, move):
        move_info = self.get_move_info(move)
        if move_info:
            move_name, move_type, move_power, move_accuracy, damage_class = move_info
            print(f"Move: {move_name}")
            print(f"Type: {move_type}")
            print(f"Power: {move_power}")
            print(f"Accuracy: {move_accuracy}")
            print(f"Class: {damage_class}")
        else:
            print(f"Could not retrieve information for move: {move}")
            
    def show_moves(self):
        print(f"Available moves for {self.name}:")
        for i, move in enumerate(self.moveset, start=1):
            print(f"{i}. {move}")
            
    def select_move_manually(self):
        self.show_moves()
        move_index = int(input("Choose a move: ")) - 1
        if 0 <= move_index < len(self.moveset):
            self.selected_move = self.moveset[move_index]
            print(f"{self.name} selected move: {self.selected_move}")
        else:
            print("Invalid move selection.")

            
    def get_type_advantage(self, opponent):
        advantage = 1.0
        for opponent_type in [opponent.type1, opponent.type2]:
            if opponent_type:
                multiplier = pb.type_damage_multiplier(self.type1, opponent_type)
                if self.type2:
                    multiplier *= pb.type_damage_multiplier(self.type2, opponent_type)
                advantage *= multiplier
        return advantage

    def update_q_table(self, opponent, damage):
        # Atualiza a tabela Q com a recompensa baseada no dano causado
        state = tuple(self.get_state(self, opponent))
        reward = damage  # Utiliza o dano causado como recompensa

        if state not in self.q_table:
            self.q_table[state] = np.zeros(len(self.moveset))

        move_index = self.moveset.index(self.selected_move)
        self.q_table[state][move_index] = (1 - self.learning_rate) * self.q_table[state][move_index] + self.learning_rate * (reward + self.gamma * np.max(self.q_table[state]))
