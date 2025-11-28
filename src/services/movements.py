import asyncio

from src.services.navigator import DataLocation
from src.utils.decorators import BotDecorator
from src.utils.exeptions import BotShutdownError
from src.utils.time_manager import TimeManager


class MovementsController:
    @staticmethod
    @BotDecorator.reformat_response
    async def status_authentication(json_data: dict) -> None:
        if json_data['error'] == 1:
            raise BotShutdownError(message=json_data['text'])

    @staticmethod
    @BotDecorator.reformat_response
    async def technical_works(json_data: dict, client: object) -> None:
        if json_data.get('response', {}).get('tech') == '1':
            client.logger.warning(message='Technical work detected...')

            time_sleep = TimeManager.get_sleep_seconds_until(3, 25)
            await asyncio.sleep(time_sleep)

            client.logger.warning(message='Technical work was finished...')

    @staticmethod
    @BotDecorator.reformat_response
    async def confused_effect(json_data: dict, client: object) -> None:
        if (
                'response' in json_data and
                isinstance(json_data['response'].get('effects'), dict) and
                'confused' in json_data['response']['effects']
        ):
            time_sleep = TimeManager.calculate_time(
                time_end=json_data['response']['effects']['confused']['time']
            )

            client.logger.warning(message='Confused effect detected')

            await asyncio.sleep(time_sleep)

    @staticmethod
    @BotDecorator.reformat_response
    async def migration_error(json_data: dict, id_location: str) -> bool | None:
        if not json_data['response']['error'] == 0:  # Access is prohibited
            raise BotShutdownError(f'Перемещение невозможно, не выполнено условие, ID: {id_location}')
        else:
            return json_data['response']['id'] == id_location

    @staticmethod
    @BotDecorator.reformat_response
    async def pokemon_health(json_data: dict, client: object) -> None:
        if (
                float(json_data['battleInfo']['myTarget']['hp']) <=
                float(json_data['battleInfo']['myTarget']['hp_max'] * 0.3) or
                len(client.team) >= 6 or
                next((p for p in client.team if p.start == '1'),
                     client.team[0] if client.team else None).last_atk() <= 1
        ):
            client.assault = 'false'
            path = DataLocation.find_shortest_named_path(
                client.position.id,
                "Покецентр",
                client.route_map
            )
            last_location = client.position.name

            for step in path:
                result = await client.route(step)

                if not result:
                    break

            await client.heal_npc()
            for pokemon in client.team:
                pokemon.restore_pp()
            if len(client.team) >= 6:
                active_pokemon = next((p for p in client.team if p.start == '1'),
                                      client.team[0] if client.team else None)
                await client.send_more_pit(active_pokemon.id)
                client.team = [active_pokemon]

            path = DataLocation.find_shortest_named_path(
                client.position.id,
                last_location,
                client.route_map
            )
            for step in path:
                result = await client.route(step, last_location)

                if not result:
                    break

            client.assault = 'true'
