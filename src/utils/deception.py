import base64
import time


class DeceptionManager:
    @staticmethod
    async def gen_t():
        timestamp = str(int(time.time() * 1000))[-7:]
        return str(base64.b64encode(timestamp.encode("UTF-8")))[2:-3][0:6]
