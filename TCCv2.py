import pokebase as pb
import random
import csv

def get_state(agent_pokemon, opponent_pokemon):
    agent_hp = agent_pokemon.hp
    opponent_hp = opponent_pokemon.hp
    agent_type1 = agent_pokemon.type1
    agent_type2 = agent_pokemon.type2
    opponent_type1 = opponent_pokemon.type1
    opponent_type2 = opponent_pokemon.type2

    return (agent_hp, opponent_hp, agent_type1, agent_type2, opponent_type1, opponent_type2)

class Pokemon:
    def __init__(self, number, name, form, type1, type2, moveset, hp, attack, defense, sp_attack, sp_defense, speed, nature, battle_rules):
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
        print(f"{self.name}'s moveset:")
        if len(self.moveset) > 4:
            selected_moves = random.sample(self.moveset, 4)
        else:
            selected_moves = self.moveset
        for move in selected_moves:
            print(f"- {move}")
        self.selected_move = random.choice(selected_moves)
        print(f"{self.name} selected move: {self.selected_move}")
        self.show_move_info(opponent)


    def use_move(self, opponent):
        move_name = self.selected_move
        print(f"{self.name} used {move_name}!")
        # Obter informações do movimento
        move_info = self.get_move_info(move_name)
        if move_info:
            # Exibir descrição do movimento
            print(f"Description: {move_info['description']}")
            # Verificar se a chave 'category' existe em move_info
            if 'category' in move_info:
                print(f"Category: {move_info['category']}")
                # Calcular e exibir o dano
                damage = self.battle_rules.calculate_damage(move_info, self, opponent)
                print(f"Damage: {damage:.2f}")  # Exibe o dano causado com 2 casas decimais
                # Atualizar a tabela Q com o resultado da ação
                self.update_q_table(opponent, damage)
                # Aqui você aplicaria o dano ao oponente com base no cálculo do dano
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
        move = pb.move(move_name.lower())
        if move:
            print(f"Move Name: {move.name.capitalize()}")
            print(f"Power: {move.power}")
            print(f"Accuracy: {move.accuracy}")
            print(f"Category: {move.damage_class.name}")
            print(f"Type: {move.type.name.capitalize()}")
            effect_text = ""
            for effect_entry in move.effect_entries:
                if effect_entry.language.name == "en":
                    effect_text = effect_entry.short_effect
                    break
            
            return {
                "description": effect_text
                
            }
        else:
            print(f"Couldn't find information for move: {move_name}")
            return None
        
    def show_move_info(self, opponent):
        move_name = self.selected_move
        print(f"Selected move: {move_name}")
        move_info = self.get_move_info(move_name)
        if move_info:
            print(f"Description: {move_info['description']}")
            user_input = input(f"Do you want to use {move_name}? (Y/N): ").strip().lower()
            if user_input == 'y':
                self.use_move(opponent)
            elif user_input == 'n':
                self.select_move(opponent)
            else:
                print("Invalid input. Please enter Y or N.")
        else:
            print(f"Could not retrieve move info for {move_name}")


    def update_q_table(self, opponent, damage):
        state = get_state(self, opponent)
        if state not in self.q_table:
            self.q_table[state] = {}

        for move in self.moveset:
            if move not in self.q_table[state]:
                self.q_table[state][move] = 0

        # Atualizando o valor Q para a ação selecionada
        selected_move_value = self.q_table[state][self.selected_move]
        self.q_table[state][self.selected_move] = selected_move_value + 0.1 * (damage - selected_move_value)

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
    def __init__(self, battle_rules):
        self.pokemons = []
        self.active_pokemon = None
        self.battle_rules = battle_rules

    def add_pokemon(self, pokemon_name):
        new_pokemon_info = Pokemon.get_pokemon_info(pokemon_name)
        if new_pokemon_info:
            name, types, moveset, hp, attack, defense, sp_attack, sp_defense, speed = new_pokemon_info
            nature = random.choice(["Adamant", "Bashful", "Bold", "Brave", "Calm", "Careful", "Docile", "Gentle", "Hardy", "Hasty", "Impish", "Jolly", "Lax", "Lonely", "Mild", "Modest", "Naive", "Naughty", "Quiet", "Quirky", "Rash", "Relaxed", "Sassy", "Serious", "Timid"])
            new_pokemon = Pokemon(None, name, None, types[0], types[1] if len(types) > 1 else None, moveset, hp, attack, defense, sp_attack, sp_defense, speed, nature, self.battle_rules)
            self.pokemons.append(new_pokemon)
        else:
            print(f"Couldn't fetch data for Pokémon {pokemon_name}")

    def switch_active_pokemon(self, pokemon_index):
        if 0 <= pokemon_index < len(self.pokemons):
            self.active_pokemon = self.pokemons[pokemon_index]
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
    def __init__(self):
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
    'Ice, Ghost': {'advantages': ['Flying', 'Grass', 'Ground', 'Dragon'], 'weaknesses': ['Bug', 'Dark', 'Fire', 'Ghost', 'Rock', 'Steel'], 'immunities': ['Normal', 'Fighting']},
    'Fire, Ghost': {'advantages': ['Bug', 'Grass', 'Ice', 'Poison'], 'weaknesses': ['Ground', 'Water', 'Rock'], 'immunities': ['Normal', 'Fighting']},
    'Fire, Fairy': {'advantages': ['Bug', 'Grass', 'Ice', 'Steel'], 'weaknesses': ['Ground', 'Water', 'Rock', 'Poison'], 'immunities': []},
    'Ghost, Fairy': {'advantages': ['Dark', 'Dragon', 'Fighting', 'Psychic'], 'weaknesses': ['Poison', 'Steel'], 'immunities': ['Dragon', 'Normal']},
    'Ghost, Dark': {'advantages': ['Ghost', 'Psychic'], 'weaknesses': ['Bug', 'Fairy', 'Fighting'], 'immunities': ['Psychic', 'Normal']},
    'Ghost, Flying': {'advantages': ['Grass', 'Fighting', 'Psychic'], 'weaknesses': ['Electric', 'Fire', 'Rock'], 'immunities': ['Ground', 'Normal']},
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
    'Ice, Ghost': {'advantages': ['Flying', 'Grass', 'Ground', 'Dragon'], 'weaknesses': ['Bug', 'Dark', 'Fire', 'Ghost', 'Rock', 'Steel'], 'immunities': ['Normal', 'Fighting']},
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

    def calculate_damage(self, move, attacker, defender):
        # Verificar se o movimento é especial ou físico
        is_special = move.category == "Special"
        
        # Calcular o poder do movimento
        base_power = move.power if move.power else 0

        # Determinar o nível do atacante
        level = attacker.level

        # Calcular o tipo de dano (STAB)
        stab = 1.5 if move.type in [attacker.type1, attacker.type2] else 1

        # Calcular o tipo de vantagem
        type_advantage = self.get_type_advantage(move.type, defender)

        # Verificar se o atacante é imune ao tipo do movimento
        if move.type in self.type_advantages.get(defender.type1, {}).get("immunities", []) \
                or move.type in self.type_advantages.get(defender.type2, {}).get("immunities", []):
            type_advantage = 0  # O ataque não afeta o Pokémon defensor

        # Calcular o dano
        damage = (((2 * level + 10) / 250) * (attacker.attack / defender.defense) * base_power + 2) \
                 * stab * type_advantage

        return int(damage)

    def get_type_advantage(self, move_type, defender):
        # Obter os tipos do Pokémon defensor
        defender_types = [defender.type1]
        if defender.type2:
            defender_types.append(defender.type2)

        # Calcular o tipo de vantagem do movimento contra o Pokémon defensor
        type_advantage = 1
        for defender_type in defender_types:
            type_advantage *= self.type_advantages.get(move_type, {}).get(defender_type, 1)

        return type_advantage


    
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

# Example usage
trainer1 = Trainer(BattleRules())
trainer1.add_pokemon("pikachu")
trainer1.switch_active_pokemon(0)

trainer2 = Trainer(BattleRules())
trainer2.add_pokemon("charmander")
trainer2.switch_active_pokemon(0)

battle_sim = BattleSimulator(trainer1.active_pokemon, trainer2.active_pokemon)
battle_sim.start_battle()