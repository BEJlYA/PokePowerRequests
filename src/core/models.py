from src.services.battle import MyTarget
from src.services.navigations import DataLocation
from src.services.tasks import UsingPokeballs
from src.utils.decorators import BotDecorator


class ResponseChecker:
    @staticmethod
    @BotDecorator.reformat_response
    async def status_authentication(json_data: dict) -> None:
        if json_data['error'] == 1:
            raise Exception(json_data['text'])

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
    async def geo_position(json_data: dict, client: object) -> None:
        data_location = json_data['response']['location']
        name, id = data_location['name'], data_location['id_loc']
        region, roads = data_location['region'], data_location['roads']

        client.position.add_info(name, id, region, roads)

    @staticmethod
    @BotDecorator.reformat_response
    async def battle_settings(json_data: dict, client: object) -> None:
        client.tasks.currentFights = int(json_data['response']['pok_limit'])

    @staticmethod
    @BotDecorator.reformat_response
    async def main_handler(json_data: dict, client: object) -> None:
        # Battle finder
        if json_data.get('battleInfo') and not json_data.get('logDrop'):
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

            client.logger.battle_start(
                enemy_num=client.enemy.basenum2,
                enemy_name=client.enemy.name,
                enemy_level=client.enemy.lvl,
                enemy_shine=client.enemy.type_text_color
            )

            if (
                    client.enemy.basenum2 in client.data.rarePokemons[0] or
                    client.enemy.name in client.data.rarePokemons[0] and
                    client.enemy.catch == 1
            ):  # Catch rare pokémon
                for key in sorted(client.data.priorityPokeballs,
                                  key=client.data.priorityPokeballs.get):  # Super rare Pokémon catch
                    for ball in client.pokeballs:
                        if key in ball.name:
                            await client.catch(ball.id)
                            return
            elif (
                    client.enemy.type_text_color == 1 and
                    client.tasks.catchShine and
                    client.enemy.catch == 1
            ):  # Catch shine pokémon
                for key in sorted(client.data.priorityPokeballs, key=client.data.priorityPokeballs.get):  # Shine catch
                    for ball in client.pokeballs:
                        if key in ball.id:
                            await client.catch(ball.id)
                            return
            elif (
                    client.tasks.targetPokemons and
                    client.enemy.catch == 1 and
                    any(
                        (
                                client.enemy.basenum2 == targetPokemon.get('num') or
                                client.enemy.name == targetPokemon.get('name')
                        ) and (
                                client.enemy.sex2 == targetPokemon.get('gender') or
                                targetPokemon.get('gender') == 'any'
                        )
                        for targetPokemon in client.tasks.targetPokemons
                        if isinstance(targetPokemon, dict)
                    )
            ):  # Catch certain pokémon
                await client.catch(client.tasks.catchTools)
            else:  # Else kill pokémon
                enemy_types = client.data.find_pokemon_types(
                    basenum=client.enemy.basenum2,
                    name=client.enemy.name
                )

                atks_types = []

                active_pokemon = next((p for p in client.team if p.start == '1'),
                                      client.team[0] if client.team else None)

                if active_pokemon:
                    for attack in active_pokemon.atks:
                        if attack[0] in (1, 2) and attack[3] > 0:
                            atks_types.append(attack[5])

                max_effectiveness = {}
                for a in atks_types:
                    for i in enemy_types:
                        e = client.data.punchEffectiveness.get(a, {}).get(i, 1)

                        if a in max_effectiveness:
                            if len(enemy_types) == 2:
                                max_effectiveness[a] = (i, e * (max_effectiveness[a][1]))
                            else:
                                max_effectiveness[a] = (i, e)
                        else:
                            max_effectiveness[a] = (i, e)

                if max_effectiveness:
                    max_type = max(max_effectiveness.items(), key=lambda x: x[1][1])

                    if active_pokemon:
                        for attack in active_pokemon.atks:
                            if (
                                    attack[0] in (1, 2) and
                                    attack[3] > 0 and
                                    attack[5] == max_type[0]
                            ):
                                active_pokemon.reduce_count_attack(attack[1])
                                await client.attack(attack)
                                break
                else:
                    await client.coward()


        elif 'logDrop' in json_data:
            await client.tasks.check_drop(client, json_data['logDrop'])
            await ResponseChecker.pokemon_health(json_data, client)

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
