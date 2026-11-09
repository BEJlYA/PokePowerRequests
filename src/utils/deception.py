from typing import Dict

from uaforge.core.generator import UserAgentGenerator


class DeceptionManager:
    def __init__(self, settings: object):
        self.agent = UserAgentGenerator(seed=settings.login)

    def random_headers(self) -> Dict[str, str]:
        identity = self.agent.generate()

        headers = identity.get_headers()

        base_headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'ru,en;q=0.9',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'DNT': '1',
            'Origin': 'https://pokepower.ru',
            'Referer': 'https://pokepower.ru/world',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'X-Requested-With': 'XMLHttpRequest'
        }

        base_headers.update(headers)

        return base_headers

    @staticmethod
    def replace_headers(headers: Dict[str, str]) -> Dict[str, str]:
        auth_headers = headers.copy()
        auth_headers['Referer'] = 'https://pokepower.ru/'
        return auth_headers
