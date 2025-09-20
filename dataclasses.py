import json
from collections import deque
from typing import Union, List


class Settings:
    def __init__(self, login, password):
        self.login = login # User login
        self.password = password # User password


class TaskManager:
    def __init__(self):
        self.currentFights = 0 # Current number of battles, automatic definition
        self.maxFights = 1500 # Maximum number of battles - 1500
        self.catchShine = True # Flag for catching shine Pokémon, by default - TRUE
        self.targetItems = [] # Items for drop [...{'name': '', 'count': ''}...]
        self.targetPokemons = [] # List catchable Pokémon [...{'num': '', 'name': '', 'gender': 'venus/mars/genderless/any', 'count': ''}...]
        self.catchTools = None # Name pokeball for catch Pokémon ('Покебол')
        self.hadTasks = False # FALSE - disconnect of tasks

    def add_info(self, target_items: list, target_pokemons: list, catch_tools: str) -> None:
        self.targetItems = sorted(target_items, key=lambda item: int(item.get('count', 0)))
        self.targetPokemons = sorted(target_pokemons, key=lambda poke: int(poke.get('count', 0)))
        self.catchTools = catch_tools
        self.hadTasks = bool(target_items or target_pokemons)

    def priority_task(self) -> dict | None:
        if not self.hadTasks:
            return None
        elif self.targetPokemons:
            return self.targetPokemons[0]
        elif self.targetItems:
            return self.targetItems[0]
        return None

    def getting_pokeball_id(self, pokeballs: list) -> None:
        for element in pokeballs:
            if element.name == self.catchTools:
                self.catchTools = element.id

    async def check_drop(self, client: object, log: list[dict]) -> None:
        for part in log:
            obj_type = part.get('object')

            if obj_type == 'item':
                name = part['name']

                count_str = part.get('count', 'x1').strip('x')
                count = int(count_str) if count_str else 1

                for item in client.tasks.targetItems:
                    if item.get('name') == name:
                        item['count'] = max(int(item.get('count')) - count, 0)

            elif obj_type == 'pokemon':
                element = MyTarget(client.enemy.id)
                element.add_info(
                    basenum2=client.enemy.basenum2,
                    gender=client.enemy.sex2,
                    hp=client.enemy.hp,
                    lvl=client.enemy.lvl,
                    name=client.enemy.name,
                    sparka='',
                    sparka_number=0,
                    start=0,
                    type_text_color=client.enemy.type_text_color
                )
                client.team.append(element)

                for poke in client.tasks.targetPokemons:

                    if poke['num'] == part.get('num') or poke['name'] == part.get('name'):

                        if poke.get('gender') is None:
                            poke['count'] = max(int(poke.get('count')) - 1, 0)
                            break
                        elif poke.get('gender') == client.enemy.sex2:
                            poke['count'] = max(int(poke.get('count')) - 1, 0)
                            break

        client.tasks.targetItems = [item for item in client.tasks.targetItems if int(item.get('count')) > 0]
        client.tasks.targetPokemons = [poke for poke in client.tasks.targetPokemons if int(poke.get('count')) > 0]

        self.currentFights += 1

        await self.check_tasks(client)

    async def check_tasks(self, client: object) -> Exception | None:
        if self.currentFights >= self.maxFights:
            raise Exception('Исполнено максимально возможное количество боёв за сутки')

        elif self.hadTasks and not self.targetItems and not self.targetPokemons:
            raise Exception('Выполнены все условия поставленных задач!')

        elif self.hadTasks and self.targetItems or self.targetPokemons:
            next_task = self.priority_task()

            if next_task:

                task_name = next_task.get('name') # or next_task.get('num')

                if task_name:
                    target_location_names = DataLocation.find_specific_loc(task_name, client.route_map)

                    if target_location_names:
                        path = DataLocation.find_shortest_named_path(
                            id_from=client.position.id,
                            name_to=target_location_names,
                            locations=client.route_map
                        )

                        if path:
                            final_location_id = path[-1] if path else None
                            final_location_name = None

                            for loc in client.route_map:
                                if loc.id == final_location_id:
                                    final_location_name = loc.name
                                    break

                            client.assault = 'false'

                            for step in path:
                                result = await client.route(step, final_location_name)

                                if not result:
                                    break

                            client.assault = 'true'


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
        self.id = None
        self.basenum2 = None # Pokedex number
        self.name = None # Pokemon name
        self.hp = None # Amount HP
        self.lvl = None # Pokémon level
        self.sex2 = None # Pokemon gender (venus/mars/genderless)
        self.type_text_color = None # 0/1 - (Dont) shine pokemon
        self.catch = 1 # 1/0 - Can/Can't be caught

    def add_info(
            self, id: int, basenum2: int, name: str, hp: int, lvl: int,
            sex2: int, type_text_color: int, catch: int
    ) -> None:
        self.id = id
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
            self._create_lookup_tables()

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
    def find_specific_loc(task_object: str, locations: list) -> list | None:
        found_locations = []

        if not task_object or not locations:
            return None

        for location in locations:
            for pokemon in location.habitat:
                if pokemon.get('name') == task_object:
                    found_locations.append(location.name)
            for item in location.items:
                if item.get('name') == task_object:
                    found_locations.append(location.name)

        return found_locations

    @staticmethod
    def find_path_by_objects(start: object, end: object):
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
    def find_shortest_named_path(id_from: str, name_to: Union[str, List[str]], locations: list) -> Union[
        List[str], List[List[str]]]:
        loc_by_id = {loc.id: loc for loc in locations}

        start_loc = loc_by_id.get(id_from)
        if not start_loc:
            raise Exception(f'Стартовая локация с ID "{id_from}" не найдена')

        loc_dict = {loc.name.lower(): loc for loc in locations}

        if isinstance(name_to, str):
            end_loc = loc_dict.get(name_to.lower())
            if not end_loc:
                raise Exception(f'Конечная локация "{name_to}" не найдена')

            if start_loc.id == end_loc.id:
                return []

            path = DataLocation.find_path_by_objects(start_loc, end_loc)
            if not path:
                raise Exception(f'Путь из "{start_loc.name}" в "{name_to}" не найден')

            return [loc.id for loc in path][1:]

        elif isinstance(name_to, list):
            paths = []
            for target_name in name_to:
                end_loc = loc_dict.get(target_name.lower())
                if not end_loc:
                    continue

                if start_loc.id == end_loc.id:
                    return []

                path = DataLocation.find_path_by_objects(start_loc, end_loc)
                if path:
                    path_ids = [loc.id for loc in path][1:]
                    paths.append((len(path_ids), path_ids))

            return min(paths, key=lambda x: x[0])[1] if paths else []

        else:
            raise TypeError('name_to должен быть строкой или списком строк')

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