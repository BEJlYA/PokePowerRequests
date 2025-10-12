import asyncio

from src.config.settings import Settings
from src.core.client import AiohttpClient
from src.core.models import ResponseChecker


async def main():
    settings = Settings(login='LOGIN', password='PASSWORD')

    async with AiohttpClient(settings) as aclient:
        await aclient.auth(settings)
        await aclient.websocket_sid()

        response = await aclient.init()

        await aclient.pokemons()
        await aclient.items()
        await aclient.get_edit()

        await ResponseChecker.main_handler(response, aclient)

        await aclient.tasks.check_tasks(aclient)

        await aclient.update()


if __name__ in '__main__':
    asyncio.run(main())
