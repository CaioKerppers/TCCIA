class Weather:
    def __init__(self, weather_type=None):
        self.weather_type = weather_type
        self.turns_left = 0  # Duração do clima em turnos

    def activate_weather(self, weather_type, duration=5):
        self.weather_type = weather_type
        self.turns_left = duration
        print(f"O clima mudou para {self.weather_type} e durará {self.turns_left} turnos.")

    def decrement_turn(self):
        self.turns_left -= 1
        if self.turns_left <= 0:
            print(f"O clima {self.weather_type} dissipou-se!")
            self.weather_type = None

    def is_active(self):
        return self.weather_type is not None

    def apply_effects(self, pokemon):
        if not self.is_active():
            return
        
        if self.weather_type == "Sunshine":
            self._apply_sunshine_effects(pokemon)
        elif self.weather_type == "Harsh Sunshine":
            self._apply_harsh_sunshine_effects(pokemon)
        elif self.weather_type == "Rain":
            self._apply_rain_effects(pokemon)
        elif self.weather_type == "Heavy Rain":
            self._apply_heavy_rain_effects(pokemon)
        elif self.weather_type == "Hail":
            self._apply_hail_effects(pokemon)
        elif self.weather_type == "Snow":
            self._apply_snow_effects(pokemon)
        elif self.weather_type == "Sandstorm":
            self._apply_sandstorm_effects(pokemon)
        elif self.weather_type == "Strong Winds":
            self._apply_strong_winds_effects(pokemon)
        elif self.weather_type == "Fog":
            self._apply_fog_effects(pokemon)

    def _apply_sunshine_effects(self, pokemon):
        if pokemon.type1 == "Fire" or pokemon.type2 == "Fire":
            pokemon.attack *= 1.5
        if pokemon.type1 == "Water" or pokemon.type2 == "Water":
            pokemon.attack *= 0.5
        #if pokemon.ability == "Chlorophyll":
        #    pokemon.speed *= 2
       # if pokemon.ability == "Solar Power":
        #    pokemon.sp_attack *= 1.5
        #    pokemon.hp -= pokemon.max_hp * 0.1  # Reduz o HP a cada turno

    def _apply_harsh_sunshine_effects(self, pokemon):
        if pokemon.type1 == "Fire" or pokemon.type2 == "Fire":
            pokemon.attack *= 1.5
        if pokemon.type1 == "Water" or pokemon.type2 == "Water":
            pokemon.attack = 0  # Movimentos de água não funcionam
        #if pokemon.ability == "Chlorophyll":
        #    pokemon.speed *= 2
        #if pokemon.ability == "Solar Power":
        #    pokemon.sp_attack *= 1.5
        #    pokemon.hp -= pokemon.max_hp * 0.1  # Reduz o HP a cada turno

    def _apply_rain_effects(self, pokemon):
        if pokemon.type1 == "Water" or pokemon.type2 == "Water":
            pokemon.attack *= 1.5
        if pokemon.type1 == "Fire" or pokemon.type2 == "Fire":
            pokemon.attack *= 0.5
       # if pokemon.ability == "Swift Swim":
        #    pokemon.speed *= 2
       # if pokemon.ability == "Dry Skin":
        #    pokemon.hp += pokemon.max_hp * 0.125  # Recupera 1/8 do HP por turno

    def _apply_heavy_rain_effects(self, pokemon):
        if pokemon.type1 == "Water" or pokemon.type2 == "Water":
            pokemon.attack *= 1.5
        if pokemon.type1 == "Fire" or pokemon.type2 == "Fire":
            pokemon.attack = 0  # Movimentos de fogo não funcionam
        #if pokemon.ability == "Swift Swim":
        #    pokemon.speed *= 2
      #  if pokemon.ability == "Dry Skin":
       #     pokemon.hp += pokemon.max_hp * 0.125  # Recupera 1/8 do HP por turno

    def _apply_hail_effects(self, pokemon):
        if pokemon.type1 != "Ice" and pokemon.type2 != "Ice":
            pokemon.hp -= pokemon.max_hp * 0.0625  # 1/16 do HP perdido a cada turno
       # if pokemon.ability == "Snow Cloak":
        #    pokemon.evasion *= 1.2

    def _apply_snow_effects(self, pokemon):
        if pokemon.type1 == "Ice" or pokemon.type2 == "Ice":
            pokemon.defense *= 1.5  # Aumenta a defesa dos Pokémon do tipo Gelo

    def _apply_sandstorm_effects(self, pokemon):
        if pokemon.type1 in ["Rock", "Ground", "Steel"] or pokemon.type2 in ["Rock", "Ground", "Steel"]:
            pokemon.sp_defense *= 1.5  # Aumenta a defesa especial desses tipos
        else:
            pokemon.hp -= pokemon.max_hp * 0.0625  # 1/16 do HP perdido a cada turno

    def _apply_strong_winds_effects(self, pokemon):
        if "Flying" in [pokemon.type1, pokemon.type2]:
            print(f"{pokemon.name} está protegido por Strong Winds!")
            # Lógica para reduzir o dano de movimentos super efetivos contra Flying

            
            def modify_damage(damage, move_type):
                effectiveness = pokemon.get_type_effectiveness(move_type, ["Flying"])
                if effectiveness > 1:  # Se o movimento é super efetivo contra Flying
                    return damage * 0.5  # Reduz o dano pela metade
                return damage
            
            # Associa a função modify_damage ao Pokémon enquanto o clima estiver ativo
            pokemon.modify_damage = modify_damage

    def _apply_fog_effects(self, pokemon):
        # Fog reduz a precisão de todos os Pokémon
        pokemon.accuracy *= 0.6
        print(f"A precisão de {pokemon.name} foi reduzida por Fog.")
