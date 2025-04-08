import asyncio
import aiohttp
import json

from handler import ResponseChecker, UniqueGenerator
from dataclasses import DataPokemon


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
            self.token = self.session.cookie_jar.filter_cookies(response.url).get("hash").value
            await ResponseChecker.status_authentication(response)

    async def websocket_sid(self):
        async with self.session.get(
            url=f'https://io.pokepower.ru/socket.io/?token={self.token}&EIO={4}&transport=polling&t={await self.generator.gen_t()}'
        ) as response:
            self.sid = json.loads(str(await response.text())[1:]).get('sid')

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

    async def attack(self, attack_id):
        async with await self.session.post(
                    url='https://pokepower.ru/do/makasimka',
                    data={
                        'makasimka': 'true',
                        'type': 'battle',
                        'targetAtk': attack_id
                    }
                ) as response:
            await ResponseChecker.main_response(self, response)
