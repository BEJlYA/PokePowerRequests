from src.config.manager import config
from src.core.exeptions import BotShutdown
from src.services.battle import MyTarget
from src.services.navigator import DataLocation
from src.services.tasks import tasks, Task, GENDER_MAP
from src.services.time_manager import TimeManager


class TaskManager:
    def __init__(self):
        # Current number of battles, automatic definition
        self.currentFights = 0
        # Maximum number of battles - 1500
        self.maxFights = 1500
        # Flag for catching shiny Pokémon, by default - TRUE
        self.catchShiny = config.catch_shiny
        # TRUE - don't change pokémon in battle
        self.notChangeHero = config.not_change_hero
        # Items for drop [...{'name': '', 'count': ''}...]

        tasks.clear()

        for entry in config.target_tasks:
            task = Task.from_dict(entry)
            if task.kind == "pokemon":
                task.gender = GENDER_MAP.get(task.gender, "any")
            tasks.add(task)
        self.hadTasks = bool(tasks)

    def _match_entry(self, task: Task, entry: dict) -> bool:
        if task.kind == "pokemon":
            entry_id = str(entry.get("id", "")).lstrip("0")
            entry_name = (entry.get("name") or "").lower()

            task_num = (task.num or "").lstrip("0")
            task_name = (task.name or "").lower()

            if task_num and entry_id == task_num:
                return True
            if task_name and entry_name == task_name:
                return True
            return False

        entry_name = (entry.get("name") or "").lower()
        task_name = (task.name or "").lower()
        return bool(task_name) and entry_name == task_name

    def _entry_timezones(self, entry: dict) -> list[int]:
        raw = entry.get("timezone", 0)

        if isinstance(raw, (list, tuple)):
            values = raw
        else:
            values = [raw]

        result: list[int] = []
        for v in values:
            try:
                result.append(int(v))
            except (TypeError, ValueError):
                continue

        return result or [0]

    def priority_task(self, client) -> Task | None:
        if not self.hadTasks or not tasks:
            return None

        active: list[tuple[int, Task]] = []
        always: list[tuple[int, Task]] = []

        for task in tasks:
            if task.count <= 0:
                continue

            has_active = False
            has_always = False

            for loc in client.route_map:
                collection = loc.habitat if task.kind == "pokemon" else loc.items
                if not collection:
                    continue

                for entry in collection:
                    if not self._match_entry(task, entry):
                        continue

                    for tz in self._entry_timezones(entry):
                        if tz == 0:
                            has_always = True
                        elif TimeManager.is_timezone_active(tz):
                            has_active = True
                            break

                    if has_active:
                        break

                if has_active:
                    break

            if has_active:
                active.append((task.count, task))
            elif has_always:
                always.append((task.count, task))

        if active:
            active.sort(key=lambda p: p[0])
            return active[0][1]

        if always:
            always.sort(key=lambda p: p[0])
            return always[0][1]

        return None

    async def check_drop(self, client, log):
        for part in log:
            obj_type = part.get('object')

            if obj_type == 'item':
                name = part['name']
                count_str = part.get('count', 'x1').strip('x')
                count = int(count_str) if count_str else 1

                client.logger.inventory_change(name=name, count=count)

                for task in tasks:
                    if task.kind != "item" or task.name != name:
                        continue
                    task.count = max(task.count - count, 0)
                    await config.decrease_task_count(task, amount=count)
                    client.logger.task_progress(
                        task_type='ITEM',
                        name_task=task.name,
                        remainder=task.count,
                    )
                    break

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
                    catched_Now=True,
                )
                client.team.append(pokemon)
                client.logger.team_action(
                    action_type="ADD",
                    description=f"Pokemon caught: #{pokemon.basenum2} {pokemon.name}",
                )

                for task in tasks:
                    if task.kind != "pokemon":
                        continue

                    matches_name = (
                            (task.name and task.name == pokemon.name)
                            or (task.num and task.num == str(pokemon.basenum2))
                    )
                    if not matches_name:
                        continue

                    matches_gender = (
                            task.gender == "any"
                            or GENDER_MAP.get(task.gender) == client.enemy.sex2
                    )
                    if not matches_gender:
                        continue

                    task.count = max(task.count - 1, 0)
                    await config.decrease_task_count(task, amount=1)
                    client.logger.task_progress(
                        task_type='POKEMON',
                        name_task=f"{task.num} {task.name}".strip(),
                        remainder=task.count,
                        gender=GENDER_MAP.get(task.gender, "any"),
                    )
                    break

        tasks.remove_completed()
        self.currentFights += 1
        await self.check_tasks(client)

    async def check_tasks(self, client) -> None:
        if self.currentFights >= self.maxFights:
            raise BotShutdown(message='Исполнено максимально возможное количество боёв за сутки')

        if self.hadTasks and not tasks:
            raise BotShutdown(message='Выполнены все условия поставленных задач!')

        if not self.hadTasks:
            return

        next_task = self.priority_task(client)
        if next_task is None:
            return

        task_name = next_task.search_name
        if not task_name:
            return

        target_location_names = DataLocation.find_specific_loc(task_name, client.route_map)
        if not target_location_names:
            return

        path = DataLocation.find_shortest_named_path(
            id_from=client.position.id,
            name_to=target_location_names,
            locations=client.route_map,
        )
        if not path:
            return

        final_location_id = path[-1]
        final_location_name = next(
            (loc.name for loc in client.route_map if loc.id == final_location_id),
            None,
        )

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
