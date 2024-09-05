# battle.py
from weather import Weather
from terrain import Terrain
from battleRules import BattleRules
from trainer import Trainer

class Battle:
    def __init__(self, trainer1, trainer2, battle_rules=None):
        self.trainer1 = trainer1
        self.trainer2 = trainer2
        self.battle_rules = battle_rules if battle_rules else BattleRules()
        self.terrain = Terrain(None)  # Nenhum terreno ativo no início
        self.weather = Weather()  # Inicializa o clima

    def apply_battle_rules(self):
        """Aplica as regras da batalha, como limite de nível e tamanho do time."""
        self.battle_rules.apply_rules(self.trainer1, self.trainer2)

    def reset_teams(self):
        """Reseta o estado dos Pokémon de ambos os treinadores antes de cada batalha."""
        for trainer in [self.trainer1, self.trainer2]:
            for pokemon in trainer.pokemon_team:
                pokemon.reset()

    def battle_turn(self):
        """Executa um turno de batalha, aplicando os efeitos de terreno e clima e determinando a ordem de ataque."""
        if self.weather.is_active():
            self.weather.apply_effects(self.trainer1.active_pokemon)
            self.weather.apply_effects(self.trainer2.active_pokemon)

        if self.terrain.is_active():
            self.terrain.apply_effects(self.trainer1.active_pokemon)
            self.terrain.apply_effects(self.trainer2.active_pokemon)

        # Determinação da ordem de batalha e execução dos movimentos
        if self.trainer1.active_pokemon.compare_speed(self.trainer2.active_pokemon) == self.trainer1.active_pokemon:
            self.trainer1.battle_turn(self.trainer2, self.weather)
            if self.trainer2.active_pokemon.hp > 0:  # Se o Pokémon adversário ainda estiver vivo
                self.trainer2.battle_turn(self.trainer1, self.weather)
        else:
            self.trainer2.battle_turn(self.trainer1, self.weather)
            if self.trainer1.active_pokemon.hp > 0:  # Se o Pokémon adversário ainda estiver vivo
                self.trainer1.battle_turn(self.trainer2, self.weather)

        # Reduzir a duração do clima e do terreno após o turno
        self.weather.decrement_turn()
        self.terrain.decrement_turn()

    def check_winner(self):
        """Verifica se algum treinador venceu a batalha."""
        if self.trainer2.all_pokemons_fainted():
            #print(f"{self.trainer1.name} wins! Todos os Pokémon de {self.trainer2.name} estão desmaiados.")
            return self.trainer1
        elif self.trainer1.all_pokemons_fainted():
            #print(f"{self.trainer2.name} wins! Todos os Pokémon de {self.trainer1.name} estão desmaiados.")
            return self.trainer2
        return None

    def start_battle(self, num_battles=1):
        """Inicia a batalha entre os treinadores."""
        self.apply_battle_rules()

        for battle_num in range(num_battles):
            #print(f"Iniciando batalha {battle_num + 1}/{num_battles}...")

            # Resetar times antes de cada batalha
            self.reset_teams()

            # Selecionar Pokémon ativo
            self.trainer1.choose_active_pokemon()
            self.trainer2.choose_active_pokemon()

            while True:
                self.battle_turn()
                winner = self.check_winner()
                if winner:
                    break

        print(f"Batalha concluída. O vencedor é {winner.name}!")
        return winner
