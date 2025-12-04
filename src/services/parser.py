from src.services.battle import MyTarget
from src.services.tasks import UsingPokeballs
from src.utils.decorators import BotDecorator


class ParseGameData:
    @staticmethod
    @BotDecorator.reformat_response
    async def team_grabber(json_data: dict, client: object) -> None:
        if len(client.team) == 0:
            for select in json_data['response']['pokemon_list']:
                pokemon = MyTarget(json_data['response']['pokemon_list'][select]['pok']['id'])

                for select_atk in json_data['response']['pokemon_list'][select]['pok']:
                    if 'atk_' in select_atk:
                        pokemon.add_atk(
                            data=[
                                json_data['response']['pokemon_list'][select]['pok'][select_atk]['category'],
                                json_data['response']['pokemon_list'][select]['pok'][select_atk]['id'],
                                json_data['response']['pokemon_list'][select]['pok'][select_atk]['name'],
                                int(json_data['response']['pokemon_list'][select]['pok'][select_atk]['pp'].split('/')[
                                        0]),
                                int(json_data['response']['pokemon_list'][select]['pok'][select_atk]['pp'].split('/')[
                                        1]),
                                json_data['response']['pokemon_list'][select]['pok'][select_atk]['type']
                            ]
                        )

                pokemon.add_info(
                    basenum2=json_data['response']['pokemon_list'][select]['pok']['basenum'],
                    gender=json_data['response']['pokemon_list'][select]['pok']['gender'],
                    hp=json_data['response']['pokemon_list'][select]['pok']['hp'],
                    maxHp=json_data['response']['pokemon_list'][select]['pok']['stat'][0],
                    lvl=json_data['response']['pokemon_list'][select]['pok']['lvl'],
                    name=json_data['response']['pokemon_list'][select]['pok']['name'],
                    sparka=json_data['response']['pokemon_list'][select]['pok']['sparka'],
                    sparka_number=json_data['response']['pokemon_list'][select]['pok']['sparkaNumber'],
                    type_text_color=json_data['response']['pokemon_list'][select]['pok']['type_text_color'],
                    item_id=json_data['response']['pokemon_list'][select]['pok']['item_id'],
                    start=json_data['response']['pokemon_list'][select]['pok']['start'],
                    nowOnBattle=False,
                    catched_Now=False
                )

                client.team.append(pokemon)

                client.logger.debug(
                    f"Pokemon: #{pokemon.basenum2} {pokemon.name} "
                    f"| Lvl: {pokemon.lvl} | HP: {pokemon.hp} "
                    f"| Gender: {pokemon.gender} | Active: {pokemon.start == '1'}"
                )
        else:
            await ParseGameData.update_team_id(json_data, client)

    @staticmethod
    @BotDecorator.reformat_response
    async def update_team_id(json_data: dict, client: object) -> None:
        server_id = []
        for pokemon in json_data['response']['pokemon_list']:
            server_id.append(json_data['response']['pokemon_list'][pokemon]['pok']['id'])

        team_ids = []
        for pokemon in client.team:
            team_ids.append(pokemon.id)

        for sid in server_id:
            if sid not in team_ids:
                for pokemon in client.team:
                    if pokemon.id not in server_id:
                        pokemon.update_pokemon_id(sid)
                        break

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
        client.logger.debug(f'Current value of completed battles - {client.tasks.currentFights}')

    @staticmethod
    @BotDecorator.reformat_response
    async def geo_position(json_data: dict, client: object) -> None:
        data_location = json_data['response']['location']
        name, id = data_location['name'], data_location['id_loc']
        region, roads = data_location['region'], data_location['roads']

        client.position.add_info(name, id, region, roads)

        client.logger.debug(f'Location data collected | '
                            f'Location name: {name} | '
                            f'ID: {id} | '
                            f'Region: {region} | '
                            f'Available routes: {roads}')

    @staticmethod
    async def update_enemy(json_data: dict, client: object) -> None:
        client.enemy.add_info(
            id=json_data['battleInfo']['id'],
            basenum2=json_data['battleInfo']['enemyTarget']['basenum2'],
            name=json_data['battleInfo']['enemyTarget']['name'],
            hp=json_data['battleInfo']['enemyTarget']['hp'],
            maxHp=json_data['battleInfo']['enemyTarget']['hp_max'],
            lvl=json_data['battleInfo']['enemyTarget']['lvl'],
            sex2=json_data['battleInfo']['enemyTarget']['sex2'],
            type_text_color=json_data['battleInfo']['enemyTarget']['type_text_color'],
            catch=json_data['battleInfo']['enemy']['catch']
        )

    @staticmethod
    async def update_ally(json_data: dict, client: object) -> None:
        for pokemon in client.team:
            if int(pokemon.id) == json_data['battleInfo']['myTarget']['id']:
                pokemon.update_pokemon_data(
                    hp=json_data['battleInfo']['myTarget']['hp'],
                    nowOnBattle=True,
                )
            else:
                pokemon.update_pokemon_data(
                    hp=pokemon.hp,
                    nowOnBattle=False,
                )

        client.enemy.update_pokemon_data(json_data['battleInfo']['enemyTarget']['hp'])
