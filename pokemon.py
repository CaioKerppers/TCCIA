import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Input, BatchNormalization, Dropout
import numpy as np
import random
import pokebase as pb
from collections import deque
from fetch_functions import fetch_banned_pokemon, fetch_type_chart, fetch_natures, fetch_type_to_int
from move import Move
from utils import get_random_nature, get_stat_multipliers
import os

type_chart = fetch_type_chart()
banned_pokemon = fetch_banned_pokemon()
natures = fetch_natures()
type_to_int = fetch_type_to_int()


# Limpar sessão anterior
tf.keras.backend.clear_session()

# Verificação da GPU e inicialização correta
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        logical_gpus = tf.config.experimental.list_logical_devices('GPU')
        print(f"{len(gpus)} GPUs físicas, {len(logical_gpus)} GPUs lógicas")
    except RuntimeError as e:
        print(f"Erro na inicialização da GPU: {e}")
else:
    print("Nenhuma GPU encontrada. Usando CPU.")

class Pokemon:
    #filepath = r'C:\Users\User\Documents\PI-III\models\larvesta_model'
    filepath = '/mnt/c/Users/User/Documents/PI-III'
    
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
        self.memory = deque(maxlen=4000)
        self.gamma = 0.41  # discount rate
        self.epsilon = 1.0  # exploration rate
        self.epsilon_min = 0.025
        self.epsilon_decay = 0.600
        self.learning_rate = 0.700
        self.model = self.build_model(input_dim=6, output_dim=len(moveset))
        self.status = {}  # Adiciona o atributo de status
        self.guts_ability = False
        self.stat_stages = {"attack": 0, "defense": 0, "sp_attack": 0, "sp_defense": 0, "speed": 0}
        self.load_stat_multipliers()
        self.calculate_final_stats()
        self.on_ground = True
        self.protected = False
        

    def build_model(self, input_dim, output_dim, neurons=128):
        model = Sequential()
        model.add(Input(shape=(input_dim,), dtype=tf.float32))  # Input layer

        #camada 1
        model.add(Dense(neurons, activation='relu', kernel_initializer='he_normal', dtype=tf.float32))
        model.add(BatchNormalization())
        model.add(Dropout(0.2))  # Dropout to prevent overfitting
        
        #camada 2
        model.add(Dense(neurons, activation='relu', kernel_initializer='he_normal', dtype=tf.float32))
        model.add(BatchNormalization())
        model.add(Dropout(0.2))  # Dropout to prevent overfitting
        
        #camada 3
        model.add(Dense(neurons, activation='relu', kernel_initializer='he_normal', dtype=tf.float32))
        model.add(BatchNormalization())
        model.add(Dropout(0.2))  # Dropout to prevent overfitting
        
        #camada 4
        model.add(Dense(neurons, activation='relu', kernel_initializer='he_normal', dtype=tf.float32))
        model.add(BatchNormalization())
        model.add(Dropout(0.2))  # Dropout to prevent overfitting
        
        #camada 5
        model.add(Dense(neurons, activation='relu', kernel_initializer='he_normal', dtype=tf.float32))
        model.add(BatchNormalization())
        model.add(Dropout(0.2))  # Dropout to prevent overfitting
        
        #camada 6
        model.add(Dense(neurons, activation='relu', kernel_initializer='he_normal', dtype=tf.float32))
        model.add(BatchNormalization())
        model.add(Dropout(0.2))  # Dropout to prevent overfitting
        
        #camada 7
        model.add(Dense(neurons, activation='relu', kernel_initializer='he_normal', dtype=tf.float32))
        model.add(BatchNormalization())
        model.add(Dropout(0.2))  # Dropout to prevent overfitting

        #camada 8
        model.add(Dense(neurons, activation='relu', kernel_initializer='he_normal', dtype=tf.float32))
        model.add(BatchNormalization())
        model.add(Dropout(0.2))  # Dropout to prevent overfitting

        # Additional hidden layer with the same number of neurons
        model.add(Dense(neurons, activation='relu', kernel_initializer='he_normal', dtype=tf.float32))

        # Output layer
        model.add(Dense(output_dim, activation='linear', dtype=tf.float32))
        model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=self.learning_rate), loss='mse')
        return model

    def train_model(self):
        # Preparar os dados (X e y) para treinamento
        X, y = self.prepare_data()

        # Certifique-se de que há dados suficientes para treinar
        if X.shape[0] == 0 or y.shape[0] == 0:
            print("Não há dados suficientes para treinar o modelo.")
            return

        # Configurar dataset para o treinamento
        dataset = tf.data.Dataset.from_tensor_slices((X, y)).batch(32).cache().prefetch(tf.data.AUTOTUNE)

        # Callbacks para o ajuste do treinamento
        early_stopping = tf.keras.callbacks.EarlyStopping(monitor='loss', patience=10, restore_best_weights=True)
        reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(monitor='loss', factor=0.2, patience=5)

        # Verificar se há GPUs e configurar para usar
        with tf.device('/GPU:0' if tf.config.list_physical_devices('GPU') else '/CPU:0'):
            # Treinamento do modelo com os dados
            self.model.fit(
                dataset, 
                epochs=50,  # Número de épocas
                callbacks=[early_stopping, reduce_lr],  # Callbacks para parar o treinamento
                verbose=1  # Mostra a barra de progresso do treinamento
            )

        # Salvar o modelo após o treinamento
        self.save_model(f'{Pokemon.filepath}/{self.name}_model')

    def prepare_data(self):
        states = []
        targets = []
        for state, move, reward, next_state in self.memory:
            state_array = np.array(state).reshape(1, -1).astype(np.float32)  # Garante float32
            next_state_array = np.array(next_state).reshape(1, -1).astype(np.float32)  # Garante float32

            target = reward + self.gamma * np.amax(self.model.predict(next_state_array, verbose=0))
            move_index = self.moveset.index(move)

            target_f = self.model.predict(state_array, verbose=0)
            target_f[0][move_index] = target

            states.append(state_array)
            targets.append(target_f)

        # Formatar corretamente as matrizes de entrada e saída
        states = np.vstack(states).astype(np.float32)
        targets = np.vstack(targets).astype(np.float32)
        return states, targets


    @tf.function(input_signature=[tf.TensorSpec(shape=[None, 6], dtype=tf.float32), tf.TensorSpec(shape=[None, None], dtype=tf.float32)], reduce_retracing=True)
    def train_step(self, X, y):
        with tf.GradientTape() as tape:
            predictions = self.model(X, training=True)
            loss = tf.keras.losses.MeanSquaredError()(y, predictions)
        gradients = tape.gradient(loss, self.model.trainable_variables)
        self.model.optimizer.apply_gradients(zip(gradients, self.model.trainable_variables))
        return loss

    def save_model(self, filepath=None):
        """Save the model's weights and architecture separately."""
        if filepath is None:
            filepath = self.filepath
        
        try:
            # Extrair o diretório e o nome base do arquivo
            directory = os.path.dirname(filepath)
            base_name = os.path.basename(filepath)
            
            # Save weights
            weights_filepath = os.path.join(directory, base_name + '.weights.h5')
            print("balacobaco")
            print(weights_filepath)
            if not weights_filepath.endswith('.h5'):
                raise ValueError("The filename must end in `.h5`.")
            self.model.save_weights(weights_filepath)
            print(f"Weights saved successfully at {weights_filepath}.")
            
            # Save architecture
            architecture_filepath = os.path.join(directory, base_name + '_architecture.json')
            with open(architecture_filepath, 'w') as json_file:
                json_file.write(self.model.to_json())
            print(f"Architecture saved successfully at {architecture_filepath}.")
        except Exception as e:
            print(f"Error saving the model: {e}")

    def load_model(self, filepath=None):
        """Load the model's weights and architecture separately."""
        if filepath is None:
            filepath = self.filepath
            
        try:
            # Extrair o diretório e o nome base do arquivo
            directory = os.path.dirname(filepath)
            base_name = os.path.basename(filepath)
            
            # Load architecture
            architecture_filepath = os.path.join(directory, base_name + '_architecture.json')
            with open(architecture_filepath, 'r') as json_file:
                model_json = json_file.read()
                self.model = tf.keras.models.model_from_json(model_json)
            print(f"Architecture loaded successfully from {architecture_filepath}.")
            
            # Load weights
            weights_filepath = os.path.join(directory, base_name + '.weights.h5')
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
    
    def get_qs(self, state):
        state = np.array(state).reshape(1, -1).astype(np.float32)
        return self.model.predict(state, verbose=0)

    def get_move(self, state):
        if np.random.rand() <= self.epsilon:
            return random.choice(self.moveset)
        q_values = self.get_qs(state)
        return self.moveset[np.argmax(q_values)]

    def remember(self, state, move, reward, next_state):
        self.memory.append((state, move, reward, next_state))

    def update_epsilon(self):
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def update_stat_stage(self, stat_name, change):
        current_stage = self.stat_stages.get(stat_name, 0)
        new_stage = max(-6, min(6, current_stage + change))
        self.stat_stages[stat_name] = new_stage

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

    def wake_up(self):
        print(f"{self.name} acordou devido ao Electric Terrain!")

    def increase_stat(self, stat_name, stages):
        # Implementação que aumenta o estágio de um stat específico
        print(f"{self.name} teve seu {stat_name} aumentado em {stages} estágio(s)!")

    def prevent_status_conditions(self):
        print(f"{self.name} está protegido contra condições de status sob Misty Terrain!")

    def prevent_priority_moves(self):
        print(f"{self.name} não pode ser afetado por movimentos prioritários sob Psychic Terrain!")

    def consume_item(self):
        print(f"{self.name} consumiu {self.holding_item}!")
        self.holding_item = None  # O item é consumido e removido
    
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

    def use_move(self, opponent, terrain=None, weather=None):
        """Execute the selected move against the opponent, considering terrain and weather."""
        if self.hp <= 0:  # Prevent fainted Pokémon from using a move
            print(f"{self.name} is fainted and cannot move!")
            return

        if not self.selected_move:  # Ensure a move is selected
            return

        # Apply terrain and weather effects before using the move
        if terrain:
            terrain.apply_effects(self)

        if weather:
            weather.apply_effects(self)

        move = Move(self.selected_move)

        # Check for protection status
        if self.protected:
            print(f"{self.name} is protected by Protect! The attack fails.")
            self.protected = False  # Reset protection after use
            return

        move_info = self.get_move_info(self.selected_move)
        if move_info:
            move_name, move_type, move_power, move_accuracy, damage_class, status_effects = move_info
            print(f"{self.name} used {self.selected_move}!")
            print(f"Move info: Name={move_name}, Type={move_type}, Power={move_power}, Accuracy={move_accuracy}, Class={damage_class}")

            if self.resolve_status():  # Check if Pokémon can move based on status conditions
                if move_power:  # Check if the move has power (deals damage)
                    damage = Move.calculate_damage(self, opponent, move_info)
                    print(f"Damage calculated: {damage:.2f}")
                    opponent.hp -= damage
                    opponent.hp = max(opponent.hp, 0)  # Ensure HP doesn't go below 0
                    print(f"{opponent.name}'s HP dropped to {opponent.hp}")
                    self.update_memory(opponent, damage)
                else:
                    print("Move has no power (might be a status move).")

                # Apply any status effects from the move
                for status in status_effects:
                    self.apply_status_effect(opponent, status)
            else:
                print(f"{self.name} is unable to attack due to status {self.status}.")
        else:
            print(f"Could not retrieve move info for {self.selected_move}")

        # Clear the selected move after execution
        self.selected_move = None

    def confirm_attack(self, opponent):
        if not self.selected_move:  # Check if a move has been selected
            print("No move selected.")
            return
        
        # Ensure the move is only used once per turn
        self.use_move(opponent)
        self.selected_move = None

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
        """Applies a status effect to the opponent if not already afflicted."""
        if status not in opponent.status:
            opponent.status[status] = 0  # Initial status counter (can be incremented if needed)
            print(f"{opponent.name} was affected by {status}!")
        else:
            print(f"{opponent.name} is already affected by {status}.")

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
