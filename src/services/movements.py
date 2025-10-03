import asyncio
import time

from src.services.navigator import DataLocation
from src.utils.decorators import BotDecorator


class MovementsController:
    @staticmethod
    @BotDecorator.reformat_response
    async def status_authentication(json_data: dict) -> None:
        if json_data['error'] == 1:
            raise Exception(json_data['text'])

    @staticmethod
    @BotDecorator.reformat_response
    async def technical_works(json_data: dict, client: object) -> None:
        if json_data['response']['tech'] == 1:
            client.logger.warning('Technical work detected')

            await asyncio.sleep(15 * 60)

    @staticmethod
    @BotDecorator.reformat_response
    async def confused_effect(json_data: dict, client: object) -> None:
        if (
                'response' in json_data and
                isinstance(json_data['response'].get('effects'), dict) and
                'confused' in json_data['response']['effects']
        ):
            sleep_time_end = json_data['response']['effects']['confused']['time']
            sleep_time_start = time.time()

            client.logger.warning('Confused effect detected')

            await asyncio.sleep(max(0, sleep_time_end - sleep_time_start))

    @staticmethod
    @BotDecorator.reformat_response
    async def migration_error(json_data: dict, id_location: str) -> bool | None:
        if json_data['response']['error'] == 15:  # Access is prohibited, you need activation of the thing
            raise Exception('Невозможно перемещение, нужно активировать предмет')
        elif json_data['response']['error'] == 16:  # Нужно пройти обучение
            raise Exception('Невозможно перемещение, нужно пройти обучение вручную')
        elif json_data['response']['error'] == 17:
            pass
        elif json_data['response']['error'] == 20:
            pass
        elif json_data['response']['error'] == 21:
            pass
        elif json_data['response']['error'] == 23:  # Access is prohibited by the effect
            raise Exception('Невозможно перемещение, мешает эффект')
        elif json_data['response'][
            'error'] == 25:  # Access is prohibited, the location is absent or the conditions for access to it are not fulfilled
            raise Exception('Невозможно перемещение, нет нужного покемона')
        elif json_data['response']['error'] == 76:  # Access is prohibited, there is no cable rope
            raise Exception('Невозможно перемещение, нет канатной веревки')
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
