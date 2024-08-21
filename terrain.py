# terrain.py
class Terrain:
    def __init__(self, terrain_type):
        self.terrain_type = terrain_type
        self.turns_left = 5  # Duração padrão para efeitos de terreno

    def apply_effects(self, pokemon):
        if self.terrain_type == "Electric Terrain":
            if pokemon.on_ground:
                pokemon.wake_up()
                if "Electric" in pokemon.type1 or "Electric" in pokemon.type2:
                    pokemon.attack *= 1.3
                if pokemon.ability == "Surge Surfer":
                    pokemon.speed *= 2
                if pokemon.ability == "Hadron Engine":
                    pokemon.increase_stat("sp_attack", 1)
                if pokemon.holding_item == "Electric Seed":
                    pokemon.increase_stat("defense", 1)
                    pokemon.consume_item()

        elif self.terrain_type == "Grassy Terrain":
            if pokemon.on_ground:
                pokemon.hp += pokemon.base_hp * 0.0625  # Restaura 1/16 do HP
                if "Grass" in pokemon.type1 or "Grass" in pokemon.type2:
                    pokemon.attack *= 1.3
                if pokemon.ability == "Grass Pelt":
                    pokemon.increase_stat("defense", 1)
                if pokemon.holding_item == "Grassy Seed":
                    pokemon.increase_stat("defense", 1)
                    pokemon.consume_item()

        elif self.terrain_type == "Misty Terrain":
            if pokemon.on_ground:
                pokemon.prevent_status_conditions()
                if "Dragon" in pokemon.type1 or "Dragon" in pokemon.type2:
                    pokemon.dragon_moves_power *= 0.5
                if pokemon.holding_item == "Misty Seed":
                    pokemon.increase_stat("sp_defense", 1)
                    pokemon.consume_item()

        elif self.terrain_type == "Psychic Terrain":
            if pokemon.on_ground:
                pokemon.prevent_priority_moves()
                if "Psychic" in pokemon.type1 or "Psychic" in pokemon.type2:
                    pokemon.attack *= 1.3
                if pokemon.holding_item == "Psychic Seed":
                    pokemon.increase_stat("sp_defense", 1)
                    pokemon.consume_item()

    def decrement_turn(self):
        self.turns_left -= 1
        if self.turns_left <= 0:
            print(f"{self.terrain_type} dissipou-se!")
            self.terrain_type = None

    def is_active(self):
        return self.terrain_type is not None
