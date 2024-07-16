import random
from fetch_functions import fetch_banned_pokemon, fetch_type_chart, fetch_natures, db
from pokemon import Pokemon
from utils import get_random_nature

def select_random_pokemons(number_of_pokemons):
    pokemon_list = []
    for _ in range(number_of_pokemons):
        random_pokemon_id = random.randint(1, 1025)  # Existem 1025 Pokémon na Pokédex total
        pokemon_info = Pokemon.get_pokemon_info(str(random_pokemon_id))
        if pokemon_info:
            pokemon_list.append(pokemon_info)
    return pokemon_list

def select_team(trainer, battle_rules):
    print(f"{trainer.name}, o seu time de Pokémon será selecionado aleatoriamente.")
    random_pokemons = select_random_pokemons(battle_rules.team_size)
    for pokemon_info in random_pokemons:
        name, types, moveset, hp, attack, defense, sp_attack, sp_defense, speed = pokemon_info
        try:
            selected_moveset = random.sample(moveset, min(4, len(moveset)))
            nature = get_random_nature(db.collection('Natures'))
            pokemon = Pokemon(
                number=random.randint(1, 1000),
                name=name,
                form=None,
                type1=types[0],
                type2=types[1] if len(types) > 1 else None,
                moveset=selected_moveset,
                hp=hp,
                attack=attack,
                defense=defense,
                sp_attack=sp_attack,
                sp_defense=sp_defense,
                speed=speed,
                nature=nature,
                battle_rules=battle_rules
            )
            if not pokemon.is_banned():
                trainer.add_pokemon(pokemon)
                print(f"{pokemon.name} foi adicionado ao time de {trainer.name}.")
            else:
                print(f"{pokemon.name} é banido e não pode ser selecionado.")
        except ValueError as e:
            print(e)
