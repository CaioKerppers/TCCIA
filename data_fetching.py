import random
from fetch_functions import fetch_banned_pokemon, fetch_type_chart, fetch_natures, db
from pokemon import Pokemon
from utils import get_random_nature

def select_team(trainer, battle_rules):
    print(f"{trainer.name}, escolha seu time de Pokémon:")
    while len(trainer.pokemon_team) < battle_rules.team_size:
        pokemon_name = input(f"Digite o nome do Pokémon {len(trainer.pokemon_team) + 1}: ")
        pokemon_info = Pokemon.get_pokemon_info(pokemon_name)
        if pokemon_info:
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
                    print(f"{pokemon.name} foi adicionado ao seu time.")
                else:
                    print(f"{pokemon.name} é banido e não pode ser selecionado. Escolha outro Pokémon.")
            except ValueError as e:
                print(e)
        else:
            print("Informações do Pokémon não encontradas. Tente outro nome.")
