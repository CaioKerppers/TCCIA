import random
import pokebase as pb
import pokemon

class Move:
    def __init__(self, name):
        self.name = name
        move_data = pb.move(name.lower())
        self.type = move_data.type.name.capitalize()
        self.power = move_data.power if move_data.power else 0
        self.accuracy = move_data.accuracy if move_data.accuracy else 100
        self.damage_class = move_data.damage_class.name.capitalize() if move_data.damage_class else "Status"
        self.pp = move_data.pp
        self.priority = move_data.priority
        self.effect_entries = move_data.effect_entries
        self.effect_chance = move_data.effect_chance if move_data.effect_chance else None
        self.target = move_data.target.name.capitalize()
        self.meta = move_data.meta

        # Optional attributes
        self.ailment = self.get_meta_attribute('ailment', 'name')
        self.ailment_chance = getattr(self.meta, 'ailment_chance', 0) if self.meta else 0
        self.min_hits = getattr(move_data, 'min_hits', 1)
        self.max_hits = getattr(move_data, 'max_hits', 1)
        self.min_turns = getattr(move_data, 'min_turns', 1)
        self.max_turns = getattr(move_data, 'max_turns', 1)
        self.healing = getattr(self.meta, 'healing', 0) if self.meta else 0
        self.drain = getattr(self.meta, 'drain', 0) if self.meta else 0
        self.flinch_chance = getattr(self.meta, 'flinch_chance', 0) if self.meta else 0
        self.stat_chance = getattr(self.meta, 'stat_chance', 0) if self.meta else 0
        self.stat_changes = getattr(self.meta, 'stat_changes', []) if self.meta else []
        self.critical_rate = getattr(self.meta, 'crit_rate', 0) if self.meta else 0
        self.recoil = getattr(self.meta, 'recoil', 0) if self.meta else 0
        self.special_effects = self.identify_special_effects()

    def get_meta_attribute(self, attribute_name, sub_attribute=None):
        """Helper function to access attributes within meta."""
        attribute = getattr(self.meta, attribute_name, None)
        if attribute and sub_attribute:
            return getattr(attribute, sub_attribute, '').capitalize() if attribute else None
        return None

    def identify_special_effects(self):
        """Identifies special effects of the move based on descriptions."""
        special_effects = []

        for effect in self.effect_entries:
            effect_text = effect.short_effect.lower()

            # Protect effects
            if "protects" in effect_text or "evades" in effect_text:
                special_effects.append("protect")

            # Return effects
            if "return" in effect_text:
                special_effects.append("return")

            # Recoil effects
            if "recoil" in effect_text:
                special_effects.append("recoil")

            # Healing effects
            if "heals" in effect_text or "restores hp" in effect_text:
                special_effects.append("heal")

            # Flinch effects
            if "may cause flinch" in effect_text or "may make the target flinch" in effect_text:
                special_effects.append("flinch")

            # Multi-hit moves
            if "hits 2-5 times" in effect_text or "hits twice" in effect_text:
                special_effects.append("multi-hit")

            # Priority moves
            if "priority" in effect_text or "moves first" in effect_text:
                special_effects.append("priority")

            # Status ailments
            if "paralyze" in effect_text:
                special_effects.append("paralyze-ailment")
            elif "burn" in effect_text:
                special_effects.append("burn-ailment")
            elif "freeze" in effect_text:
                special_effects.append("freeze-ailment")
            elif "sleep" in effect_text:
                special_effects.append("sleep-ailment")
            elif "poison" in effect_text:
                special_effects.append("poison-ailment")
            elif "confuse" in effect_text:
                special_effects.append("confuse-ailment")

            # Stat changes
            if "sharply raises" in effect_text:
                special_effects.append("sharply-raise-stat")
            elif "raises" in effect_text:
                special_effects.append("raise-stat")
            elif "sharply lowers" in effect_text:
                special_effects.append("sharply-lower-stat")
            elif "lowers" in effect_text:
                special_effects.append("lower-stat")

            # Drain effects
            if "drains" in effect_text or "absorbs half the damage it inflicted" in effect_text:
                special_effects.append("drain")

            # Critical hit effects
            if "more easily" in effect_text or "high critical-hit ratio" in effect_text:
                special_effects.append("high-crit")

            # Weather effects
            if "sunlight turned harsh" in effect_text:
                special_effects.append("sunlight-harsh")
            elif "it started to rain" in effect_text:
                special_effects.append("rain-start")
            elif "a sandstorm brewed" in effect_text:
                special_effects.append("sandstorm-start")
            elif "hail began to fall" in effect_text:
                special_effects.append("hail-start")

            # Terrain effects
            if "electric terrain" in effect_text:
                special_effects.append("electric-terrain")
            elif "grassy terrain" in effect_text:
                special_effects.append("grassy-terrain")
            elif "misty terrain" in effect_text:
                special_effects.append("misty-terrain")
            elif "psychic terrain" in effect_text:
                special_effects.append("psychic-terrain")

            # Attribute negation
            if "negates" in effect_text or "ignores" in effect_text:
                special_effects.append("negate-attribute")

            # Immunity effects
            if "grants immunity" in effect_text:
                special_effects.append("grant-immunity")

            # Stat swap effects
            if "switches its attack and defense" in effect_text:
                special_effects.append("swap-attack-defense")
            elif "switches its special attack and special defense" in effect_text:
                special_effects.append("swap-spattack-spdefense")

            # Self-destruct effects
            if "faints the user" in effect_text:
                special_effects.append("self-destruct")

            # Switch out effects
            if "switches out" in effect_text or "teleports" in effect_text:
                special_effects.append("switch-out")

        return special_effects

    def apply_effects(self, attacker, defender, damage=None, weather=None, terrain=None):
        """Applies special effects of the move."""
        for effect in self.special_effects:
            # Status ailments
            if effect.endswith("-ailment"):
                ailment_name = effect.split("-")[0]
                if random.random() < self.ailment_chance / 100:
                    if ailment_name not in defender.status:
                        defender.status[ailment_name] = 1
                        print(f"{defender.name} foi afetado por {ailment_name}!")
                    else:
                            print(f"{defender.name} já está sob o efeito de {ailment_name}.")

            # Protect effect
            elif effect == "protect":
                print(f"{defender.name} used Protect and is protected this turn!")
                defender.protected = True

            # Recoil damage
            elif effect == "recoil":
                recoil_damage = int(damage * self.recoil / 100)
                attacker.hp -= recoil_damage
                print(f"{attacker.name} received {recoil_damage} recoil damage!")

            # Healing effect
            elif effect == "heal":
                heal_amount = int(self.healing * attacker.base_hp / 100)
                attacker.hp = min(attacker.hp + heal_amount, attacker.base_hp)
                print(f"{attacker.name} healed for {heal_amount} HP!")

            # Flinch effect
            elif effect == "flinch":
                if random.random() < self.flinch_chance / 100:
                    defender.flinched = True
                    print(f"{defender.name} flinched and cannot move!")

            # Multi-hit effect
            elif effect == "multi-hit":
                hits = random.randint(self.min_hits, self.max_hits)
                print(f"{self.name} hits {hits} times!")

            # Priority effect
            elif effect == "priority":
                attacker.priority += self.priority
                print(f"{self.name} has priority {self.priority}!")

            # Stat changes
            elif "sharply-raise-stat" in effect:
                for change in self.stat_changes:
                    stat_name = change.stat.name
                    stat_value = change.change
                    attacker.apply_buff(stat_name, 2)
            elif "raise-stat" in effect:
                for change in self.stat_changes:
                    stat_name = change.stat.name
                    stat_value = change.change
                    attacker.apply_buff(stat_name, 1)
            elif "sharply-lower-stat" in effect:
                for change in self.stat_changes:
                    stat_name = change.stat.name
                    stat_value = change.change
                    defender.apply_debuff(stat_name, 2)
            elif "lower-stat" in effect:
                for change in self.stat_changes:
                    stat_name = change.stat.name
                    stat_value = change.change
                    defender.apply_debuff(stat_name, 1)

            # Drain effect
            elif effect == "drain":
                drained_hp = int(damage * self.drain / 100)
                attacker.hp = min(attacker.hp + drained_hp, attacker.base_hp)
                print(f"{attacker.name} drained {drained_hp} HP from {defender.name}!")

            # Critical hit rate increase
            elif effect == "high-crit":
                attacker.critical_rate += 1
                print(f"{self.name} has an increased critical hit rate!")

            # Weather effects
            elif effect.endswith("-start"):
                weather_type = effect.split("-")[0].capitalize()
                if weather:
                    weather.activate_weather(weather_type)
                    print(f"{weather_type} started!")

            # Terrain effects
            elif effect.endswith("-terrain"):
                terrain_type = effect.split("-")[0].capitalize()
                if terrain:
                    terrain.activate_terrain(terrain_type)
                print(f"{terrain_type} Terrain is now active!")

            # Attribute negation
            elif effect == "negate-attribute":
                print(f"{defender.name}'s attribute is negated!")

            # Grant immunity
            elif effect == "grant-immunity":
                    print(f"{attacker.name} is now immune to status conditions!")

            # Stat swap effects
            elif effect == "swap-attack-defense":
                attacker.attack, attacker.defense = attacker.defense, attacker.attack
                print(f"{attacker.name} swapped its Attack and Defense!")
            elif effect == "swap-spattack-spdefense":
                attacker.sp_attack, attacker.sp_defense = attacker.sp_defense, attacker.sp_attack
                print(f"{attacker.name} swapped its Special Attack and Special Defense!")

            # Self-destruct effect
            elif effect == "self-destruct":
                attacker.hp = 0
                print(f"{attacker.name} used Self-Destruct!")

            # Switch out effect
            elif effect == "switch-out":
                print(f"{attacker.name} is switching out!")

    def calculate_damage(attacker, defender, move_info):
        level = attacker.level
        move_power = move_info[2] if move_info[2] else 0
        damage_class = move_info[4].lower()
        if damage_class == "physical":
            attack_stat = attacker.attack
            defense_stat = defender.defense
        elif damage_class == "special":
            attack_stat = attacker.sp_attack
            defense_stat = defender.sp_defense
        else:
            return 0
        damage = (((2 * level / 5 + 2) * move_power * (attack_stat / defense_stat)) / 50) + 2
        if move_info[1].capitalize() in [attacker.type1, attacker.type2]:
            damage *= 1.5
        defender_types = [defender.type1, defender.type2] if defender.type2 else [defender.type1]
        type_effectiveness = pokemon.Pokemon.get_type_effectiveness(move_info[1].capitalize(), defender_types)
        damage *= type_effectiveness
        is_critical = random.random() < 0.0625
        critical = 1.5 if is_critical else 1.0
        damage *= critical
        damage *= random.uniform(0.85, 1.0)
        return damage
