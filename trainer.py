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

    def battle_turn(self, opponent_trainer, weather=None):
        """Realiza um turno de batalha, considerando os efeitos de clima e terreno."""
        if weather and weather.is_active():
            weather.apply_effects(self.active_pokemon)

        # Lógica de seleção e execução de movimentos
        self.active_pokemon.select_move(opponent_trainer.active_pokemon)
        self.active_pokemon.use_move(opponent_trainer.active_pokemon, weather=weather)

        # Verifique se o Pokémon oponente desmaiou
        if opponent_trainer.active_pokemon.hp <= 0:
            print(f"{opponent_trainer.active_pokemon.name} desmaiou!")

    def handle_fainted_pokemon(self):
        print(f"{self.active_pokemon.name} desmaiou!")
        if not any(pokemon.hp > 0 for pokemon in self.pokemon_team):
            print(f"{self.name} não tem mais Pokémon disponíveis.")
            return False
        else:
            self.choose_active_pokemon()
            return True

    def all_pokemons_fainted(self):
        return all(pokemon.hp == 0 for pokemon in self.pokemon_team)
