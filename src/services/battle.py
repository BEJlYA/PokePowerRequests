class MyTarget:
    def __init__(self, id: str):
        self.atks = []  # List of attack [...[category damage, id, name, pp_count, max_pp, type]...]
        self.basenum2 = None  # Pokedex number
        self.gender = None  # Pokemon gender (venus/mars/genderless)
        self.hp = None  # Count of HP
        self.id = id  # Pokemon ID
        self.lvl = None  # Pokémon level
        self.name = None  # Pokemon name
        self.sparka = None  # Mating availability
        self.sparkaNumber = None  # Mating compatibility
        self.start = None  # Priority flag
        self.type_text_color = None  # 0/1 - (Dont) shine pokemon

    def add_info(
            self, basenum2: int, gender: str, hp: int, lvl: int,
            name: str, sparka: str, sparka_number: int, start: int, type_text_color: int
    ) -> None:
        self.basenum2 = basenum2
        self.gender = gender
        self.hp = hp
        self.lvl = lvl
        self.name = name
        self.sparka = sparka
        self.sparkaNumber = sparka_number
        self.start = start
        self.type_text_color = type_text_color

    def last_atk(self) -> int:
        sum_of_pp = 0

        for atk in self.atks:
            if atk[0] in (1, 2):
                sum_of_pp += atk[3]
        return sum_of_pp

    def add_atk(self, data: list) -> None:
        self.atks.append(data)

    def reduce_count_attack(self, attack_id: int) -> None:
        for attack in self.atks:
            if attack_id in attack[1]:
                attack[3] -= 1

    def restore_pp(self) -> None:
        for atk in self.atks:
            if not atk[3] == atk[4]:
                atk[3] += atk[4] - atk[3]


class EnemyTarget:
    def __init__(self):
        self.id = None
        self.basenum2 = None  # Pokedex number
        self.name = None  # Pokemon name
        self.hp = None  # Amount HP
        self.lvl = None  # Pokémon level
        self.sex2 = None  # Pokemon gender (venus/mars/genderless)
        self.type_text_color = None  # 0/1 - (Dont) shine pokemon
        self.catch = 1  # 1/0 - Can/Can't be caught

    def add_info(
            self, id: int, basenum2: int, name: str, hp: int, lvl: int,
            sex2: int, type_text_color: int, catch: int
    ) -> None:
        self.id = id
        self.basenum2 = basenum2
        self.name = name
        self.hp = hp
        self.lvl = lvl
        self.sex2 = sex2
        self.type_text_color = type_text_color
        self.catch = catch
