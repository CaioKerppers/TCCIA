from battleRules import BattleRules
from trainer import Trainer
from data_fetching import select_team

def main():
    battle_rules = BattleRules()

    # Criar treinadores
    trainer1 = Trainer("Ash")
    trainer2 = Trainer("Gary")

    # Selecionar Pokémon para os times
    select_team(trainer1, battle_rules)
    select_team(trainer2, battle_rules)

    # Aplicar regras de batalha
    battle_rules.apply_rules(trainer1, trainer2)

    # Treinar modelos de IA
    for trainer in [trainer1, trainer2]:
        for pokemon in trainer.pokemon_team:
            pokemon.train_model()

    # Selecionar Pokémon ativo
    trainer1.choose_active_pokemon()
    trainer2.choose_active_pokemon()

    # Simular batalha
    while True:
        trainer1.battle_turn(trainer2)
        if trainer2.active_pokemon.hp <= 0:
            if not trainer2.handle_fainted_pokemon():
                print(f"{trainer1.name} wins!")
                break
        if trainer2.all_pokemons_fainted():
            print(f"{trainer1.name} wins! Todos os Pokémon de {trainer2.name} estão desmaiados.")
            break

        trainer2.battle_turn(trainer1)
        if trainer1.active_pokemon.hp <= 0:
            if not trainer1.handle_fainted_pokemon():
                print(f"{trainer2.name} wins!")
                break
        if trainer1.all_pokemons_fainted():
            print(f"{trainer2.name} wins! Todos os Pokémon de {trainer1.name} estão desmaiados.")
            break

if __name__ == "__main__":
    main()
