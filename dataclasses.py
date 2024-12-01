import json


class Settings:
    def __init__(self, login, password): # Может сделать цели ловли в виде списков?
        self.login = login # User login
        self.password = password # User password
        self.fight = None # Fight flag
        self.targetItems = None # Items for drop
        self.targetPokemons = [] # List catchable Pokémon ['nuber', 'name', 'count']
        self.catchGender = None # Gender catching Pokémon
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


class MyTarget:
    def __init__(self, id):
        self.atks = [] # List of attack [category, id, name, pp, type]
        self.basenum2 = None # Pokedex number
        self.gender = None # Pokemon gender (venus/mars/genderless)
        self.hp = None # Count of HP
        self.id = id # Pokemon ID
        self.lvl = None # Pokemon level
        self.name = None # Pokemon name
        self.sparka = None # Mating availability
        self.sparkaNumber = None # Mating compatibility
        self.start = None # Priority flag
        self.type_text_color = None # 0/1 - (Dont) shine pokemon

    def add_atk(self, data):
        self.atks.append(data)

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
        self.lvl = None # Pokemon level
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

    def reduce_count(self):
        self.count = self.count - 1


class DataPokemon:
    def __init__(self):
        with open('data/rare_pokemons.json', 'r') as file:
            self.rarePokemons = [['187', 'Хоппип'], ['191', 'Санкерн']] # json.load(file) # Rare pokemons
        with open('data/priority_pokeballs.json', 'r') as file:
            self.priorityPokeballs = json.load(file) # Priority pokeballs for catch
