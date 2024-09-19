from battle import Battle
from trainer import Trainer
from data_fetching import select_team
from concurrent.futures import ProcessPoolExecutor
from battleRules import BattleRules
import trainer

def train_pokemon_model(pokemon):
    pokemon.train_model()
    
def load_trained_models(pokemon):
    for pokemon in trainer.pokemon_team:
        pokemon.load_model()

def main():
    print("Iniciando simulação de batalha...")

    battle_rules = BattleRules()

    # Criar treinadores
    trainer1 = Trainer("Ash")
    trainer2 = Trainer("Gary")

    # Selecionar Pokémon para os times
    print(f"Selecionando time de Pokémon para {trainer1.name}...")
    select_team(trainer1, battle_rules)  # Passa o battle_rules
    print(f"Selecionando time de Pokémon para {trainer2.name}...")
    select_team(trainer2, battle_rules)  # Passa o battle_rules

    # Iniciar a batalha
    battle = Battle(trainer1, trainer2, battle_rules)
    battle.start_battle(num_battles=1)

    # Treinar modelos para ambos os treinadores após coleta de dados
    print("Treinando modelos para Ash e Gary...")
    pokemons = trainer1.pokemon_team + trainer2.pokemon_team
    with ProcessPoolExecutor() as executor:
        executor.map(train_pokemon_model, pokemons)
        
    # Carregar os modelos treinados antes da batalha final
    print("Carregando modelos treinados para a batalha final...")
    load_trained_models(trainer1)
    load_trained_models(trainer2)

    # Batalha final após treinamento
    print("Iniciando batalha final após treinamento...")
    battle.start_battle(num_battles=1)

if __name__ == "__main__":
    main()
