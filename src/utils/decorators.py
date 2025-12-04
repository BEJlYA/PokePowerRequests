import asyncio
import json
import traceback
from functools import wraps

import aiohttp

from src.utils.exeptions import BotShutdown, BotShutdownError, BotNotify


class BotDecorator:
    @staticmethod
    def reformat_response(func):
        @wraps(func)
        async def wrapper(response, *args, **kwargs):
            if isinstance(response, dict):
                return await func(response, *args, **kwargs)

            elif hasattr(response, 'text'):
                text_response = await response.text()
                start_index = text_response.find('{')
                end_index = text_response.rfind('}')
                json_str = text_response[start_index:end_index + 1]
                json_data = json.loads(json_str)
                return await func(json_data, *args, **kwargs)

            else:
                raise ValueError(f"Unsupported input type: {type(response)}")

        return wrapper

    @staticmethod
    def safe_request(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            client = args[0] if args else None

            try:
                return await func(*args, **kwargs)

            except (aiohttp.ServerDisconnectedError,
                    aiohttp.ClientOSError,
                    aiohttp.ClientConnectorError,
                    aiohttp.ServerTimeoutError,
                    aiohttp.ClientConnectorDNSError,
                    asyncio.TimeoutError) as e:
                client.logger.warning(message=f"Waiting for internet restoration...")

                while True:
                    await asyncio.sleep(5)

                    try:
                        async with aiohttp.ClientSession() as session:
                            async with session.get(
                                    url="https://google.com"
                            ) as response:
                                if response.status == 200:
                                    client.logger.warning(message="Internet restored! Repeating request...")

                                    break
                    except:
                        client.logger.warning(message="Internet not available yet, waiting...")

                        continue

                return await func(*args, **kwargs)

            except BotNotify as e:
                client.logger.warning(
                    message=f'{e.message}')
                return await func(*args, **kwargs)

            except BotShutdownError as e:
                frame = traceback.extract_tb(e.__traceback__)[-1]
                client.logger.error(
                    message=f"Сlient crashed due to {frame.name}: {frame.lineno}",
                    extra_data=f"{type(e).__name__}: {e}"
                )
                raise

            except BotShutdown:
                raise

            except asyncio.exceptions.CancelledError:
                pass

            except Exception as e:
                frame = traceback.extract_tb(e.__traceback__)[-1]
                client.logger.error(
                    message=f"Critical error in {frame.name}: {frame.lineno}",
                    extra_data=f"{type(e).__name__}: {e}"
                )
                raise

        return wrapper
