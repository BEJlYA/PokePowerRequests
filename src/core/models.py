from src.services.movements import MovementsController
from src.services.parser import ParseGameData
from src.utils.decorators import BotDecorator


class ResponseChecker:
    @staticmethod
    @BotDecorator.reformat_response
    async def main_handler(json_data: dict, client: object) -> None:
        if json_data.get('battleInfo') and not json_data.get('logDrop'):
            await ParseGameData.update_enemy(json_data, client)

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
                for key in sorted(
                        client.data.priorityPokeballs,
                        key=client.data.priorityPokeballs.get
                ):
                    for ball in client.pokeballs:
                        if key in ball.name:
                            await client.catch(ball.id)
                            return

            elif (
                    client.enemy.type_text_color == 1 and
                    client.tasks.catchShine and
                    client.enemy.catch == 1
            ):  # Catch shine pokémon
                for key in sorted(
                        client.data.priorityPokeballs,
                        key=client.data.priorityPokeballs.get
                ):
                    for ball in client.pokeballs:
                        if key in ball.name:
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
                await client.enemy.calculate_attack(client)

        elif 'logDrop' in json_data:
            await client.tasks.check_drop(client, json_data['logDrop'])
            await MovementsController.pokemon_health(json_data, client)
