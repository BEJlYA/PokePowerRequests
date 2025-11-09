import asyncio
import json
import traceback
from functools import wraps

import aiohttp

from src.utils.exeptions import BotShutdown, BotShutdownError


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
            max_retries = 5

            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)

                except aiohttp.ServerDisconnectedError as e:
                    if client:
                        delay = min(30, 2 ** attempt)
                        client.logger.warning(message=
                                              f"{e} in {func.__name__}, "
                                              f"attempt {attempt + 1}/{max_retries}, wait {delay}sec"
                                              )
                        await asyncio.sleep(delay)

                    if attempt == max_retries - 1:
                        client.logger.error(
                            message=f"Server unavailable after {max_retries} attempts at {func.__name__}")
                        raise

                except (aiohttp.ClientOSError,
                        aiohttp.ClientConnectorError,
                        aiohttp.ServerTimeoutError,
                        asyncio.TimeoutError) as e:
                    if "103" in str(e) or "1236" in str(e):
                        client.logger.warning(message='The system disconnected network...')
                        await asyncio.sleep(30)

                        continue
                    else:
                        client.logger.warning(message=f"Internet connection error...")
                        while True:
                            await asyncio.sleep(5)
                            try:
                                async with aiohttp.ClientSession() as session:
                                    async with session.get(
                                            url="https://google.com",
                                            timeout=30
                                    ) as response:
                                        if response.status == 200:
                                            client.logger.warning(
                                                message="Internet has been restored, let's continue...",
                                                exc=func.__name__)
                                            break
                            except:
                                client.logger.warning(message="Internet is not available yet, we are waiting...")
                                continue

                        continue

                except (aiohttp.ClientResponseError,
                        json.JSONDecodeError,
                        KeyError,
                        BotShutdownError) as e:
                    frame = traceback.extract_tb(e.__traceback__)[-1]
                    client.logger.error(f"{type(e).__name__} in {frame.name}:{frame.lineno} - {e}")
                    raise

                except BotShutdown:
                    raise

                except Exception as e:
                    frame = traceback.extract_tb(e.__traceback__)[-1]
                    client.logger.error(
                        message=f"Error in {frame.name}: {frame.lineno}",
                        extra_data=f"{type(e).__name__}: {e}"
                    )
                    raise

            return None

        return wrapper
