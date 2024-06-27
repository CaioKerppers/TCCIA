import pokebase as pb
import random
import csv
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import numpy as np
import pokepastes_scraper as pastes

def get_state(agent_pokemon, opponent_pokemon):
    agent_hp = agent_pokemon.hp
    opponent_hp = opponent_pokemon.hp
    agent_type1 = agent_pokemon.type1
    agent_type2 = agent_pokemon.type2
    opponent_type1 = opponent_pokemon.type1
    opponent_type2 = opponent_pokemon.type2
    return (agent_hp, opponent_hp, agent_type1, agent_type2, opponent_type1, opponent_type2)

def build_model(input_dim, output_dim):
    model = Sequential()
    model.add(Dense(64, input_dim=input_dim, activation='relu'))
    model.add(Dense(64, activation='relu'))
    model.add(Dense(output_dim, activation='linear'))
    model.compile(optimizer='adam', loss='mse')
    return model

def prepare_data(pokemon):
    X = []
    y = []
    for state, actions in pokemon.q_table.items():
        for action, reward in actions.items():
            state_list = list(state)
            move_index = pokemon.moveset.index(action)
            X.append(state_list)
            y.append([reward if i == move_index else 0 for i in range(len(pokemon.moveset))])
    return np.array(X), np.array(y)

def train_model(pokemon):
    X, y = prepare_data(pokemon)
    input_dim = X.shape[1]
    output_dim = y.shape[1]
    model = build_model(input_dim, output_dim)
    model.fit(X, y, epochs=100, verbose=1)
    return model

class Pokemon:
    banned_pokemon = [
    "Koraidon", "Miraidon", "Meloetta", "Mew", "Mewtwo", "Calyrex", "Eternatus",
    "Zacian", "Zamazenta", "Arceus", "Dialga", "Giratina", "Palkia", "Ho-Oh",
    "Lugia", "Kyogre", "Groudon", "Rayquaza", "Zarude", "Magearna", "Terapagos",
    "Volcanion", "Hoopa", "Necrozma", "Lunala", "Solgaleo", "Jirachi", "Deoxys",
    "Phione", "Manaphy", "Darkrai", "Shaymin", "Kyurem", "Reshiram", "Zekrom",
    "Keldeo", "Cosmog", "Cosmoem"
    ]

    def __init__(self, number, name, form, type1, type2, moveset, hp, attack, defense, sp_attack, sp_defense, speed, nature, battle_rules, item=None, level=50, *args, **kwargs):
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

    def train_model(self):
        self.model = train_model(self)

    def is_banned(self):
        return self.name in Pokemon.banned_pokemon

    def auto_level(self):
        self.level = 50  # Auto-level to 50 during battle

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
        poke = pb.pokemon(pokemon_name)
        if poke:
            name = poke.name.capitalize()
            types = [t.type.name.capitalize() for t in poke.types] if poke.types else []
            moveset = [move.move.name.capitalize() for move in poke.moves] if poke.moves else []
            # Estatísticas do Pokémon
            hp = poke.stats[0].base_stat
            attack = poke.stats[1].base_stat
            defense = poke.stats[2].base_stat
            sp_attack = poke.stats[3].base_stat
            sp_defense = poke.stats[4].base_stat
            speed = poke.stats[5].base_stat
            return name, types, moveset, hp, attack, defense, sp_attack, sp_defense, speed
        else:
            # Se não encontrar na API, tenta obter do CSV
            with open('bdpoke.csv', mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['Name'].lower() == pokemon_name.lower():
                        name = row['Name'].capitalize()
                        types = [row['Type1'].capitalize()]
                        if row['Type2']:
                            types.append(row['Type2'].capitalize())
                        moveset = [move.capitalize() for move in row['Moveset'].split(',')]
                        hp = int(row['HP'])
                        attack = int(row['Attack'])
                        defense = int(row['Defense'])
                        sp_attack = int(row['Sp. Attack'])
                        sp_defense = int(row['Sp. Defense'])
                        speed = int(row['Speed'])
                        
                        # Imprime o nome obtido do arquivo CSV
                        print(f"Nome obtido do CSV: {name}")
                        
                        return name, types, moveset, hp, attack, defense, sp_attack, sp_defense, speed
                    
            print(f"Não foi possível obter dados para o Pokémon {pokemon_name}")
            return None

    def select_move(self, opponent):
        if self.model is None:
            print(f"{self.name} não possui um modelo treinado. Usando seleção aleatória de movimentos.")
            self.select_random_move(opponent)
            return
        state = np.array([list(get_state(self, opponent))])
        q_values = self.model.predict(state)
        move_index = np.argmax(q_values)
        self.selected_move = self.moveset[move_index]
        print(f"{self.name} selecionou o movimento: {self.selected_move}")
        self.show_move_info(opponent)

    def select_random_move(self, opponent):
        self.selected_move = random.choice(self.moveset)
        print(f"{self.name} randomly selected move: {self.selected_move}")
        self.show_move_info(opponent)

    def use_move(self, opponent):
        if self.is_banned():
            print(f"{self.name} is banned and cannot participate in battles.")
            return
        move_name = self.selected_move
        print(f"{self.name} used {move_name}!")
        # Obter informações do movimento
        move_info = self.get_move_info(move_name)
        if move_info:
            # Exibir descrição do movimento
            description = move_info['description'] if move_info['description'] else "No description available."
            print(f"Description: {description}")
            # Verificar se a chave 'damage_class' existe em move_info
            if 'damage_class' in move_info:
                print(f"Category: {move_info['damage_class']}")
                # Calcular o dano para reduzir o HP do oponente a 0
                damage = opponent.hp
                print(f"Damage: {damage:.2f}")  # Exibe o dano causado com 2 casas decimais
                # Atualizar a tabela Q com o resultado da ação
                self.update_q_table(opponent, damage)
                # Aplicar o dano ao oponente
                opponent.hp -= damage
                print(f"{opponent.name}'s HP caiu para {opponent.hp}")
            else:
                print("Could not retrieve move category.")
        else:
            print(f"Could not retrieve move info for {move_name}")

    def confirm_attack(self, opponent):
        move_name = self.selected_move
        while True:
            user_input = input(f"Do you want to use {move_name}? (Y/N): ").strip().lower()
            if user_input == 'y':
                self.use_move(opponent)
                break
            elif user_input == 'n':
                self.select_move(opponent)
                break
            else:
                print("Invalid input. Please enter Y or N.")

    def get_move_info(self, move_name):
        try:
            move = pb.move(move_name.lower())
            # Filtrar as descrições para pegar a versão em inglês
            english_descriptions = [entry for entry in move.flavor_text_entries if entry.language.name == 'en']
            description = english_descriptions[-1].flavor_text if english_descriptions else "No description available."
            damage_class = move.damage_class.name if move.damage_class else "Unknown"
            return {"description": description, "damage_class": damage_class}
        except Exception as e:
            print(f"An error occurred while fetching move info for {move_name}: {str(e)}")
            return None
        
    def show_move_info(self, opponent):
        move_info = self.get_move_info(self.selected_move)
        if move_info:
            description = move_info['description']
            print(f"Move Description: {description}")
            self.confirm_attack(opponent)
        else:
            print(f"Could not retrieve move info for {self.selected_move}")

    def update_q_table(self, opponent, reward):
        state = get_state(self, opponent)
        if state not in self.q_table:
            self.q_table[state] = {}
        if self.selected_move not in self.q_table[state]:
            self.q_table[state][self.selected_move] = 0.0
        self.q_table[state][self.selected_move] += reward
        
    @staticmethod
    def fetch_pokemon_from_pokepaste():
        results = pastes.search_pokepaste()
        pokemons = []
        for paste in results:
            for pokemon in paste.teams:
                poke_info = Pokemon.get_pokemon_info(pokemon)
                if poke_info:
                    name, types, moveset, hp, attack, defense, sp_attack, sp_defense, speed = poke_info
                    p = Pokemon(
                        number=pokemon.number,
                        name=name,
                        form="",
                        type1=types[0] if len(types) > 0 else None,
                        type2=types[1] if len(types) > 1 else None,
                        moveset=moveset,
                        hp=hp,
                        attack=attack,
                        defense=defense,
                        sp_attack=sp_attack,
                        sp_defense=sp_defense,
                        speed=speed,
                        nature=None,
                        battle_rules={}
                    )
                    pokemons.append(p)
        return pokemons
        
def select_random_pokemon():
    with open('bdpoke.csv', mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        pokemons = list(reader)
        selected_pokemon = random.choice(pokemons)
        number = int(selected_pokemon['Number'])
        name = selected_pokemon['Name']
        form = selected_pokemon['Form']
        type1 = selected_pokemon['Type1']
        type2 = selected_pokemon['Type2']
        moveset = selected_pokemon['Moveset'].split(',')
        hp = int(selected_pokemon['HP'])
        attack = int(selected_pokemon['Attack'])
        defense = int(selected_pokemon['Defense'])
        sp_attack = int(selected_pokemon['Sp. Attack'])
        sp_defense = int(selected_pokemon['Sp. Defense'])
        speed = int(selected_pokemon['Speed'])
        nature = selected_pokemon['Nature']
        battle_rules = BattleRules()
        item = selected_pokemon.get('Item')
        pokemon = Pokemon(number, name, form, type1, type2, moveset, hp, attack, defense, sp_attack, sp_defense, speed, nature, battle_rules, item)
        return pokemon

def apply_nature(self):
    nature_effects = {
    "Adamant": {"Increases": "Attack", "Decreases": "Sp. Atk"},
    "Bashful": {"Increases": "Sp. Atk", "Decreases": "Sp. Atk"},
    "Bold": {"Increases": "Defense", "Decreases": "Attack"},
    "Brave": {"Increases": "Attack", "Decreases": "Speed"},
    "Calm": {"Increases": "Sp. Def", "Decreases": "Attack"},
    "Careful": {"Increases": "Sp. Def", "Decreases": "Sp. Atk"},
    "Docile": {"Increases": None, "Decreases": None},
    "Gentle": {"Increases": "Sp. Def", "Decreases": "Defense"},
    "Hardy": {"Increases": None, "Decreases": None},
    "Hasty": {"Increases": "Speed", "Decreases": "Defense"},
    "Impish": {"Increases": "Defense", "Decreases": "Sp. Atk"},
    "Jolly": {"Increases": "Speed", "Decreases": "Sp. Atk"},
    "Lax": {"Increases": "Defense", "Decreases": "Sp. Def"},
    "Lonely": {"Increases": "Attack", "Decreases": "Defense"},
    "Mild": {"Increases": "Sp. Atk", "Decreases": "Defense"},
    "Modest": {"Increases": "Sp. Atk", "Decreases": "Attack"},
    "Naive": {"Increases": "Speed", "Decreases": "Sp. Def"},
    "Naughty": {"Increases": "Attack", "Decreases": "Sp. Def"},
    "Quiet": {"Increases": "Sp. Atk", "Decreases": "Speed"},
    "Quirky": {"Increases": None, "Decreases": None},
    "Rash": {"Increases": "Sp. Atk", "Decreases": "Sp. Def"},
    "Relaxed": {"Increases": "Defense", "Decreases": "Speed"},
    "Sassy": {"Increases": "Sp. Def", "Decreases": "Speed"},
    "Serious": {"Increases": None, "Decreases": None},
    "Timid": {"Increases": "Speed", "Decreases": "Attack"}
    }

    nature = self.nature
    if nature in nature_effects:
        increased_stat = nature_effects[nature]["Increases"]
        decreased_stat = nature_effects[nature]["Decreases"]

        if increased_stat:
            setattr(self, increased_stat.lower(), getattr(self, increased_stat.lower()) * 1.1)
        if decreased_stat:
            setattr(self, decreased_stat.lower(), getattr(self, decreased_stat.lower()) * 0.9)

def receive_status(self, status):
    self.status = status
    print(f"{self.name} is now {status}.")

class Trainer:
    def __init__(self, name):
        self.name = name
        self.pokemon_team = []

    def add_pokemon(self, pokemon):
        if len(self.pokemon_team) < 6:
            self.pokemon_team.append(pokemon)
            print(f"Pokémon {pokemon.name} adicionado ao time do {self.name}.")
        else:
            print("Você não pode adicionar mais do que 6 Pokémon ao time.")
        
    def remove_pokemon(self, pokemon_name):
        for pokemon in self.pokemon_team:
            if pokemon.name == pokemon_name:
                self.pokemon_team.remove(pokemon)
                print(f"Pokémon {pokemon_name} removido do time do {self.name}.")
                return
        print(f"Pokémon {pokemon_name} não encontrado no time do {self.name}.")
        
    def select_pokemon(self):
        if not self.pokemon_team:
            print(f"{self.name} não possui Pokémon no time.")
            return None
        return random.choice(self.pokemon_team)

    def switch_active_pokemon(self, pokemon_index):
        if 0 <= pokemon_index < len(self.pokemon_team):
            self.active_pokemon = self.pokemon_team[pokemon_index]
        else:
            print("Invalid Pokémon index.")

    def select_move(self, opponent):
        print(f"{self.name}'s moveset:")
        if len(self.moveset) > 4:
            selected_moves = random.sample(self.moveset, 4)
        else:
            selected_moves = self.moveset
        for move in selected_moves:
            print(f"- {move}")
        self.selected_move = random.choice(selected_moves)
        print(f"{self.name} selected move: {self.selected_move}")
    
    def get_opponent(self):
        # Retorna o Pokémon ativo do oponente
        if self == trainer1:
            return trainer2.active_pokemon
        elif self == trainer2:
            return trainer1.active_pokemon

    def use_move(self, opponent):
        if self.active_pokemon:
            self.active_pokemon.use_move(opponent)
        else:
            print("No active Pokémon.")

class BattleRules:
    def __init__(self, weather=None, terrain=None):
        self.weather = weather
        self.terrain = terrain
        self.type_advantages = {
        'Normal': {'advantages': [], 'weaknesses': ['Fighting'], 'immunities': ['Ghost']},
        'Grass': {'advantages': ['Ground', 'Rock', 'Water'], 'weaknesses': ['Bug', 'Fire', 'Flying', 'Ice', 'Poison'], 'immunities': []},
        'Fire': {'advantages': ['Bug', 'Grass', 'Ice', 'Steel'], 'weaknesses': ['Rock', 'Water', 'Ground'], 'immunities': []},
        'Water': {'advantages': ['Fire', 'Ground', 'Rock'], 'weaknesses': ['Electric', 'Grass'], 'immunities': []},
        'Electric': {'advantages': ['Water', 'Flying'], 'weaknesses': ['Ground'], 'immunities': []},
        'Flying': {'advantages': ['Bug', 'Fighting', 'Grass'], 'weaknesses': ['Electric', 'Ice', 'Rock'], 'immunities': ['Ground']},
        'Ice': {'advantages': ['Dragon', 'Flying', 'Grass', 'Ground'], 'weaknesses': ['Fighting', 'Fire', 'Rock', 'Steel'], 'immunities': []},
        'Rock': {'advantages': ['Bug', 'Fire', 'Flying', 'Ice'], 'weaknesses': ['Fighting', 'Grass', 'Ground', 'Steel', 'Water'], 'immunities': []},
        'Ground': {'advantages': ['Electric', 'Fire', 'Poison', 'Rock', 'Steel'], 'weaknesses': ['Grass', 'Ice', 'Water'], 'immunities': ['Electric']},
        'Steel': {'advantages': ['Fairy', 'Ice', 'Rock'], 'weaknesses': ['Fighting', 'Fire', 'Ground'], 'immunities': ['Poison']},
        'Fighting': {'advantages': ['Dark', 'Ice', 'Normal', 'Rock', 'Steel'], 'weaknesses': ['Fairy', 'Flying', 'Psychic'], 'immunities': []},
        'Dark': {'advantages': ['Ghost', 'Psychic'], 'weaknesses': ['Bug', 'Fairy', 'Fighting'], 'immunities': ['Psychic']},
        'Psychic': {'advantages': ['Fighting', 'Poison'], 'weaknesses': ['Bug', 'Dark', 'Ghost'], 'immunities': []},
        'Poison': {'advantages': ['Fairy', 'Grass'], 'weaknesses': ['Ground', 'Psychic'], 'immunities': []},
        'Bug': {'advantages': ['Dark', 'Grass', 'Psychic'], 'weaknesses': ['Fire', 'Flying', 'Rock'], 'immunities': []},
        'Fairy': {'advantages': ['Dark', 'Dragon', 'Fighting'], 'weaknesses': ['Steel', 'Poison'], 'immunities': ['Dragon']},
        'Ghost': {'advantages': ['Ghost', 'Psychic'], 'weaknesses': ['Dark', 'Ghost'], 'immunities': ['Normal', 'Fighting']},
        'Dragon': {'advantages': ['Dragon'], 'weaknesses': ['Dragon', 'Fairy', 'Ice'], 'immunities': []},
        'Grass, Poison': {'advantages': ['Fairy', 'Ground', 'Rock', 'Water'], 'weaknesses': ['Psychic', 'Ice'], 'immunities': []},
        'Electric, Steel': {'advantages': ['Flying', 'Water'], 'weaknesses': ['Fire', 'Fighting', 'Ground'], 'immunities': ['Poison']},
        'Water, Dark': {'advantages': ['Fire', 'Rock', 'Ground', 'Psychic'], 'weaknesses': ['Bug', 'Electric', 'Fairy', 'Fighting', 'Grass'], 'immunities': []},
        'Ice, Psychic': {'advantages': ['Flying', 'Grass', 'Ground', 'Dragon'], 'weaknesses': ['Bug', 'Dark', 'Fire', 'Ghost', 'Rock', 'Steel'], 'immunities': []},
        'Dragon, Flying': {'advantages': ['Bug', 'Fighting', 'Grass'], 'weaknesses': ['Electric', 'Ice', 'Rock', 'Fairy'], 'immunities': ['Ground']},
        'Bug, Steel': {'advantages': ['Fairy', 'Ice', 'Rock'], 'weaknesses': ['Fire', 'Fighting', 'Ground'], 'immunities': ['Poison']},
        'Fire, Rock': {'advantages': ['Bug', 'Grass', 'Ice'], 'weaknesses': ['Water', 'Ground', 'Fighting'], 'immunities': []},
        'Grass, Fighting': {'advantages': ['Ground', 'Rock', 'Steel', 'Water'], 'weaknesses': ['Psychic', 'Flying', 'Fairy', 'Fire', 'Ice'], 'immunities': []},
        'Fire, Flying': {'advantages': ['Bug', 'Fighting', 'Grass'], 'weaknesses': ['Electric', 'Rock', 'Water'], 'immunities': ['Ground']},
        'Bug, Flying': {'advantages': ['Grass', 'Fighting', 'Psychic'], 'weaknesses': ['Electric', 'Fire', 'Rock'], 'immunities': ['Ground']},
        'Ground, Flying': {'advantages': ['Bug', 'Fighting', 'Grass'], 'weaknesses': ['Electric', 'Ice', 'Water'], 'immunities': []},
        'Electric, Flying': {'advantages': ['Water', 'Bug'], 'weaknesses': ['Ice', 'Rock'], 'immunities': ['Ground']},
        'Rock, Flying': {'advantages': ['Bug', 'Fire', 'Ice'], 'weaknesses': ['Electric', 'Ice', 'Rock', 'Steel', 'Water'], 'immunities': ['Ground']},
        'Electric, Fairy': {'advantages': ['Water', 'Fighting', 'Dragon', 'Dark'], 'weaknesses': ['Poison', 'Steel', 'Ground'], 'immunities': ['Dragon']},
        'Ice, Ghost': {'advantages': ['Flying', 'Grass', 'Ground', 'Dragon'], 'weaknesses': ['Bug', 'Dark', 'Fire', 'Rock', 'Steel'], 'immunities': ['Normal', 'Fighting']},
        'Fire, Ghost': {'advantages': ['Bug', 'Grass', 'Ice', 'Poison'], 'weaknesses': ['Ground', 'Water', 'Rock'], 'immunities': ['Normal', 'Fighting']},
        'Fire, Fairy': {'advantages': ['Bug', 'Grass', 'Ice', 'Steel'], 'weaknesses': ['Ground', 'Water', 'Rock', 'Poison'], 'immunities': []},
        'Ghost, Fairy': {'advantages': ['Dark', 'Dragon', 'Fighting', 'Psychic'], 'weaknesses': ['Poison', 'Steel'], 'immunities': ['Dragon', 'Normal']},
        'Ghost, Dark': {'advantages': ['Ghost', 'Psychic'], 'weaknesses': ['Bug', 'Fairy', 'Fighting'], 'immunities': ['Psychic', 'Normal']},
        'Ghost, Flying': {'advantages': ['Grass', 'Fighting', 'Psychic'], 'weaknesses': ['Electric', 'Fire', 'Rock'], 'immunities': ['Ground', 'Normal']},
        'Ghost, Grass': {'advantages': ['Fairy', 'Ground', 'Rock', 'Water'], 'weaknesses': ['Fire', 'Flying', 'Ice', 'Poison'], 'immunities': ['Normal']},
        'Ghost, Ground': {'advantages': ['Electric', 'Fire', 'Poison', 'Rock', 'Steel'], 'weaknesses': ['Grass', 'Ice', 'Water'], 'immunities': ['Electric', 'Normal']},
        'Ghost, Steel': {'advantages': ['Fairy', 'Ice', 'Rock'], 'weaknesses': ['Fighting', 'Fire', 'Ground'], 'immunities': ['Normal', 'Poison']},
        'Electric, Psychic': {'advantages': ['Fighting', 'Poison'], 'weaknesses': ['Bug', 'Dark', 'Ghost'], 'immunities': ['Poison']},
        'Electric, Poison': {'advantages': ['Fairy', 'Grass'], 'weaknesses': ['Ground', 'Psychic'], 'immunities': ['Poison']},
        'Electric, Fairy': {'advantages': ['Water', 'Fighting', 'Dragon', 'Dark'], 'weaknesses': ['Poison', 'Steel', 'Ground'], 'immunities': ['Dragon']},
        'Bug, Fairy': {'advantages': ['Dark', 'Dragon', 'Fighting', 'Grass'], 'weaknesses': ['Steel', 'Poison'], 'immunities': ['Dragon']},
        'Dark, Poison': {'advantages': ['Bug', 'Fairy', 'Fighting', 'Grass', 'Poison'], 'weaknesses': ['Ground', 'Psychic'], 'immunities': []},
        'Psychic, Poison': {'advantages': ['Bug', 'Fairy', 'Fighting', 'Grass', 'Poison'], 'weaknesses': ['Ground', 'Psychic'], 'immunities': []},
        'Dark, Fighting': {'advantages': ['Ghost', 'Ice', 'Normal', 'Rock', 'Steel'], 'weaknesses': ['Fairy', 'Flying', 'Psychic'], 'immunities': []},
        'Dark, Fairy': {'advantages': ['Ghost', 'Ice', 'Normal', 'Rock', 'Steel'], 'weaknesses': ['Fairy', 'Flying', 'Psychic'], 'immunities': ['Dragon']},
        'Dark, Electric': {'advantages': ['Ghost', 'Water'], 'weaknesses': ['Fairy', 'Ground'], 'immunities': ['Psychic']},
        'Dark, Ice': {'advantages': ['Ghost', 'Psychic'], 'weaknesses': ['Bug', 'Fairy', 'Fighting', 'Rock', 'Steel'], 'immunities': ['Psychic']},
        'Dark, Grass': {'advantages': ['Ghost', 'Psychic'], 'weaknesses': ['Bug', 'Fairy', 'Fighting', 'Fire', 'Flying', 'Ice', 'Poison'], 'immunities': ['Psychic']},
        'Dark, Ground': {'advantages': ['Ghost', 'Psychic', 'Poison'], 'weaknesses': ['Fairy', 'Fighting', 'Grass', 'Ice', 'Water'], 'immunities': ['Electric', 'Psychic']},
        'Dark, Rock': {'advantages': ['Ghost', 'Psychic'], 'weaknesses': ['Bug', 'Fairy', 'Fighting', 'Ground', 'Steel', 'Water'], 'immunities': ['Psychic']},
        'Dark, Steel': {'advantages': ['Ghost', 'Psychic'], 'weaknesses': ['Fairy', 'Fighting', 'Fire', 'Ground'], 'immunities': ['Psychic']},
        'Ice, Fairy': {'advantages': ['Dark', 'Dragon', 'Fighting', 'Grass'], 'weaknesses': ['Fire', 'Poison', 'Rock', 'Steel'], 'immunities': ['Dragon']},
        'Ice, Electric': {'advantages': ['Dragon', 'Flying', 'Grass', 'Ground'], 'weaknesses': ['Fighting', 'Fire', 'Rock', 'Steel'], 'immunities': ['Poison']},
        'Ice, Poison': {'advantages': ['Bug', 'Fairy', 'Fighting', 'Grass'], 'weaknesses': ['Ground', 'Psychic'], 'immunities': []},
        'Ice, Ghost': {'advantages': ['Flying', 'Grass', 'Ground', 'Dragon'], 'weaknesses': ['Bug', 'Dark', 'Fire', 'Rock', 'Steel'], 'immunities': ['Normal', 'Fighting']},
        'Ice, Flying': {'advantages': ['Bug', 'Fighting', 'Grass'], 'weaknesses': ['Electric', 'Rock', 'Steel'], 'immunities': ['Ground']},
        'Ice, Rock': {'advantages': ['Bug', 'Fire', 'Flying', 'Ice'], 'weaknesses': ['Fighting', 'Ground', 'Steel', 'Water'], 'immunities': []},
        'Ice, Steel': {'advantages': ['Fairy', 'Ice', 'Rock'], 'weaknesses': ['Fighting', 'Fire', 'Ground'], 'immunities': ['Poison']},
        'Fairy, Flying': {'advantages': ['Grass', 'Fighting', 'Psychic'], 'weaknesses': ['Electric', 'Fire', 'Rock'], 'immunities': ['Ground', 'Normal']},
        'Fairy, Ground': {'advantages': ['Electric', 'Fire', 'Poison', 'Rock', 'Steel'], 'weaknesses': ['Grass', 'Ice', 'Water'], 'immunities': ['Electric', 'Normal']},
        'Fairy, Steel': {'advantages': ['Fairy', 'Ice', 'Rock'], 'weaknesses': ['Fighting', 'Fire', 'Ground'], 'immunities': ['Normal', 'Poison']},
        }
        
    def calculate_damage(self, move_info, attacker, defender):
        # Base damage formula
        power = move_info['power']
        attack = attacker.attack
        defense = defender.defense
        if move_info['damage_class'] == 'special':
            attack = attacker.sp_attack
            defense = defender.sp_defense
        base_damage = (((2 * attacker.level / 5 + 2) * power * attack / defense) / 50) + 2
        
        # Type effectiveness
        move_type = move_info['type'].capitalize()
        defender_types = [defender.type1, defender.type2]
        effectiveness = 1.0
        for defender_type in defender_types:
            if defender_type is not None:
                defender_type = defender_type.capitalize()
                if defender_type in self.type_advantages[move_type]['advantages']:
                    effectiveness *= 2
                elif defender_type in self.type_advantages[move_type]['weaknesses']:
                    effectiveness *= 0.5
                elif defender_type in self.type_advantages[move_type]['immunities']:
                    effectiveness *= 0
        
        damage = base_damage * effectiveness
        return damage
    
class BattleSimulator:
    def __init__(self, pokemon1, pokemon2):
        self.pokemon1 = pokemon1
        self.pokemon2 = pokemon2
        self.battle_rules = BattleRules()

    def start_battle(self):
        print(f"A battle between {self.pokemon1.name} and {self.pokemon2.name} begins!\n")
        
        while self.pokemon1.hp > 0 and self.pokemon2.hp > 0:
            print(f"{self.pokemon1.name}'s turn:")
            self.pokemon1.select_move(self.pokemon2)  # Pass opponent as argument
            self.pokemon1.use_move(self.pokemon2)
            
            if self.pokemon2.hp <= 0:
                print(f"{self.pokemon2.name} fainted!")
                break  # If opponent faints, battle ends
            
            print(f"{self.pokemon2.name}'s turn:")
            self.pokemon2.select_move(self.pokemon1)  # Pass opponent as argument
            self.pokemon2.use_move(self.pokemon1)
            
            if self.pokemon1.hp <= 0:
                print(f"{self.pokemon1.name} fainted!")
                break  # If active Pokemon faints, battle ends

        # Check which Pokemon won the battle
        if self.pokemon1.hp <= 0 and self.pokemon2.hp <= 0:
            print("It's a draw!")
        elif self.pokemon1.hp <= 0:
            print(f"{self.pokemon2.name} wins!")
        elif self.pokemon2.hp <= 0:
            print(f"{self.pokemon1.name} wins!")
    

# Criando os objetos Pokémon
pikachu = Pokemon(25, "Pikachu", None, "Electric", None, ["Thunder Shock", "Quick Attack", "Iron Tail", "Electro Ball"], 35, 55, 40, 50, 50, 90, "Jolly", BattleRules())
charmander = Pokemon(4, "Charmander", None, "Fire", None, ["Scratch", "Ember", "Smokescreen", "Dragon Breath"], 39, 52, 43, 60, 50, 65, "Brave", BattleRules())

trainer1 = Trainer("Trainer 1")
trainer1.add_pokemon(pikachu)
trainer1.switch_active_pokemon(0)

trainer2 = Trainer("Trainer 2")
trainer2.add_pokemon(charmander)
trainer2.switch_active_pokemon(0)

battle_sim = BattleSimulator(trainer1.active_pokemon, trainer2.active_pokemon)
battle_sim.start_battle()
