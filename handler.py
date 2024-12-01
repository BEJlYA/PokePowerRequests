import json
from dataclasses import MyTarget, EnemyTarget, UsingPokeballs


class ResponseChecker:
    @staticmethod
    async def status_authentication(response):
        json_data = json.loads(await response.text())
        if json_data['error'] == 1:
            print(json_data['text']) # Слинковать с гуи для вывода алерта

    @staticmethod
    async def team_grabber(response):
        team = []
        json_data = json.loads(await response.text())

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
    async def pokeballs_grabber(response):
        pokeballs = []
        json_data = json.loads(await response.text())

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
    async def main_response(client, response):
        text_response = await response.text()
        if not text_response.strip():
            raise 'Ошибка: сервер разорвал соединение.' # Может написать кастомные экзепшены, для выводов алертов по типу обновы/разрыва/некорректного логина/пароля?

        json_data = json.loads(await response.text())
        if (
                'battleInfo' in json_data and
                'logBattle' not in json_data
        ):
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
                for key in sorted(client.data.priorityPokeballs, key=client.data.priorityPokeballs.get): # Rare catch
                    for ball in client.pokeballs:
                        if key in ball.id:
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
                # алгоритм нахождения наиболее эффективной атаки, дальше отправка запроса.
                print('skip')
                # await client.attack()
        elif 'logBattle' in json_data:
            print('Battle end')
