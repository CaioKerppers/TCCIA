import random
from fetch_functions import fetch_banned_pokemon, fetch_type_chart, fetch_natures, db
from pokemon import Pokemon
from utils import get_random_nature

def select_random_pokemons(num_pokemons, battle_rules):
    selected_pokemons = []
    for _ in range(num_pokemons):
        pokemon_id = random.randint(1, 1025)  # Considerando a faixa de IDs de Pokémon conhecidos
        pokemon_info = Pokemon.get_pokemon_info(pokemon_id)
        if pokemon_info:
            id, name, types, moveset, hp, attack, defense, sp_attack, sp_defense, speed = pokemon_info
            selected_pokemons.append(Pokemon(
                number=id,
                id=id,
                name=name,
                form=None,
                type1=types[0],
                type2=types[1] if len(types) > 1 else None,
                moveset=moveset,
                hp=hp,
                attack=attack,
                defense=defense,
                sp_attack=sp_attack,
                sp_defense=sp_defense,
                speed=speed,
                nature=get_random_nature(db.collection('Natures')),
                battle_rules=battle_rules
            ))
        else:
            print(f"Pokémon ID {pokemon_id} não é válido ou não pôde ser recuperado.")
    return selected_pokemons

def select_team(trainer, battle_rules):
    print(f"{trainer.name}, o seu time de Pokémon será selecionado aleatoriamente.")
    random_pokemons = select_random_pokemons(battle_rules.team_size, battle_rules)
    for pokemon in random_pokemons:
        try:
            if not pokemon.is_banned():
                trainer.add_pokemon(pokemon)
                print(f"{pokemon.name} foi adicionado ao time de {trainer.name}.")
            else:
                print(f"{pokemon.name} é banido e não pode ser selecionado.")
        except ValueError as e:
            print(e)
