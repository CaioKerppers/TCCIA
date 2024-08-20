from concurrent.futures import ProcessPoolExecutor
from battleRules import BattleRules
from trainer import Trainer
from data_fetching import select_team

def train_pokemon_model(pokemon):
    pokemon.train_model()


def main():
    print("Iniciando simulação de batalha...")

    battle_rules = BattleRules()

    # Criar treinadores
    trainer1 = Trainer("Ash")
    trainer2 = Trainer("Gary")

    # Selecionar Pokémon para os times
    print(f"Selecionando time de Pokémon para {trainer1.name}...")
    select_team(trainer1, battle_rules)
    print(f"Selecionando time de Pokémon para {trainer2.name}...")
    select_team(trainer2, battle_rules)

    # Aplicar regras de batalha
    print("Aplicando regras de batalha...")
    battle_rules.apply_rules(trainer1, trainer2)

    # Função para resetar os times dos treinadores
    def reset_teams(trainer):
        for pokemon in trainer.pokemon_team:
            pokemon.reset()

    # Simular batalhas para coletar dados
    num_battles = 2  # Número de batalhas para coletar dados
    for battle_num in range(num_battles):
        print(f"Iniciando batalha {battle_num + 1}/{num_battles}...")

        # Resetar times antes de cada batalha
        reset_teams(trainer1)
        reset_teams(trainer2)

        # Selecionar Pokémon ativo
        trainer1.choose_active_pokemon()
        trainer2.choose_active_pokemon()

        while True:
            print(f"{trainer1.name} está atacando...")
            trainer1.battle_turn(trainer2)
            if trainer2.active_pokemon.hp <= 0:
                if not trainer2.handle_fainted_pokemon():
                    print(f"{trainer1.name} wins!")
                    break
            if trainer2.all_pokemons_fainted():
                print(f"{trainer1.name} wins! Todos os Pokémon de {trainer2.name} estão desmaiados.")
                break

            print(f"{trainer2.name} está atacando...")
            trainer2.battle_turn(trainer1)
            if trainer1.active_pokemon.hp <= 0:
                if not trainer1.handle_fainted_pokemon():
                    print(f"{trainer2.name} wins!")
                    break
            if trainer1.all_pokemons_fainted():
                print(f"{trainer2.name} wins! Todos os Pokémon de {trainer1.name} estão desmaiados.")
                break

    # Treinar modelos para ambos os treinadores após coleta de dados
    print("Treinando modelos para Ash e Gary...")
    pokemons = trainer1.pokemon_team + trainer2.pokemon_team
    with ProcessPoolExecutor() as executor:
        executor.map(train_pokemon_model, pokemons)

    # Batalha final após treinamento
    print("Iniciando batalha final após treinamento...")

    # Resetar times antes da batalha final
    reset_teams(trainer1)
    reset_teams(trainer2)

    trainer1.choose_active_pokemon()
    trainer2.choose_active_pokemon()

    # Mostrar a batalha final na interface gráfica
    # battle(trainer1.active_pokemon, trainer2.active_pokemon)

if __name__ == "__main__":
    main()
