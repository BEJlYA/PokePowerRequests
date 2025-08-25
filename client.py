import asyncio
import json
from functools import wraps

import aiohttp

from dataclasses import DataPokemon, DataLocation, MyPosition, TaskManager, EnemyTarget
from handler import ResponseChecker, UniqueGenerator


class AiohttpClient:
    def __init__(self, settings: object):
        self.session = None # Session
        self.token = None # Hash token by authorize
        self.sid = None # Resulting SID phrase
        self.generator = UniqueGenerator() # Custom generator
        self.tasks = TaskManager() # Tasks for execution
        self.team = [] # Our team of Pokémon
        self.pokeballs = None # Our items for using in battle
        self.enemy = EnemyTarget() # Enemy Pokémon in battle
        self.assault = 'true' # Assault flag for wild Pokémon
        self.settings = settings # Inherited setting of GUI
        self.data = DataPokemon() # Data of Pokemon
        self.route_map = DataLocation.load_all() # Data of Route map
        self.position = MyPosition() # Information about position

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.session:
            await self.session.close()

    @staticmethod
    def safe_request(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except (aiohttp.ClientConnectorError,
                    aiohttp.ServerTimeoutError,
                    asyncio.TimeoutError):
                print("Ошибка соединения: сервер недоступен или отсутствует интернет.")
            except aiohttp.ClientResponseError as e:
                print(f"Сервер вернул ошибку: {e.status} {e.message}")
            except Exception as e:
                print(f"Непредвиденная ошибка: {e}")

            return None
        return wrapper

    @safe_request
    async def auth(self, settings: object) -> None:
        async with self.session.post(
        url='https://pokepower.ru/do/sign',
        data={
            'login': settings.login,
            'password': settings.password
        },
        timeout=10
    ) as response:
            await ResponseChecker.status_authentication(response)

    @safe_request
    async def websocket_sid(self) -> None:
        self.token = self.session.cookie_jar.filter_cookies('https://pokepower.ru').get("hash").value
        async with self.session.get(
            url=f'https://io.pokepower.ru/socket.io/?token={self.token}&EIO={4}&transport=polling&t={await self.generator.gen_t()}',
            timeout=10
        ) as response:
            self.sid = json.loads(str(await response.text())[1:]).get('sid')

    @safe_request
    async def init(self) -> None:
        async with await self.session.post(
            url='https://pokepower.ru/do/init',
            data={
                'id': 'init',
            },
            timeout=10
        ) as response:
            await ResponseChecker.geo_position(response, self)
            self.route_map = DataLocation.delete_excess(self.position.region, self.route_map)
            return response

    @safe_request
    async def pokemons(self) -> None:
        async with await self.session.post(
            url='https://pokepower.ru/do/pokemons',
            data={
                'id': 'pokemons',
                'type': 'open',
                'val': '2'
            },
            timeout=10
        ) as response:
            await ResponseChecker.team_grabber(response, self)

    @safe_request
    async def update(self) -> None:
        while True:
            await asyncio.sleep(3)
            async with await self.session.post(
                    url='https://pokepower.ru/do/update',
                    data={
                        'id': 'update',
                        'type': 'every',
                        'assault': self.assault
                    },
                     timeout=10
                ) as response:
                await ResponseChecker.main_handler(response, self)

    @safe_request
    async def items(self) -> None:
        async with await self.session.post(
                    url='https://pokepower.ru/do/makasimka',
                    data={
                        'makasimka': 'true',
                        'type': 'items',
                        'cat': 'ball'
                    },
                    timeout=10
                ) as response:
            self.pokeballs = await ResponseChecker.pokeballs_grabber(response)
            self.tasks.getting_pokeball_id(self.pokeballs)

    @safe_request
    async def get_edit(self) -> None:
        async with await self.session.post(
            url='https://pokepower.ru/do/edit',
            data={
                'id': 'edit',
                'type': 'open',
                'val': 2
            },
            timeout=10
        ) as response:
            await ResponseChecker.battle_settings(response, self)

    @safe_request
    async def catch(self, pokeball: int) -> None:
        async with await self.session.post(
                    url='https://pokepower.ru/do/makasimka',
                    data={
                        'makasimka': 'true',
                        'type': 'battle',
                        'catch': f'{pokeball}'
                    },
                    timeout=10
                ) as response:
            for element in self.pokeballs:
                if pokeball == element.id:
                    element.reduce_count_pokeball()
            await ResponseChecker.main_handler(response, self)

    @safe_request
    async def attack(self, attack_id: int) -> None:
        async with await self.session.post(
                    url='https://pokepower.ru/do/makasimka',
                    data={
                        'makasimka': 'true',
                        'type': 'battle',
                        'targetAtk': attack_id
                    },
                    timeout=10
                ) as response:
            await ResponseChecker.main_handler(response, self)

    @safe_request
    async def route(self, id_location: int) -> None or bool:
        async with await self.session.post(
            url='https://pokepower.ru/do/route',
            data={
                'id': 'route',
                'type': 'go',
                'val': id_location
            },
            timeout=10
        ) as response:
            correct_move = await ResponseChecker.checking_move(response, id_location)

            if correct_move:
                await ResponseChecker.geo_position(response, self)
                return True
            else:
                path = DataLocation.find_shortest_named_path(self.position.name, "Покецентр", self.route_map)

                for step in path:
                    await self.route(step)
                return False

    @safe_request
    async def heal_npc(self) -> None:
        async with await self.session.post(
                    url='https://pokepower.ru/do/npc',
                    data={
                        'id': 'npc',
                        'type': 'addons',
                        'val[]': 'heal'
                    },
                    timeout=10
                ) as response:
            await ResponseChecker.main_handler(response, self)

    @safe_request
    async def send_once_pit(self, id_pokemon: str) -> None:
        async with await self.session.post(
                    url='https://pokepower.ru/do/pokemons',
                    data={
                        'id': 'pokemons',
                        'type': 'action',
                        'val': f'{'gopit', id_pokemon}', # ID Pokemon, which should be sent
                    },
                    timeout=10
                ) as response:
            await ResponseChecker.main_handler(response, self)

    @safe_request
    async def send_more_pit(self, id_pokemon: str) -> None:
        async with await self.session.post(
                    url='https://pokepower.ru/do/pokemons',
                    data={
                        'id': 'pokemons',
                        'type': 'action',
                        'val[]': 'gopitAll',
                        'val[1][]': f'{id_pokemon}', # ID Pokémon of which must be left
                    },
                    timeout=10
                ) as response:
            await ResponseChecker.main_handler(response, self)