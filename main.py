import asyncio
from client import AiohttpClient
from dataclasses import Settings

async def main():
    settings = Settings(login='LOGIN', password='PASSWORD')
    try:
        async with AiohttpClient(settings) as aclient:
            await aclient.auth(settings)
            await aclient.pokemons()
            await aclient.items()
            await aclient.init()

            await asyncio.create_task(await aclient.update())
    except asyncio.CancelledError:
        pass
    except KeyboardInterrupt:
        pass
    finally:
        pass

if __name__ in '__main__':
    asyncio.run(main())