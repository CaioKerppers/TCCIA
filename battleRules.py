class BattleRules:
    def __init__(self):
        self.level_cap = 50
        self.team_size = 2

    def apply_rules(self, trainer1, trainer2):
        for trainer in [trainer1, trainer2]:
            for pokemon in trainer.pokemon_team:
                pokemon.auto_level()
                if not pokemon.check_play_restrictions(trainer.pokemon_team):
                    print(f"{pokemon.name} violates the battle rules and cannot be used.")