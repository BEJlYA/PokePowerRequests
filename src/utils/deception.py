import base64
import platform
import random
import time
from typing import Dict


class DeceptionManager:
    @staticmethod
    async def gen_t():
        timestamp = str(int(time.time() * 1000))[-7:]
        return str(base64.b64encode(timestamp.encode("UTF-8")))[2:-3][0:6]

    @staticmethod
    def random_headers() -> Dict[str, str]:
        desktop_user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
        ]
        mobile_user_agents = [
            'Mozilla/5.0 (Linux; Android 14; SM-S911B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.210 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.210 Mobile Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1'
        ]

        desktop_sec_ch_ua = [
            '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
            '"Chromium";v="139", "Not=A?Brand";v="24", "Google Chrome";v="139"',
            '"Chromium";v="138", "Not=A?Brand";v="24", "Google Chrome";v="138"'
        ]
        mobile_sec_ch_ua = [
            '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            '"Not_A Brand";v="8", "Chromium";v="120", "Apple Safari";v="120"'
        ]

        system = platform.system().lower()

        if system == 'linux':
            user_agent = random.choice(mobile_user_agents)
            sec_ch_ua_mobile = 1
            if 'iPhone' in user_agent:
                sec_ch_ua = mobile_sec_ch_ua[1]
                device = 'iOS'
            else:
                sec_ch_ua = mobile_sec_ch_ua[0]
                device = 'Android'
        else:
            user_agent = random.choice(random.choice(desktop_user_agents))
            sec_ch_ua = random.choice(random.choice(desktop_sec_ch_ua))
            device = 'Windows'
            sec_ch_ua_mobile = 0

        return {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'ru,en;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Dnt': '1',
            'Origin': 'https://pokepower.ru',
            'Referer': 'https://pokepower.ru/world',
            'Sec-Ch-Ua': sec_ch_ua,
            'Sec-Ch-Ua-Mobile': f'?{sec_ch_ua_mobile}',
            'Sec-Ch-Ua-Platform': f'"{device}"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': user_agent,
            'X-Requested-With': 'XMLHttpRequest'
        }

    @staticmethod
    def replace_headers(headers: Dict[str, str]) -> Dict[str, str]:
        auth_headers = headers.copy()
        auth_headers['Referer'] = 'https://pokepower.ru/'
        return auth_headers
