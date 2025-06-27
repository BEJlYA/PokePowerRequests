import json
from collections import deque, defaultdict


class Settings:
    def __init__(self, login, password):
        self.login = login # User login
        self.password = password # User password
        self.catchShine = 0 # 0/1 - catch flag shine Pokémon


class TaskManager:
    def __init__(self):
        self.fight = 1500 # Fight flag
        self.targetItems = [] # Items for drop [...['name item', 'count']...]
        self.targetPokemons = [] # List catchable Pokémon [...['nuber', 'name', 'count']...]
        self.catchGender = None # Gender catching Pokémon (venus/mars/genderless/None)
        self.catchTools = None # Name pokeball for catch Pokémon

    def add_info(self, fight, target_items, target_pokemons, catch_gender, catch_tools):
        self.targetItems = target_items
        self.targetPokemons = target_pokemons
        self.catchGender = catch_gender
        self.catchTools = catch_tools

    def priority_task(self): # метод для определения следующей цели
        if self.targetPokemons:
            pass
        else:
            pass

    def getting_pokeball_id(self, pokeballs: list) -> None: # Сделать позже в GUI подсказку по названиям покеболов
        for element in pokeballs:
            if element.name == self.catchTools:
                self.catchTools = element.id

    def check_drop(self, client: object, log: list[dict]) -> None:
        for part in log:
            obj_type = part.get('object')

            if obj_type == 'item':
                name = part.get('name')
                count = int(part.get('count', 'x1').strip('x'))

                for target in client.tasks.targetItems:
                    if target[0] == name:
                        target[1] = str(max(int(target[1]) - count, 0))
            elif obj_type == 'pokemon':
                num = part.get('num')

                for target in client.tasks.targetPokemons:
                    if target[0] == num:
                        target[2] = str(max(int(target[2]) - 1, 0))

        client.tasks.targetItems = [item for item in client.tasks.targetItems if int(item[1]) > 0]
        client.tasks.targetPokemons = [poke for poke in client.tasks.targetPokemons if int(poke[2]) > 0]

        self.check_fight()

    def check_fight(self) -> None:
        self.fight = self.fight - 1
        if self.fight <= 0:
            raise 'Исполнено желаемое количество боёв' # В будущем написать вызов алерта


class MyTarget:
    def __init__(self, id: str):
        self.atks = [] # List of attack [...[category damage, id, name, pp_count, max_pp, type]...]
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

    def add_info(
            self, basenum2: int, gender: str, hp: int, lvl: int,
            name: str, sparka: str, sparka_number: int, start: int, type_text_color: int
    ) -> None:
        self.basenum2 = basenum2
        self.gender = gender
        self.hp = hp
        self.lvl = lvl
        self.name = name
        self.sparka = sparka
        self.sparkaNumber = sparka_number
        self.start = start
        self.type_text_color = type_text_color

    def last_atk(self) -> int:
        sum_of_pp = 0

        for atk in self.atks:
            if atk[0] in (1,2):
                sum_of_pp += atk[3]
        return sum_of_pp

    def add_atk(self, data: list) -> None:
        self.atks.append(data)

    def reduce_count_attack(self, attack_id: int) -> None:
        for attack in self.atks:
            if attack_id in attack[1]:
                attack[3] -= 1

    def restore_pp(self) -> None:
        for atk in self.atks:
            if not atk[3] == atk[4]:
                atk[3] += atk[4] - atk[3]


class EnemyTarget:
    def __init__(self):
        self.basenum2 = None # Pokedex number
        self.name = None # Pokemon name
        self.hp = None # Amount HP
        self.lvl = None # Pokémon level
        self.sex2 = None # Pokemon gender (venus/mars/genderless)
        self.type_text_color = None # 0/1 - (Dont) shine pokemon
        self.catch = 1 # 1/0 - Can/Can't be caught

    def add_info(
            self, basenum2: int, name: str, hp: int, lvl: int,
            sex2: int, type_text_color: int, catch: int
    ) -> None:
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

    def add_item(self, name: str, id: int, count: int) -> None:
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


class DataLocation:
    def __init__(self, name: str, id: str, region:str, routes: list, habitat: list, items: list):
        self.name = name
        self.id = id
        self.region = region
        self.routes = routes
        self.habitat = habitat
        self.items = items

    def resolve_routes(self, location_list: list) -> None:
        id_to_location = {loc.id: loc for loc in location_list}
        self.routes = [id_to_location[route['id']] for route in self.routes if route['id'] in id_to_location]

    @classmethod
    def load_all(cls):
        with open('data/locations.json', 'r', encoding='utf-8') as f:
            raw_data = json.load(f)

        locations = [cls(
            name=loc['name'],
            id=loc['id'],
            region=loc['region'],
            routes=loc['routes'],
            habitat=loc['habitat'],
            items=loc['items']
        ) for loc in raw_data]

        for loc in locations:
            loc.resolve_routes(locations)

        return locations

    @staticmethod
    def delete_excess(region: str, locations: list) -> list:
        for location in locations:
            if location.region != region:
                del locations[locations.index(location)]
        return locations

    @staticmethod
    def find_shortest_path(start: object, end: object):
        visited = set()
        queue = deque([(start, [start])])

        while queue:
            current, path = queue.popleft()

            if current.id == end.id:
                return path

            visited.add(current.id)

            for neighbor in current.routes:
                if neighbor.id not in visited:
                    queue.append((neighbor, path + [neighbor]))

        return None

    @staticmethod
    def find_shortest_named_path(name_from: str, name_to: str, locations: list) -> list or None:
        from_name = name_from.lower()
        to_name = name_to.lower()

        locations_by_name = defaultdict(list)
        for location in locations:
            locations_by_name[location.name.lower()].append(location)

        start_candidates = locations_by_name[from_name]
        end_candidates = locations_by_name[to_name]

        best_path = None
        shortest = float('inf')

        for start in start_candidates:
            for end in end_candidates:
                path = DataLocation.find_shortest_path(start, end)
                if path and len(path) < shortest:
                    best_path = path
                    shortest = len(path)

        if best_path:
            return [loc.id for loc in best_path][1:]
        else:
            Exception('Путь не найден.')


class MyPosition:
    def __init__(self):
        self.name = None
        self.id = None
        self.region = None
        self.routes = None

    def add_info(self, name: str, id: str, region: str, routes: list) -> None:
        self.name = name
        self.id = id
        self.region = region
        self.routes = routes
