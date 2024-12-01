import asyncio
import aiohttp
from aiohttp.log import client_logger

from handler import ResponseChecker
from dataclasses import DataPokemon


class AiohttpClient:
    def __init__(self, settings):
        self.session = None # Session
        self.team = None # Our team of Pokémon
        self.pokeballs = None # Our items for using in battle
        self.enemy = None # Enemy Pokémon in battle
        self.data = DataPokemon() # Data
        self.assault = 'true' # Assault flag for wild Pokémon
        self.id_atk = None # ID attack for send request in battle Зачееееем?
        self.settings = settings # Inherited setting of GUI

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.session:
            await self.session.close()

    async def auth(self, settings):
        async with self.session.post(
        url='https://pokepower.ru/do/sign',
        data={
            'login': settings.login,
            'password': settings.password
        }
    ) as response:
            await ResponseChecker.status_authentication(response)

    async def init(self):
        async with await self.session.post(
            url='https://pokepower.ru/do/init',
            data={
                'id': 'init',
            }
        ) as response:
            await ResponseChecker.main_response(self, response)

    async def pokemons(self):
        async with await self.session.post(
            url='https://pokepower.ru/do/pokemons',
            data={
                'id': 'pokemons',
                'type': 'open',
                'val': '2'
            }
        ) as response:
            self.team = await ResponseChecker.team_grabber(response)

    async def update(self):
        while True:
            await asyncio.sleep(3)
            async with await self.session.post(
                    url='https://pokepower.ru/do/update',
                    data={
                        'id': 'update',
                        'type': 'every',
                        'assault': self.assault
                    }
                ) as response:
                await ResponseChecker.main_response(self, response)

    async def attack(self):
        async with await self.session.post(
                    url='https://pokepower.ru/do/makasimka',
                    data={
                        'makasimka': 'true',
                        'type': 'battle',
                        'targetAtk': self.id_atk # Зачем? Если получать будем из алгоритма вычисления наиболее эфф атаки и с массива тимы
                    }
                ) as response:
            await ResponseChecker.main_response(self, response)

    async def items(self):
        async with await self.session.post(
                    url='https://pokepower.ru/do/makasimka',
                    data={
                        'makasimka': 'true',
                        'type': 'items',
                        'cat': 'ball'
                    }
                ) as response:
            self.pokeballs = await ResponseChecker.pokeballs_grabber(response)
            self.settings.getting_pokeball_id(self.pokeballs)

    async def catch(self, pokeball):
        async with await self.session.post(
                    url='https://pokepower.ru/do/makasimka',
                    data={
                        'makasimka': 'true',
                        'type': 'battle',
                        'catch': f'{pokeball}'
                    }
                ) as response:
            for element in self.pokeballs:
                if pokeball == element.id:
                    element.reduce_count()
            await ResponseChecker.main_response(self, response)