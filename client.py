import asyncio
import json
from functools import wraps

import aiohttp

from dataclasses import DataPokemon, MyPosition
from handler import ResponseChecker, UniqueGenerator


class AiohttpClient:
    def __init__(self, settings):
        self.session = None # Session
        self.token = None # Hash token by authorize
        self.sid = None # Resulting SID phrase
        self.team = None # Our team of Pokémon
        self.pokeballs = None # Our items for using in battle
        self.enemy = None # Enemy Pokémon in battle
        self.data = DataPokemon() # Data
        self.assault = 'true' # Assault flag for wild Pokémon
        self.settings = settings # Inherited setting of GUI
        self.generator = UniqueGenerator() # Custom generator
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
    async def auth(self, settings):
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
    async def websocket_sid(self):
        self.token = self.session.cookie_jar.filter_cookies('https://pokepower.ru').get("hash").value
        async with self.session.get(
            url=f'https://io.pokepower.ru/socket.io/?token={self.token}&EIO={4}&transport=polling&t={await self.generator.gen_t()}',
            timeout=10
        ) as response:
            self.sid = json.loads(str(await response.text())[1:]).get('sid')

    @safe_request
    async def init(self):
        async with await self.session.post(
            url='https://pokepower.ru/do/init',
            data={
                'id': 'init',
            },
            timeout=10
        ) as response:
            await ResponseChecker.geo_position(response, self)
            await ResponseChecker.main_handler(response, self)

    @safe_request
    async def pokemons(self):
        async with await self.session.post(
            url='https://pokepower.ru/do/pokemons',
            data={
                'id': 'pokemons',
                'type': 'open',
                'val': '2'
            },
            timeout=10
        ) as response:
            self.team = await ResponseChecker.team_grabber(response)

    @safe_request
    async def update(self):
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
    async def items(self):
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
            self.settings.getting_pokeball_id(self.pokeballs)

    @safe_request
    async def catch(self, pokeball):
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
    async def attack(self, attack_id):
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
    async def route(self, id_location):
        async with await self.session.post(
            url='https://pokepower.ru/do/route',
            data={
                'id': 'route',
                'type': 'go',
                'val': id_location
            },
            timeout=10
        ) as response:
            await ResponseChecker.geo_position(response, self)
            await ResponseChecker.main_handler(response, self)