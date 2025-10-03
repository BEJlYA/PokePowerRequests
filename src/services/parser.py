from src.services.battle import MyTarget
from src.services.tasks import UsingPokeballs
from src.utils.decorators import BotDecorator


class ParseGameData:
    @staticmethod
    @BotDecorator.reformat_response
    async def team_grabber(json_data: dict, client: object) -> None:
        for select in json_data['response']['pokemon_list']:
            element = MyTarget(json_data['response']['pokemon_list'][select]['pok']['id'])

            for select_atk in json_data['response']['pokemon_list'][select]['pok']:
                if 'atk_' in select_atk:
                    element.add_atk(
                        data=[
                            json_data['response']['pokemon_list'][select]['pok'][select_atk]['category'],
                            json_data['response']['pokemon_list'][select]['pok'][select_atk]['id'],
                            json_data['response']['pokemon_list'][select]['pok'][select_atk]['name'],
                            int(json_data['response']['pokemon_list'][select]['pok'][select_atk]['pp'].split('/')[0]),
                            int(json_data['response']['pokemon_list'][select]['pok'][select_atk]['pp'].split('/')[1]),
                            json_data['response']['pokemon_list'][select]['pok'][select_atk]['type']
                        ]
                    )

            element.add_info(
                basenum2=json_data['response']['pokemon_list'][select]['pok']['basenum'],
                gender=json_data['response']['pokemon_list'][select]['pok']['gender'],
                hp=json_data['response']['pokemon_list'][select]['pok']['hp'],
                lvl=json_data['response']['pokemon_list'][select]['pok']['lvl'],
                name=json_data['response']['pokemon_list'][select]['pok']['name'],
                sparka=json_data['response']['pokemon_list'][select]['pok']['sparka'],
                sparka_number=json_data['response']['pokemon_list'][select]['pok']['sparkaNumber'],
                start=json_data['response']['pokemon_list'][select]['pok']['start'],
                type_text_color=json_data['response']['pokemon_list'][select]['pok']['type_text_color'],
            )

            client.team.append(element)

    @staticmethod
    @BotDecorator.reformat_response
    async def pokeballs_grabber(json_data: dict) -> list:
        pokeballs = []

        for select in json_data['ballList']:
            if select['type'] == 1:
                raw_count = select.get('count', '').strip('x')
                clear_count = int(raw_count) if raw_count.isdigit() else 1

                element = UsingPokeballs()
                element.add_item(
                    name=select['name'],
                    id=select['id'],
                    count=clear_count
                )
                pokeballs.append(element)
        return pokeballs

    @staticmethod
    @BotDecorator.reformat_response
    async def battle_settings(json_data: dict, client: object) -> None:
        client.tasks.currentFights = int(json_data['response']['pok_limit'])

    @staticmethod
    @BotDecorator.reformat_response
    async def geo_position(json_data: dict, client: object) -> None:
        data_location = json_data['response']['location']
        name, id = data_location['name'], data_location['id_loc']
        region, roads = data_location['region'], data_location['roads']

        client.position.add_info(name, id, region, roads)

    @staticmethod
    async def update_enemy(json_data: dict, client: object) -> None:
        client.enemy.add_info(
            id=json_data['battleInfo']['id'],
            basenum2=json_data['battleInfo']['enemyTarget']['basenum2'],
            name=json_data['battleInfo']['enemyTarget']['name'],
            hp=json_data['battleInfo']['enemyTarget']['hp'],
            lvl=json_data['battleInfo']['enemyTarget']['lvl'],
            sex2=json_data['battleInfo']['enemyTarget']['sex2'],
            type_text_color=json_data['battleInfo']['enemyTarget']['type_text_color'],
            catch=json_data['battleInfo']['enemy']['catch']
        )
