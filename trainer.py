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
        # Filter out fainted Pokémon (HP <= 0)
        available_pokemons = [pokemon for pokemon in self.pokemon_team if pokemon.hp > 0]
        
        if available_pokemons:
            self.active_pokemon = random.choice(available_pokemons)
            print(f"{self.name} escolheu {self.active_pokemon.name} como Pokémon ativo.")
        else:
            # If no Pokémon are available, the trainer has lost
            print(f"{self.name} não tem nenhum Pokémon disponível para lutar.")
            self.active_pokemon = None  # Set to None if no Pokémon are available
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
        if self.active_pokemon.hp <= 0:  # Check if the active Pokémon is fainted
            print(f"{self.active_pokemon.name} is fainted and cannot move!")
            if not self.handle_fainted_pokemon():  # Try to switch to another Pokémon
                return  # End the turn if no Pokémon are available
        if weather and weather.is_active():
            weather.apply_effects(self.active_pokemon)

        # Lógica de seleção e execução de movimentos
        self.active_pokemon.select_move(opponent_trainer.active_pokemon)
        self.active_pokemon.use_move(opponent_trainer.active_pokemon, weather=weather)

        # Verifique se o Pokémon oponente desmaiou
        if opponent_trainer.active_pokemon.hp <= 0:
            print(f"{opponent_trainer.active_pokemon.name} desmaiou!")
            if not opponent_trainer.handle_fainted_pokemon():
                return  # If no Pokémon are left, end the battle

    def handle_fainted_pokemon(self):
        """Handle the situation when the active Pokémon faints."""
        print(f"{self.active_pokemon.name} desmaiou!")
        if not any(pokemon.hp > 0 for pokemon in self.pokemon_team):
            print(f"{self.name} não tem mais Pokémon disponíveis.")
            return False  # End the battle if no Pokémon are left
        else:
            self.choose_active_pokemon()  # Choose another Pokémon if available
            return True  # Return True if a new Pokémon is selected

    def all_pokemons_fainted(self):
        return all(pokemon.hp == 0 for pokemon in self.pokemon_team)
