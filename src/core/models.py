from src.services.movements import MovementsController
from src.services.parser import ParseGameData
from src.utils.decorators import BotDecorator


class ResponseChecker:
    @staticmethod
    @BotDecorator.reformat_response
    async def main_handler(json_data: dict, client: object) -> None:
        if json_data.get('battleInfo') and not json_data.get('logDrop'):
            await ParseGameData.update_enemy(json_data, client)

            if not json_data.get('battleInfo').get('log'):
                client.logger.battle_start(
                    enemy_num=client.enemy.basenum2,
                    enemy_name=client.enemy.name,
                    enemy_level=client.enemy.lvl,
                    enemy_shiny=client.enemy.type_text_color
                )

            await ParseGameData.update_ally(json_data, client)

            for injured in client.team:
                if injured.nowOnBattle and injured.need_heal() and client.tasks.notChangeHero:
                    injured.start = 0
                    for pokemon in client.team:
                        if not pokemon.need_heal() and not pokemon.item_id == '10002':
                            await client.change(pokemon=pokemon)
                            await client.start(pokemon=pokemon)
                            pokemon.start = 1
                            return

            if (
                    len(client.team) < 6 and
                    (client.enemy.basenum2 in client.data.rarePokemons[0] or
                     client.enemy.name in client.data.rarePokemons[1]) and
                    client.enemy.catch == 1
            ):  # Catch rare pokémon
                if not json_data.get('battleInfo').get('log'):
                    client.logger.info(message='Rare pokemon detected...')
                for key in sorted(
                        client.data.specialPriorityPokeballs,
                        key=client.data.specialPriorityPokeballs.get
                ):
                    for ball in client.pokeballs:
                        if key in ball.name:
                            await client.catch(ball.id)
                            return

            elif (
                    len(client.team) < 6 and
                    client.enemy.type_text_color == 1 and
                    client.tasks.catchShiny and
                    client.enemy.catch == 1
            ):  # Catch shiny pokémon
                if not json_data.get('battleInfo').get('log'):
                    client.logger.info(message='Shiny pokemon detected...')
                for key in sorted(
                        client.data.specialPriorityPokeballs,
                        key=client.data.specialPriorityPokeballs.get
                ):
                    for ball in client.pokeballs:
                        if key in ball.name:
                            await client.catch(ball.id)
                            return

            elif (
                    len(client.team) < 6 and
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
                if not json_data.get('battleInfo').get('log'):
                    client.logger.info(message='Pokemon from task detected...')
                for key in sorted(
                        client.data.priorityPokeballs,
                        key=client.data.priorityPokeballs.get
                ):
                    for ball in client.pokeballs:
                        if key in ball.name:
                            await client.catch(ball.id)
                            return

            else:  # Else kill pokémon
                await client.enemy.calculate_attack(client)

        elif 'response' in json_data and json_data.get('response').get('f') == 1:  # Detect missed battle
            client.logger.info(message='Missed battle discovered...')
            response = await client.init()
            await ResponseChecker.main_handler(response, client)

        elif 'logDrop' in json_data:  # Process results of battle
            await client.tasks.check_drop(client, json_data['logDrop'])
            await MovementsController.pokemon_health(client)
