import asyncio
import time

from src.utils.decorators import BotDecorator


class MovementsController:
    @staticmethod
    @BotDecorator.reformat_response
    async def confused_effect(json_data: dict):
        if (
                'response' in json_data and
                isinstance(json_data['response'].get('effects'), dict) and
                'confused' in json_data['response']['effects']
        ):
            sleep_time_end = json_data['response']['effects']['confused']['time']
            sleep_time_start = time.time()

            await asyncio.sleep(max(0, sleep_time_end - sleep_time_start))


    @staticmethod
    @BotDecorator.reformat_response
    async def migration_error(json_data: dict, id_location: str) -> bool:
        if json_data['response']['error'] == 15: # Access is prohibited, you need activation of the thing
            raise Exception('Невозможно перемещение, нужно активировать предмет')
        elif json_data['response']['error'] == 16: # Нужно пройти обучение
            raise Exception('Невозможно перемещение, нужно пройти обучение вручную')
        elif json_data['response']['error'] == 17:
            pass
        elif json_data['response']['error'] == 20:
            pass
        elif json_data['response']['error'] == 21:
            pass
        elif json_data['response']['error'] == 23: # Access is prohibited by the effect
            raise Exception('Невозможно перемещение, мешает эффект')
        elif json_data['response']['error'] == 25: # Access is prohibited, the location is absent or the conditions for access to it are not fulfilled
            raise Exception('Невозможно перемещение, нет нужного покемона')
        elif json_data['response']['error'] == 76: # Access is prohibited, there is no cable rope
            raise Exception('Невозможно перемещение, нет канатной веревки')
        else:
            return json_data['response']['id'] == id_location
