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
                break;
            elif user_input == 'n':
                self.select_move(opponent)
                break;
            else:
                print("Invalid input. Please enter Y or N.")

    def get_move_info(self, move_name):
        try:
            move = pb.move(move_name.lower())
            # Filtrar as descrições para pegar a versão em inglês
            english_descriptions = [entry for entry in move.flavor_text_entries if entry.language.name == 'en']
            # Pegar a primeira descrição em inglês
            description = english_descriptions[0].flavor_text if english_descriptions else None
            damage_class = move.damage_class.name if move.damage_class else None
            return {"description": description, "damage_class": damage_class}
        except Exception as e:
            print(f"An error occurred while fetching move info: {e}")
            return None

    def show_move_info(self, opponent):
        move_info = self.get_move_info(self.selected_move)
        if move_info:
            print(f"{self.name} está prestes a usar {self.selected_move}!")
            print(f"Descrição: {move_info['description']}")
            print(f"Categoria: {move_info['damage_class']}")
        self.confirm_attack(opponent)

    def update_q_table(self, opponent, reward):
        state = get_state(self, opponent)
        if state not in self.q_table:
            self.q_table[state] = {move: 0 for move in self.moveset}
        self.q_table[state][self.selected_move] = reward

def get_team(paste_code):
    url = f"https://pokepast.es/{paste_code}"
    team = pastes.team_from_url(url)
    if not team:
        print("Não foi possível acessar o Pokepaste ou o time está vazio.")
        return None
    
    return {'pokemons': team.members}

def select_pokemon_from_pokepastes():
    while True:
        paste_code = input("Insira o código do Pokepaste: ").strip()
        team = get_team(paste_code)
        if team:
            return team
        else:
            print("Código inválido ou equipe não encontrada. Tente novamente.")

def get_pokemon_team_from_pokepastes():
    selected_team = select_pokemon_from_pokepastes()
    team = []
    for pokemon in selected_team['pokemons']:
        name, types, moveset, hp, attack, defense, sp_attack, sp_defense, speed = Pokemon.get_pokemon_info(pokemon.species)
        type1, type2 = types if len(types) == 2 else (types[0], None)
        team.append(Pokemon(None, name, None, type1, type2, moveset, hp, attack, defense, sp_attack, sp_defense, speed, None, None, item=pokemon.item))
    return team

def main():
    print("Escolha seu time:")
    user_team = get_pokemon_team_from_pokepastes()
    for i, pokemon in enumerate(user_team):
        print(f"User's Pokemon {i + 1}: {pokemon.name}")

    print("Escolha o time do oponente:")
    opponent_team = get_pokemon_team_from_pokepastes()
    for i, pokemon in enumerate(opponent_team):
        print(f"Opponent's Pokemon {i + 1}: {pokemon.name}")

    for user_pokemon, opponent_pokemon in zip(user_team, opponent_team):
        user_pokemon.auto_level()
        opponent_pokemon.auto_level()
        print(f"Starting battle: {user_pokemon.name} vs {opponent_pokemon.name}")
        user_pokemon.select_move(opponent_pokemon)
        opponent_pokemon.select_random_move(user_pokemon)
        user_pokemon.use_move(opponent_pokemon)
        if opponent_pokemon.hp > 0:
            opponent_pokemon.use_move(user_pokemon)

if __name__ == "__main__":
    main()
