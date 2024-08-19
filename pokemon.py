import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Input
import numpy as np
import random
import pokebase as pb
from collections import deque
from fetch_functions import fetch_banned_pokemon, fetch_type_chart, fetch_natures, fetch_type_to_int
from utils import get_random_nature
from utils import get_stat_multipliers

type_chart = fetch_type_chart()
banned_pokemon = fetch_banned_pokemon()
natures = fetch_natures()
type_to_int = fetch_type_to_int()

class Pokemon:
    filepath = 'D:\PI-III\modelos'
    
    banned_pokemon = banned_pokemon

    def __init__(self, number, id, name, form, type1, type2, moveset, hp, attack, defense, sp_attack, sp_defense, speed, nature, battle_rules, level=50, ivs=None, evs=None, *args, **kwargs):
        self.number = number
        self.id = id
        self.name = name
        self.form = form
        self.type1 = type1
        self.type2 = type2
        self.base_hp = hp
        self.base_attack = attack
        self.base_defense = defense
        self.base_sp_attack = sp_attack
        self.base_sp_defense = sp_defense
        self.base_speed = speed
        self.nature = nature
        self.battle_rules = battle_rules
        self.moveset = moveset
        self.selected_move = None
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
        self.status = {}  # Adiciona o atributo de status
        self.guts_ability = False
        self.stat_stages = {"attack": 0, "defense": 0, "sp_attack": 0, "sp_defense": 0, "speed": 0}
        self.load_stat_multipliers()
        self.calculate_final_stats()

    def build_model(self, input_dim, output_dim):
        model = Sequential()
        model.add(Input(shape=(input_dim,), dtype=tf.float32))
        model.add(Dense(64, activation='relu', dtype=tf.float32))
        model.add(Dense(64, activation='relu', dtype=tf.float32))
        model.add(Dense(output_dim, activation='linear', dtype=tf.float32))
        model.compile(optimizer='adam', loss='mse')
        return model

    def train_model(self):
        X, y = self.prepare_data()
        if X.shape[0] == 0 or y.shape[0] == 0:
            print("Not enough data to train the model.")
            return
        X = X.astype(np.float32)  # Convertendo para float32
        y = y.astype(np.float32)  # Convertendo para float32
        dataset = tf.data.Dataset.from_tensor_slices((X, y)).batch(32)
        for epoch in range(100):
            for batch_X, batch_y in dataset:
                loss = self.train_step(batch_X, batch_y)
            print(f"Epoch {epoch + 1}, Loss: {loss.numpy()}")

    def prepare_data(self):
        X = []
        y = []
        for state, move, reward, next_state in self.memory:
            state_list = list(state)
            next_state_list = list(next_state)
            target = reward + self.gamma * np.amax(self.model.predict(np.array(next_state_list).reshape(1, -1), verbose=0)[0])
            move_index = self.moveset.index(move)
            target_f = self.model.predict(np.array(state_list).reshape(1, -1), verbose=0)
            target_f[0][move_index] = target
            X.append(state_list)
            y.append(target_f[0])
        X = np.array(X)
        y = np.array(y)
        return X, y

    @tf.function(input_signature=[tf.TensorSpec(shape=[None, 6], dtype=tf.float32), tf.TensorSpec(shape=[None, None], dtype=tf.float32)], reduce_retracing=True)
    def train_step(self, X, y):
        with tf.GradientTape() as tape:
            predictions = self.model(X, training=True)
            loss = tf.keras.losses.MeanSquaredError()(y, predictions)
        gradients = tape.gradient(loss, self.model.trainable_variables)
        self.model.optimizer.apply_gradients(zip(gradients, self.model.trainable_variables))
        return loss

    def save_model(self, filepath):
        """Save the model's weights and architecture separately."""
        try:
            # Save weights
            weights_filepath = filepath + '_weights.h5'
            self.model.save_weights(weights_filepath)
            print(f"Weights saved successfully at {weights_filepath}.")
            # Save architecture
            architecture_filepath = filepath + '_architecture.json'
            with open(architecture_filepath, 'w') as json_file:
                json_file.write(self.model.to_json())
            print(f"Architecture saved successfully at {architecture_filepath}.")
        except Exception as e:
            print(f"Error saving the model: {e}")

    def load_model(self, filepath):
        """Load the model's weights and architecture separately."""
        try:
            # Load architecture
            architecture_filepath = filepath + '_architecture.json'
            with open(architecture_filepath, 'r') as json_file:
                model_json = json_file.read()
                self.model = tf.keras.models.model_from_json(model_json)
            print(f"Architecture loaded successfully from {architecture_filepath}.")
            # Load weights
            weights_filepath = filepath + '_weights.h5'
            self.model.load_weights(weights_filepath)
            print(f"Weights loaded successfully from {weights_filepath}.")
        except Exception as e:
            print(f"Error loading the model: {e}")

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
        evs = {
            'hp': 0,
            'attack': 0,
            'defense': 0,
            'sp_attack': 0,
            'sp_defense': 0,
            'speed': 0
        }
        stats = list(evs.keys())
        stat1, stat2 = random.sample(stats, 2)
        evs[stat1] = 252
        evs[stat2] = 252
        stats.remove(stat1)
        stats.remove(stat2)
        remaining_evs = 6
        while remaining_evs > 0:
            stat = random.choice(stats)
            increment = min(remaining_evs, 4)
            evs[stat] += increment
            remaining_evs -= increment
        return evs

    def load_stat_multipliers(self):
        # Carregar multiplicadores de estágios de stats do Firebase
        self.STAT_STAGE_MULTIPLIERS = get_stat_multipliers()

    def apply_buff(self, stat, stages):
        if stat in self.stat_stages:
            self.stat_stages[stat] += stages
            self.stat_stages[stat] = min(6, max(-6, self.stat_stages[stat]))
            print(f"{self.name} recebeu um buff em {stat}: {stages} estágios. Novo estágio: {self.stat_stages[stat]}")
        self.calculate_final_stats()

    def apply_debuff(self, stat, stages):
        if stat in self.stat_stages:
            self.stat_stages[stat] -= stages
            self.stat_stages[stat] = min(6, max(-6, self.stat_stages[stat]))
            print(f"{self.name} recebeu um debuff em {stat}: {stages} estágios. Novo estágio: {self.stat_stages[stat]}")
        self.calculate_final_stats()

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
        self.hp = self.calculate_hp_stat(self.base_hp, self.ivs['hp'], self.evs['hp'], self.level)
        self.attack = self.calculate_stat(self.base_attack, self.ivs['attack'], self.evs['attack'], self.level)
        self.attack = self.apply_nature_effects('attack')
        self.defense = self.calculate_stat(self.base_defense, self.ivs['defense'], self.evs['defense'], self.level)
        self.defense = self.apply_nature_effects('defense')
        self.sp_attack = self.calculate_stat(self.base_sp_attack, self.ivs['sp_attack'], self.evs['sp_attack'], self.level)
        self.sp_attack = self.apply_nature_effects('sp_attack')
        self.sp_defense = self.calculate_stat(self.base_sp_defense, self.ivs['sp_defense'], self.evs['sp_defense'], self.level)
        self.sp_defense = self.apply_nature_effects('sp_defense')
        self.speed = self.calculate_stat(self.base_speed, self.ivs['speed'], self.evs['speed'], self.level)
        self.speed = self.apply_nature_effects('speed')
        self.attack = self.apply_stat_change(self.attack, self.stat_stages["attack"])
        self.defense = self.apply_stat_change(self.defense, self.stat_stages["defense"])
        self.sp_attack = self.apply_stat_change(self.sp_attack, self.stat_stages["sp_attack"])
        self.sp_defense = self.apply_stat_change(self.sp_defense, self.stat_stages["sp_defense"])
        self.speed = self.apply_stat_change(self.speed, self.stat_stages["speed"])

    def apply_stat_change(self, base_value, stage):
        multiplier = self.STAT_STAGE_MULTIPLIERS[str(stage)]
        return int(base_value * multiplier)

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
        species_count = sum(1 for pokemon in team if pokemon.name == self.name)
        if species_count > 1:
            return False
        return True

    @staticmethod
    def get_pokemon_info(pokemon_id):
        try:
            poke = pb.pokemon(pokemon_id)
            if poke:
                id = poke.id
                name = poke.name
                types = [t.type.name.capitalize() for t in poke.types] if poke.types else []
                moveset = [move.move.name.capitalize() for move in poke.moves] if poke.moves else []
                hp = poke.stats[0].base_stat
                attack = poke.stats[1].base_stat
                defense = poke.stats[2].base_stat
                sp_attack = poke.stats[3].base_stat
                sp_defense = poke.stats[4].base_stat
                speed = poke.stats[5].base_stat
                return id, name, types, moveset, hp, attack, defense, sp_attack, sp_defense, speed
        except Exception as e:
            print(f"Error retrieving Pokémon info from API: {e}")
        print(f"Não foi possível obter dados para o Pokémon {pokemon_id}")
        return None

    def select_move(self, opponent):
        state = self.get_state_for_model(self, opponent)
        if np.random.rand() <= self.epsilon:
            move_index = random.randint(0, len(self.moveset) - 1)
        else:
            q_values = self.model.predict(np.array(state).reshape(1, -1).astype(np.float32))
            move_index = np.argmax(q_values[0])
        self.selected_move = self.moveset[move_index]
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        print(f"{self.name} selected move: {self.selected_move}")
        self.show_move_info(self.selected_move)
        self.confirm_attack(opponent)

    def select_move_automatically(self, opponent):
        state = self.get_state_for_model(self, opponent)
        q_values = self.model.predict(np.array(state).reshape(1, -1).astype(np.float32))
        best_move_index = np.argmax(q_values)
        best_move = self.moveset[best_move_index]
        self.selected_move = best_move
        print(f"{self.name} usa {self.selected_move}!")
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
                move_name, move_type, move_power, move_accuracy, damage_class, status_effects = move_info
                print(f"{self.name} used {self.selected_move}!")
                print(f"Move info: Name={move_name}, Type={move_type}, Power={move_power}, Accuracy={move_accuracy}, Class={damage_class}")

                if self.resolve_status():
                    if move_power:  # Verifica se há poder (dano) para o movimento
                        damage = self.calculate_damage(self, opponent, move_info)
                        print(f"Damage calculated: {damage:.2f}")
                        opponent.hp -= damage
                        if opponent.hp < 0:
                            opponent.hp = 0
                        print(f"{opponent.name}'s HP dropped to {opponent.hp}")
                        self.update_memory(opponent, damage)
                    else:
                        print("Move has no power (might be a status move).")
                    for status in status_effects:
                        self.apply_status_effect(opponent, status)
                else:
                    print(f"{self.name} não pode atacar devido ao status {self.status}.")
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
            return 0
        damage = (((2 * level / 5 + 2) * move_power * (attack_stat / defense_stat)) / 50) + 2
        if move_info[1].capitalize() in [attacker.type1, attacker.type2]:
            damage *= 1.5
        defender_types = [defender.type1, defender.type2] if defender.type2 else [defender.type1]
        type_effectiveness = Pokemon.get_type_effectiveness(move_info[1].capitalize(), defender_types)
        damage *= type_effectiveness
        is_critical = random.random() < 0.0625
        critical = 1.5 if is_critical else 1.0
        damage *= critical
        damage *= random.uniform(0.85, 1.0)
        return damage

    def confirm_attack(self, opponent):
        self.use_move(opponent)

    def get_move_info(self, move):
        try:
            move_data = pb.move(move.lower())
            if move_data:
                move_name = move_data.name.capitalize()
                move_type = move_data.type.name.capitalize()
                move_power = move_data.power if move_data.power else 0
                move_accuracy = move_data.accuracy if move_data.accuracy else 100
                damage_class = move_data.damage_class.name.capitalize() if move_data.damage_class else "Status"
                status_effects = []
                for effect in move_data.effect_entries:
                    effect_text = effect.effect
                    if "paralyze" in effect_text:
                        status_effects.append("paralyze")
                    elif "burn" in effect_text:
                        status_effects.append("burn")
                    elif "freeze" in effect_text:
                        status_effects.append("freeze")
                    elif "sleep" in effect_text:
                        status_effects.append("sleep")
                    elif "poison" in effect_text:
                        status_effects.append("poison")
                    elif "confuse" in effect_text:
                        status_effects.append("confuse")
                return move_name, move_type, move_power, move_accuracy, damage_class, status_effects
        except Exception as e:
            print(f"Error retrieving move info: {e}")
        return None, None, None, None, None, []

    def show_move_info(self, move):
        move_info = self.get_move_info(move)
        if move_info:
            move_name, move_type, move_power, move_accuracy, damage_class, status_effects = move_info
            print(f"Move: {move_name}")
            print(f"Type: {move_type}")
            print(f"Power: {move_power}")
            print(f"Accuracy: {move_accuracy}")
            print(f"Class: {damage_class}")
            if status_effects:
                print(f"Status Effects: {', '.join(status_effects)}")
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

    def get_state_for_model(self, agent_pokemon, opponent_pokemon):
        agent_hp = agent_pokemon.hp
        opponent_hp = opponent_pokemon.hp
        agent_type1 = type_to_int[agent_pokemon.type1.lower()]
        agent_type2 = type_to_int[agent_pokemon.type2.lower()] if agent_pokemon.type2 else type_to_int["none"]
        opponent_type1 = type_to_int[opponent_pokemon.type1.lower()]
        opponent_type2 = type_to_int[opponent_pokemon.type2.lower()] if opponent_pokemon.type2 else type_to_int["none"]
        return (agent_hp, opponent_hp, agent_type1, agent_type2, opponent_type1, opponent_type2)

    def update_memory(self, opponent, damage):
        state = tuple(self.get_state_for_model(self, opponent))
        reward = damage
        next_state = tuple(self.get_state_for_model(opponent, self))
        self.memory.append((state, self.selected_move, reward, next_state))
    
    def apply_status_effect(self, opponent, status):
        if status not in opponent.status:
            opponent.status[status] = 0
            print(f"{opponent.name} foi afetado por {status}!")

    def resolve_status(self):
        if not self.status:
            return True
        
        can_move = True
        new_statuses = {}

        for status, counter in self.status.items():
            if status == "paralyze":
                if random.random() < 0.25:
                    print(f"{self.name} está paralisado e não pode se mover!")
                    can_move = False
                new_statuses[status] = counter
            elif status == "burn":
                burn_damage = self.hp * 0.0625 if self.guts_ability else self.hp * 0.125
                self.hp -= burn_damage
                print(f"{self.name} está queimado e perdeu {burn_damage:.2f} HP!")
                new_statuses[status] = counter
            elif status == "freeze":
                if random.random() < 0.2:
                    print(f"{self.name} descongelou!")
                else:
                    print(f"{self.name} está congelado e não pode se mover!")
                    can_move = False
                    new_statuses[status] = counter
            elif status == "sleep":
                if counter >= 1:
                    print(f"{self.name} acordou!")
                else:
                    print(f"{self.name} está dormindo e não pode se mover!")
                    can_move = False
                    new_statuses[status] = counter + 1
            elif status == "poisoned":
                poison_damage = self.hp * 0.125
                self.hp -= poison_damage
                print(f"{self.name} está envenenado e perdeu {poison_damage:.2f} HP!")
                new_statuses[status] = counter
            elif status == "badly poisoned":
                poison_damage = self.hp * (0.0625 * (counter + 1))
                self.hp -= poison_damage
                print(f"{self.name} está gravemente envenenado e perdeu {poison_damage:.2f} HP!")
                new_statuses[status] = counter + 1
            elif status == "confused":
                if random.random() < 0.33:
                    confusion_damage = self.hp * 0.1
                    self.hp -= confusion_damage
                    print(f"{self.name} está confuso e se machucou na confusão!")
                    can_move = False
                else:
                    print(f"{self.name} superou a confusão!")
                new_statuses[status] = counter
        
        self.status = new_statuses
        return can_move
    
    def compare_speed(self, other):
        """Compara a velocidade deste Pokémon com outro Pokémon."""
        if self.speed > other.speed:
            return self
        elif self.speed < other.speed:
            return other
        else:
            return random.choice([self, other])

    def reset(self):
        self.hp = self.calculate_hp_stat(self.base_hp, self.ivs['hp'], self.evs['hp'], self.level)
        self.attack = self.calculate_stat(self.base_attack, self.ivs['attack'], self.evs['attack'], self.level)
        self.attack = self.apply_nature_effects('attack')
        self.defense = self.calculate_stat(self.base_defense, self.ivs['defense'], self.evs['defense'], self.level)
        self.defense = self.apply_nature_effects('defense')
        self.sp_attack = self.calculate_stat(self.base_sp_attack, self.ivs['sp_attack'], self.evs['sp_attack'], self.level)
        self.sp_attack = self.apply_nature_effects('sp_attack')
        self.sp_defense = self.calculate_stat(self.base_sp_defense, self.ivs['sp_defense'], self.evs['sp_defense'], self.level)
        self.sp_defense = self.apply_nature_effects('sp_defense')
        self.speed = self.calculate_stat(self.base_speed, self.ivs['speed'], self.evs['speed'], self.level)
        self.speed = self.apply_nature_effects('speed')
        self.attack = self.apply_stat_change(self.attack, self.stat_stages["attack"])
        self.defense = self.apply_stat_change(self.defense, self.stat_stages["defense"])
        self.sp_attack = self.apply_stat_change(self.sp_attack, self.stat_stages["sp_attack"])
        self.sp_defense = self.apply_stat_change(self.sp_defense, self.stat_stages["sp_defense"])
        self.speed = self.apply_stat_change(self.speed, self.stat_stages["speed"])
        self.status = {}  # Resetar todos os status
        self.stat_stages = {"attack": 0, "defense": 0, "sp_attack": 0, "sp_defense": 0, "speed": 0}
