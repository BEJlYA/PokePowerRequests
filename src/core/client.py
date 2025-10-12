import asyncio
import logging

import aiohttp

from src.core.models import ResponseChecker
from src.services.battle import EnemyTarget
from src.services.loader import DataPokemon
from src.services.movements import MovementsController
from src.services.navigator import DataLocation, MyPosition
from src.services.parser import ParseGameData
from src.services.tasks import TaskManager
from src.utils.deception import DeceptionManager
from src.utils.decorators import BotDecorator
from src.utils.logger import UniversalLogger


class AiohttpClient:
    def __init__(self, settings: object):
        self.session = None  # Session
        self.deception = DeceptionManager()  # Custom generator
        self.tasks = TaskManager()  # Tasks for execution
        self.team = []  # Our team of Pokémon
        self.pokeballs = None  # Our items for using in battle
        self.enemy = EnemyTarget()  # Enemy Pokémon in battle
        self.assault = 'true'  # Assault flag for wild Pokémon
        self.settings = settings  # Inherited setting of GUI
        self.data = DataPokemon()  # Data of Pokemon
        self.route_map = DataLocation.load_all()  # Data of Route map
        self.position = MyPosition()  # Information about position
        self.logger = UniversalLogger(logging.INFO)  # Logger makes info about works

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers=self.deception.random_headers()
        )
        self.logger.bot_start()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.session:
            await self.session.close()
            self.logger.bot_stop()

    @BotDecorator.safe_request
    async def auth(self, settings: object) -> None:
        async with self.session.post(
                url='https://pokepower.ru/do/sign',
                headers=self.deception.replace_headers(self.session.headers),
                data={
                    'login': settings.login,
                    'password': settings.password
                },
                timeout=10
        ) as response:
            self.logger.info('Successful authorization...')
            await MovementsController.status_authentication(response)

    @BotDecorator.safe_request
    async def websocket_sid(self) -> None:
        token = self.session.cookie_jar.filter_cookies('https://pokepower.ru').get("hash").value
        async with self.session.get(
                url=f'https://io.pokepower.ru/socket.io/?token={token}&EIO={4}&transport=polling&t={await self.deception.gen_t()}',
                headers=self.deception.replace_headers(self.session.headers),
                timeout=10
        ):
            self.logger.debug('Socket connection successfully established...')
            return

    @BotDecorator.safe_request
    async def init(self) -> None:
        async with await self.session.post(
                url='https://pokepower.ru/do/init',
                data={
                    'id': 'init',
                },
                timeout=10
        ) as response:
            await ParseGameData.geo_position(response, self)
            self.route_map = DataLocation.delete_excess(self.position.region, self.route_map)
            await MovementsController.confused_effect(response, self)
            self.logger.debug('Initialization completed, data collected...')
            return response

    @BotDecorator.safe_request
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
            await ParseGameData.team_grabber(response, self)
            self.logger.debug("Successfully collected information about the user's Pokemon team...")

    @BotDecorator.safe_request
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
            self.pokeballs = await ParseGameData.pokeballs_grabber(response)
            self.logger.debug(f'Collected data on available pokeballs:\n'
                              f'        {[[a.name, a.count] for a in self.pokeballs]}')
            self.tasks.getting_pokeball_id(self.pokeballs)
            self.logger.debug(f'Received ID of the Pokeball selected for catching - {self.tasks.catchTools}')

    @BotDecorator.safe_request
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
            await ParseGameData.battle_settings(response, self)

    @BotDecorator.safe_request
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
                if response.status == 200:
                    self.logger.debug('Update request - sent')

                    await MovementsController.technical_works(response, self)
                    await ResponseChecker.main_handler(response, self)
                else:
                    self.logger.debug('Update request - not sent')

    @BotDecorator.safe_request
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

                    self.logger.battle_action(
                        action_type=f"Catch",
                        description=f"{element.name}: {element.count}"
                    )
            await ResponseChecker.main_handler(response, self)

    @BotDecorator.safe_request
    async def attack(self, attack: list) -> None:
        async with await self.session.post(
                url='https://pokepower.ru/do/makasimka',
                data={
                    'makasimka': 'true',
                    'type': 'battle',
                    'targetAtk': attack[1]
                },
                timeout=10
        ) as response:
            if response.status == 200:
                self.logger.battle_action(
                    action_type=f"Attack",
                    description=f"{attack[2]}: {attack[3]}/{attack[4]}"
                )
                await ResponseChecker.main_handler(response, self)
            else:
                await self.coward()

    @BotDecorator.safe_request
    async def coward(self) -> None | Exception:
        async with await self.session.post(
                url='https://pokepower.ru/do/makasimka',
                data={
                    'makasimka': 'true',
                    'type': 'battle',
                    'coward': 1
                }
        ) as response:
            if response.status == 200:
                self.logger.battle_action(
                    action_type=f"Coward",
                    description="Pokemon has low level HP"
                )
                await MovementsController.pokemon_health(response, self)
            else:
                raise Exception("Not possible to run away")

    @BotDecorator.safe_request
    async def route(self, id_location: str, fallback_target: str = 'Покецентр') -> None | bool:
        async with await self.session.post(
                url='https://pokepower.ru/do/route',
                data={
                    'id': 'route',
                    'type': 'go',
                    'val': id_location
                },
                timeout=10
        ) as response:
            self.logger.debug(f"Move to - {id_location}")

            correct_move = await MovementsController.migration_error(response, id_location)

            if correct_move:
                await ParseGameData.geo_position(response, self)
                return True
            else:
                await ParseGameData.geo_position(response, self)

                path = DataLocation.find_shortest_named_path(
                    self.position.id,
                    fallback_target,
                    self.route_map
                )
                if not path:
                    return False

                for step in path:
                    result = await self.route(step, fallback_target)
                    if not result:
                        return False

                return False

    @BotDecorator.safe_request
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
            self.logger.pokecenter(reason="Pokemon has a small amount of HP")
            await ResponseChecker.main_handler(response, self)

    @BotDecorator.safe_request
    async def send_once_pit(self, id_pokemon: str) -> None:
        async with await self.session.post(
                url='https://pokepower.ru/do/pokemons',
                data={
                    'id': 'pokemons',
                    'type': 'action',
                    'val[]': ['gopit', id_pokemon],  # ID Pokémon, which should be sent
                },
                timeout=10
        ) as response:
            self.logger.pokecenter(reason=f"Pokemon has sent to pit - {id_pokemon}")
            await ResponseChecker.main_handler(response, self)

    @BotDecorator.safe_request
    async def send_more_pit(self, id_pokemon: str) -> None:
        async with await self.session.post(
                url='https://pokepower.ru/do/pokemons',
                data={
                    'id': 'pokemons',
                    'type': 'action',
                    'val[]': ['gopitAll', id_pokemon],  # ID Pokémon of which must be left
                },
                timeout=10
        ) as response:
            self.logger.pokecenter(reason="Little place for catching, sending pokemon to pit")
            await ResponseChecker.main_handler(response, self)
