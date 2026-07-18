from src.config.manager import config
from src.core.exeptions import BotShutdown
from src.services.battle import MyTarget
from src.services.navigator import DataLocation


class TaskManager:
    def __init__(self):
        # Current number of battles, automatic definition
        self.currentFights = 0
        # Maximum number of battles - 1500
        self.maxFights = 1500
        # Flag for catching shiny Pokémon, by default - TRUE
        self.catchShiny = config.catch_shiny
        # Items for drop [...{'name': '', 'count': ''}...]
        self.targetItems = sorted(self._normalize_items(config.target_items), key=lambda item: int(item.get('count', 0)))
        # List catchable Pokémon [...{'num': '', 'name': '', 'gender': 'venus/mars/genderless/any', 'count': ''}...]
        self.targetPokemons = sorted(self._normalize_pokemon(config.target_pokemons), key=lambda poke: int(poke.get('count', '0')))
        # FALSE - disconnect of tasks
        self.hadTasks = bool(config.target_items or config.target_pokemons)
        # TRUE - don't change pokémon in battle
        self.notChangeHero = config.not_change_hero

    @staticmethod
    def _normalize_pokemon(pokemons: list[dict]) -> list[dict]:
        gender_map = {
            "Б": "genderless",
            "М": "mars",
            "Ж": "venus",
            "Л": "any"
        }

        for pokemon in pokemons:
            pokemon['gender'] = gender_map.get(pokemon.get('gender', 'Л'), 'any')
            pokemon['count'] = str(pokemon.get('count', 0))

        return pokemons

    @staticmethod
    def _normalize_items(items: list[dict]) -> list[dict]:
        for item in items:
            item['count'] = str(item['count'])

        return items

    def priority_task(self) -> dict | None:
        if not self.hadTasks:
            return None
        elif self.targetPokemons:
            return self.targetPokemons[0]
        elif self.targetItems:
            return self.targetItems[0]
        return None

    async def check_drop(self, client: object, log: list[dict]) -> None:
        for part in log:
            obj_type = part.get('object')

            if obj_type == 'item':
                name = part['name']

                count_str = part.get('count', 'x1').strip('x')
                count = int(count_str) if count_str else 1

                client.logger.inventory_change(
                    name=name,
                    count=count,
                )

                for item in client.tasks.targetItems:
                    if item.get('name') == name:
                        item['count'] = max(int(item.get('count')) - count, 0)

                        config.decrease_item_count(name=name, amount=count)

                        client.logger.task_progress(
                            task_type='ITEM',
                            name_task=item.get('name'),
                            remainder=item.get('count'),
                        )

            elif obj_type == 'pokemon':
                pokemon = MyTarget(client.enemy.id)
                pokemon.add_info(
                    basenum2=client.enemy.basenum2,
                    gender=client.enemy.sex2,
                    hp=client.enemy.hp,
                    maxHp=client.enemy.maxHp,
                    lvl=client.enemy.lvl,
                    name=client.enemy.name,
                    sparka='',
                    sparka_number=0,
                    type_text_color=client.enemy.type_text_color,
                    item_id='0',
                    start=0,
                    nowOnBattle=False,
                    catched_Now=True
                )
                client.team.append(pokemon)

                client.logger.team_action(
                    action_type="ADD",
                    description=f"Pokemon caught: #{pokemon.basenum2} {pokemon.name}"
                )


                for poke in client.tasks.targetPokemons:
                    if poke.get('gender') == 'any' and (poke.get('name') == pokemon.name or poke.get('num') == pokemon.basenum2):
                        poke['count'] = max(int(poke.get('count')) - 1, 0)

                        config.decrease_pokemon_count(num=pokemon.basenum2, name=pokemon.name, gender="Л")
                    elif poke.get('gender') == client.enemy.sex2 and (poke.get('name') == pokemon.name or poke.get('num') == pokemon.basenum2):
                        gender_map = {
                            "genderless": "Б",
                            "mars": "М",
                            "venus": "Ж"
                        }

                        poke['count'] = max(int(poke.get('count')) - 1, 0)

                        config.decrease_pokemon_count(num=pokemon.basenum2, name=pokemon.name, gender=gender_map.get(poke.get('gender')))
                    else:
                        continue

                    client.logger.task_progress(
                        task_type='POKEMON',
                        name_task=f"{poke.get('num')} {poke.get('name')}",
                        remainder=poke.get('count'),
                        gender=poke.get('gender'),
                    )

        client.tasks.targetItems = [item for item in client.tasks.targetItems if int(item.get('count')) > 0]
        client.tasks.targetPokemons = [poke for poke in client.tasks.targetPokemons if int(poke.get('count')) > 0]

        self.currentFights += 1

        await self.check_tasks(client)

    async def check_tasks(self, client: object) -> Exception | None:
        if self.currentFights >= self.maxFights:
            raise BotShutdown(message='Исполнено максимально возможное количество боёв за сутки')

        elif self.hadTasks and not self.targetItems and not self.targetPokemons:
            raise BotShutdown(message='Выполнены все условия поставленных задач!')

        elif self.hadTasks and self.targetItems or self.targetPokemons:
            next_task = self.priority_task()

            if next_task:
                task_name = next_task.get('name') or next_task.get('num')

                if task_name:
                    target_location_names = DataLocation.find_specific_loc(task_name, client.route_map)

                    if target_location_names:
                        path = DataLocation.find_shortest_named_path(
                            id_from=client.position.id,
                            name_to=target_location_names,
                            locations=client.route_map
                        )

                        if path:
                            final_location_id = path[-1] if path else None
                            final_location_name = None

                            for loc in client.route_map:
                                if loc.id == final_location_id:
                                    final_location_name = loc.name
                                    break

                            client.assault = 'false'

                            for step in path:
                                result = await client.route(step, final_location_name)

                                if not result:
                                    break

                            client.assault = 'true'


class UsingPokeballs:
    def __init__(self):
        self.name = None  # Name of pokeball
        self.id = None  # ID pokeball
        self.count = None  # Count of pokeballs

    def add_item(self, name: str, id: int, count: int) -> None:
        self.name = name
        self.id = id
        self.count = count

    def reduce_count_pokeball(self):
        self.count = self.count - 1
