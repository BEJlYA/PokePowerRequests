import json

from src.config.manager import config


class DataPokemon:
    def __init__(self):
        with open('data/pokedex.json', 'r', encoding='UTF-8') as file:  # All Pokémon
            self.pokedex = json.load(file)
        with open('data/punch_effectiveness.json', 'r', encoding='UTF-8') as file:  # Table of attack effectiveness
            self.punchEffectiveness = json.load(file)
        with open('data/rare_pokemons.json', 'r', encoding='UTF-8') as file:  # Rare pokemons
            self.rarePokemons = json.load(file)
            self._create_lookup_tables()

        self.priorityPokeballs = config.priority
        self.specialPriorityPokeballs = config.special_priority

    def _create_lookup_tables(self):
        self.by_basenum = {}
        self.by_name = {}

        for pokemon in self.pokedex:
            if 'basenum' in pokemon:
                self.by_basenum[pokemon['basenum']] = pokemon

            if 'name' in pokemon:
                self.by_name[pokemon['name']] = pokemon

    def find_pokemon_types(self, basenum=None, name=None):
        if basenum and basenum in self.by_basenum:
            return self.by_basenum[basenum].get('types', [])
        elif name and name in self.by_name:
            return self.by_name[name].get('types', [])
        return []
