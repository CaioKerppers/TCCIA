import random

class Trainer:
    def __init__(self, name):
        self.name = name
        self.pokemon_team = []
        self.active_pokemon = None

    def add_pokemon(self, pokemon):
        self.pokemon_team.append(pokemon)

    def switch_active_pokemon(self, index):
        if index < len(self.pokemon_team):
            self.active_pokemon = self.pokemon_team[index]
            print(f"{self.name} escolheu {self.active_pokemon.name} como Pokémon ativo.")
        else:
            print("Índice inválido.")

    def choose_active_pokemon(self):
        available_pokemons = [pokemon for pokemon in self.pokemon_team if pokemon.hp > 0]
        if available_pokemons:
            self.active_pokemon = random.choice(available_pokemons)
            print(f"{self.name} escolheu {self.active_pokemon.name} como Pokémon ativo.")
        else:
            print(f"{self.name} não tem nenhum Pokémon disponível.")
            return False
        return True

    def select_random_pokemon(self):
        available_pokemons = [pokemon for pokemon in self.pokemon_team if pokemon.hp > 0]
        if available_pokemons:
            self.active_pokemon = random.choice(available_pokemons)
            print(f"{self.name} randomly selected {self.active_pokemon.name} as active Pokémon.")
        else:
            print(f"{self.name} has no available Pokémon.")

    def battle_turn(self, opponent_trainer):
        print(f"{self.name}'s turn.")
        if self.name == "Gary":
            self.active_pokemon.select_move_automatically(opponent_trainer.active_pokemon)
        else:
            self.active_pokemon.select_move(opponent_trainer.active_pokemon)

    def handle_fainted_pokemon(self):
        print(f"{self.active_pokemon.name} fainted!")
        if not any(pokemon.hp > 0 for pokemon in self.pokemon_team):
            print(f"{self.name} has no available Pokémon.")
            return False

        if self.choose_active_pokemon():
            print(f"{self.name} automatically chose {self.active_pokemon.name} as the new active Pokémon.")
            return True
        else:
            print(f"{self.name} has no available Pokémon.")
            return False

    def all_pokemons_fainted(self):
        return all(pokemon.hp == 0 for pokemon in self.pokemon_team)
