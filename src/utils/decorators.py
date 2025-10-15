import asyncio
import json
from functools import wraps

import aiohttp


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
                        return None

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
                                            timeout=5
                                    ) as response:
                                        if response.status == 200:
                                            client.logger.warning(
                                                message="Internet has been restored, let's continue...")
                                            break
                            except:
                                client.logger.warning(message="Internet is not available yet, we are waiting...")
                                continue
                        continue

                except aiohttp.ClientResponseError as e:
                    client.logger.error(
                        message=f"Error HTTP {e.status} в {func.__name__}",
                        extra_data={e.message}
                    )
                except json.JSONDecodeError:
                    client.logger.error(
                        message=f"Error JSON in {func.__name__}",
                    )
                except KeyError as e:
                    client.logger.error(
                        message=f"Key {e} is missing in {func.__name__}",
                    )
                except Exception as e:
                    client.logger.error(
                        message=f"Error in {func.__name__}",
                        extra_data=f"{type(e).__name__}: {e}"
                    )
                return None

        return wrapper
