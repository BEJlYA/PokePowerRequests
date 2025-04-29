import base64
import json
import time
from functools import wraps

from dataclasses import MyTarget, EnemyTarget, UsingPokeballs


class ResponseChecker:
    @staticmethod
    async def status_authentication(response):
        json_data = json.loads(await response.text())
        if json_data['error'] == 1:
            raise Exception(json_data['text']) # Слинковать с гуи для вывода алерта о неудачной аунтефикации

    @staticmethod
    def reformat_response(func):
        @wraps(func)
        async def wrapper(response, *args, **kwargs):
            try:
                text_response = await response.text()
                start_index = text_response.find('{')
                end_index = text_response.rfind('}')
                json_str = text_response[start_index:end_index + 1]
                json_data = json.loads(json_str)

                return await func(json_data, *args, **kwargs)
            except Exception as e:
                print(e)
                raise

        return wrapper

    @staticmethod
    @reformat_response
    async def team_grabber(json_data):
        team = []

        for select in json_data['response']['pokemon_list']:
            element = MyTarget(json_data['response']['pokemon_list'][select]['pok']['id'])

            for select_atk in json_data['response']['pokemon_list'][select]['pok']:
                if 'atk_' in select_atk:
                    element.add_atk(
                        data=[
                            json_data['response']['pokemon_list'][select]['pok'][select_atk]['category'],
                            json_data['response']['pokemon_list'][select]['pok'][select_atk]['id'],
                            json_data['response']['pokemon_list'][select]['pok'][select_atk]['name'],
                            json_data['response']['pokemon_list'][select]['pok'][select_atk]['pp'].split('/')[0],
                            json_data['response']['pokemon_list'][select]['pok'][select_atk]['pp'].split('/')[1],
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

            team.append(element)
        return team

    @staticmethod
    @reformat_response
    async def pokeballs_grabber(json_data):
        pokeballs = []

        for select in json_data['ballList']:
            if select['type'] == 1:
                element = UsingPokeballs()
                element.add_item(
                    name=select['name'],
                    id=select['id'],
                    count=int(select['count'].strip('x')) + 1,
                )
                pokeballs.append(element)
        return pokeballs

    @staticmethod
    @reformat_response
    async def geo_position(json_data, client):
        # Search geo-position
        try:
            if json_data['response'].get('location'):
                data_location = json_data['response'].get('location')
                name, id = data_location.get('name'), data_location.get('id_loc')
                region, roads = data_location.get('region'), data_location.get('roads')

                client.position.add_info(name, id, region, roads)
        except json.JSONDecodeError:
            raise Exception('Ошибка при парсинге JSON.')
        except KeyError:
            pass

    @staticmethod
    @reformat_response
    async def main_handler(json_data, client):
        # Battle finder
        if json_data.get('battleInfo') and not json_data.get('logDrop'):
            target = EnemyTarget()
            target.add_info(
                basenum2=json_data['battleInfo']['enemyTarget']['basenum2'],
                name=json_data['battleInfo']['enemyTarget']['name'],
                hp=json_data['battleInfo']['enemyTarget']['hp'],
                lvl=json_data['battleInfo']['enemyTarget']['lvl'],
                sex2=json_data['battleInfo']['enemyTarget']['sex2'],
                type_text_color=json_data['battleInfo']['enemyTarget']['type_text_color'],
                catch=json_data['battleInfo']['enemy']['catch']
            )
            client.enemy = target

            if (
                    client.enemy.basenum2 in client.data.rarePokemons[0] or
                    client.enemy.name in client.data.rarePokemons[0] and
                    client.enemy.catch == 1
            ):
                for key in sorted(client.data.priorityPokeballs, key=client.data.priorityPokeballs.get): # Super rare Pokémon catch
                    for ball in client.pokeballs:
                        if key in ball.name:
                            await client.catch(ball.id)
                            return # Написать обработку ситуации когда нашего покемона ранят или убивают и нужно идти лечиться или менять его на другого
            elif (
                    client.enemy.type_text_color == 1 and
                    client.settings.catchShine == 1 and
                    client.enemy.catch == 1
            ):
                for key in sorted(client.data.priorityPokeballs, key=client.data.priorityPokeballs.get): # Shine catch
                    for ball in client.pokeballs:
                        if key in ball.id:
                            await client.catch(ball.id)
                            return  # Написать обработку ситуации когда нашего покемона ранят или убивают и нужно идти лечиться или менять его на другого
            elif (
                    client.settings.targetPokemons and
                    any(
                        (
                                client.enemy.basenum2 in target or
                                client.enemy.name in target
                        )
                        for target in client.settings.targetPokemons
                        if isinstance(target, list) and len(target) >= 2
                    ) and (
                            client.enemy.sex2 == client.settings.catchGender or
                            client.settings.catchGender is None
                    ) and
                    client.enemy.catch == 1
            ):
                await client.catch(client.settings.catchTools)
            else:
                enemy_types = None
                for pokemon in client.data.pokedex:
                    if client.enemy.basenum2 == pokemon['basenum'] or client.enemy.name == pokemon['name']:
                        enemy_types = pokemon['types']
                        break

                atks_types = []
                for myPokemon in client.team:
                    if myPokemon.start == '1':
                        for attack in myPokemon.atks:
                            if (attack[0] == 1 or attack[0] == 2) and int(attack[3]) > 0:
                                atks_types.append(attack[5])

                max_effectiveness = {}
                if len(enemy_types) == 2:
                    for a in atks_types:
                        for i in enemy_types:
                            e = client.data.punchEffectiveness.get(a, {}).get(i, 1)
                            if a in max_effectiveness:
                                max_effectiveness[a] = (i, e * (max_effectiveness[a][1]))
                            else:
                                max_effectiveness[a] = (i, e)
                else:
                    for a in atks_types:
                        for i in enemy_types:
                            e = client.data.punchEffectiveness.get(a, {}).get(i, 1)
                            if a in max_effectiveness:
                                if e > max_effectiveness[a][1]:
                                    max_effectiveness[a] = (i, e)
                            else:
                                max_effectiveness[a] = (i, e)
                max_type = max(max_effectiveness.items(), key=lambda x: x[1][1])

                for myPokemon in client.team:
                    if myPokemon.start == '1':
                        for attack in myPokemon.atks:
                            if (
                                    attack[0] == 1 or attack[0] == 2 and
                                    int(attack[3]) > 0 and
                                    attack[5] == max_type[0]
                            ):
                                print('attack send!')
                                await client.attack(attack[1])
                                myPokemon.reduce_count_attack(attack[1])
                                break

        elif 'logDrop' in json_data:
            client.enemy = None

            await ResponseChecker.pokemon_health(json_data['battleInfo'], client)
            client.settings.check_drop(client, json_data['logDrop'])


    @staticmethod
    async def pokemon_health(battle_info, client):
        if int(battle_info['myTarget']['hp']) <= int(battle_info['myTarget']['hp_max']) * 0.3:
            print('low pokemon hp!')

class UniqueGenerator:
    @staticmethod
    async def gen_t():
        timestamp = str(int(time.time() * 1000))[-7:]
        return str(base64.b64encode(timestamp.encode("UTF-8")))[2:-3][0:6]