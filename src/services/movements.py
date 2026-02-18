import asyncio

from src.services.navigator import DataLocation
from src.utils.decorators import BotDecorator
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
        tm = TimeManager()
        if json_data.get('response', {}).get('tech') == '1' \
                and tm.is_time_in_range(3, 4):
            client.logger.warning(message='Technical work detected...')

            time_sleep = tm.get_sleep_seconds_until(3, 25)
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
    async def migration_error(json_data: dict, id_location: str, client: object = None) -> bool:
        if json_data['response']['error'] != 0:  # Access is prohibited
            if client:
                client.logger.warning(
                    f'Перемещение в локацию недоступно, не выполнено условие, ID: {id_location}'
                )
            return False

        return str(json_data['response'].get('id')) == str(id_location)

    @staticmethod
    async def pokemon_health(client: object) -> None:
        injured = []
        for pokemon in client.team:
            injured.append(pokemon.need_heal())

        queue = []
        if len(client.team) >= 6:
            for pokemon in client.team:
                if pokemon.catchedNow:
                    queue.append(pokemon)

        if (
                injured.count(False) < 1 or
                len(client.team) >= 6 and len(queue) > 0 or
                client.tasks.notChangeHero and injured.count(True) >= 1
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

            await client.pokemons()
            if len(queue) >= 5:
                for pokemon in client.team:
                    if pokemon not in queue:
                        await client.send_more_pit(pokemon.id)
                        client.team = [pokemon]
            else:
                for pokemon in queue:
                    await client.send_once_pit(pokemon.id)

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
