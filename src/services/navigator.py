import json
from collections import deque
from typing import Union, List

from src.core.exeptions import BotShutdownError


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


class DataLocation:
    def __init__(self, name: str, id: str, region: str, routes: list, habitat: list, items: list):
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
                if pokemon.get('name') == task_object or pokemon.get('id') == task_object:
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
    def find_shortest_named_path(id_from: str, name_to: Union[str, List[str]], locations: list) -> List[str]:
        start_loc = next((loc for loc in locations if loc.id == id_from), None)

        if not start_loc:
            raise BotShutdownError(message=f'Стартовая локация с ID "{id_from}" не найдена, куда: {name_to}')

        if isinstance(name_to, str):
            target_names = [name_to.lower()]
        else:
            target_names = [name.lower() for name in name_to]

        target_locations = []
        for loc in locations:
            loc_name_lower = loc.name.lower()
            if any(target_name in loc_name_lower for target_name in target_names):
                target_locations.append(loc)

        if not target_locations:
            raise BotShutdownError(message=f'Целевые локации "{name_to}" не найдены')

        all_paths = []
        for target_loc in target_locations:
            if start_loc.id == target_loc.id:
                return []

            path = DataLocation.find_path_by_objects(start_loc, target_loc)
            if path:
                all_paths.append((len(path), path))

        if not all_paths:
            raise BotShutdownError(message=f'Пути из "{start_loc.name}" в "{name_to}" не найдены')

        shortest_path = min(all_paths, key=lambda x: x[0])[1]
        return [loc.id for loc in shortest_path][1:]
