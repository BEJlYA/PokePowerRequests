import json


class Settings:
    def __init__(self, login, password):
        self.login = login # User login
        self.password = password # User password
        self.fight = 1500 # Fight flag
        self.targetItems = [] # Items for drop [...['name item', 'count']...]
        self.targetPokemons = [] # List catchable Pokémon [...['nuber', 'name', 'count']...]
        self.catchGender = None # Gender catching Pokémon (venus/mars/genderless/None)
        self.catchTools = None # ID pokebal for catch Pokémon
        self.catchShine = 0 # 0/1 - catch flag shine Pokémon

    def add_info(self, fight, target_items, target_pokemons, catch_gender, catch_tools, catch_shine):
        self.fight = fight
        self.targetItems = target_items
        self.targetPokemons = target_pokemons
        self.catchGender = catch_gender
        self.catchTools = catch_tools
        self.catchShine = catch_shine

    def getting_pokeball_id(self, pokeballs): # Сделать позже в GUI подсказку по названиям покеболов
        for element in pokeballs:
            if element.name == self.catchTools:
                self.catchTools = element.id

    def check_drop(self, client, log):
        for part in log:
            if client.settings.targetItems:
                for target in client.settings.targetItems:
                    if part['object'] == 'item' and target[0] == part['name']:
                        target[1] = str(int(target[1]) - int(part['count'].strip('x')))
            elif client.settings.targetPokemons:
                for target in client.settings.targetPokemons:
                    if part['object'] == 'pokemon' and target[0] == part['num']:
                        target[2] = str(int(target[2]) - 1)
        # Написать удаление предмета если его меньше 0 и вызов алерта цели достигнуты...
        self.check_fight()

    def check_fight(self):
        self.fight = self.fight - 1
        if self.fight <= 0:
            raise 'Исполнено желаемое количество боёв' # В будущем написать вызов алерта

class MyTarget:
    def __init__(self, id):
        self.atks = [] # List of attack [...[category, id, name, pp_count, max_pp, type]...]
        self.basenum2 = None # Pokedex number
        self.gender = None # Pokemon gender (venus/mars/genderless)
        self.hp = None # Count of HP
        self.id = id # Pokemon ID
        self.lvl = None # Pokémon level
        self.name = None # Pokemon name
        self.sparka = None # Mating availability
        self.sparkaNumber = None # Mating compatibility
        self.start = None # Priority flag
        self.type_text_color = None # 0/1 - (Dont) shine pokemon

    def add_atk(self, data):
        self.atks.append(data)

    def reduce_count_attack(self, attack_id):
        for attack in self.atks:
            if attack_id in attack[1]:
                attack[3] = str(int(attack[3]) - 1)

    def add_info(self, basenum2, gender, hp, lvl, name, sparka, sparka_number, start, type_text_color):
        self.basenum2 = basenum2
        self.gender = gender
        self.hp = hp
        self.lvl = lvl
        self.name = name
        self.sparka = sparka
        self.sparkaNumber = sparka_number
        self.start = start
        self.type_text_color = type_text_color


class EnemyTarget:
    def __init__(self):
        self.basenum2 = None # Pokedex number
        self.name = None # Pokemon name
        self.hp = None # Amount HP
        self.lvl = None # Pokémon level
        self.sex2 = None # Pokemon gender (venus/mars/genderless)
        self.type_text_color = None # 0/1 - (Dont) shine pokemon
        self.catch = 1 # 1/0 - Can/Can't be caught

    def add_info(self, basenum2, name, hp, lvl, sex2, type_text_color, catch):
        self.basenum2 = basenum2
        self.name = name
        self.hp = hp
        self.lvl = lvl
        self.sex2 = sex2
        self.type_text_color = type_text_color
        self.catch = catch


class UsingPokeballs:
    def __init__(self):
        self.name = None # Name of pokeball
        self.id = None # ID pokeball
        self.count = None # Count of pokeballs

    def add_item(self, name, id, count):
        self.name = name
        self.id = id
        self.count = count

    def reduce_count_pokeball(self):
        self.count = self.count - 1


class DataPokemon:
    def __init__(self):
        with open('data/pokedex.json', 'r', encoding='UTF-8') as file: # All Pokémon
            self.pokedex = json.load(file)
        with open('data/punch_effectiveness.json', 'r', encoding='UTF-8') as file: # Table of attack effectiveness
            self.punchEffectiveness = json.load(file)
        with open('data/priority_pokeballs.json', 'r', encoding='UTF-8') as file: # Priority pokeballs for catch
            self.priorityPokeballs = json.load(file)
        with open('data/rare_pokemons.json', 'r', encoding='UTF-8') as file: # Rare pokemons
            self.rarePokemons = json.load(file)

class MyPosition:
    def __init__(self):
        self.name = None
        self.id = None
        self.region = None
        self.routes = None

    def add_info(self, name, id, region, routes):
        self.name = name
        self.id = id
        self.region = region
        self.routes = routes

# class DataLocation:
#     def __init__(self):
#         self.allLocations = None
#
# class Location:
#     def __init__(self):
#         self.name = None
#         self.id = None
#         self.region = None
#         self.routes = []
#         self.habitat = []
#         self.items = []
#
#     def add_info(self, name, id, region, routes, habitat, items):
#         self.name = name
#         self.id = id
#         self.region = region
#         self.routes = routes
#         self.habitat = habitat
#         self.items = items