import asyncio
import json
from functools import wraps

import aiohttp


class BotDecorator:
    @staticmethod
    def reformat_response(func):
        @wraps(func)
        async def wrapper(response: str, *args, **kwargs):
            text_response = await response.text()
            start_index = text_response.find('{')
            end_index = text_response.rfind('}')
            json_str = text_response[start_index:end_index + 1]
            json_data = json.loads(json_str)

            return await func(json_data, *args, **kwargs)

        return wrapper

    @staticmethod
    def safe_request(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            client = args[0] if args else None

            try:
                return await func(*args, **kwargs)
            except (aiohttp.ClientConnectorError,
                    aiohttp.ServerTimeoutError,
                    asyncio.TimeoutError):
                client.logger.error(
                    message=f"Ошибка соединения в: {func.__name__}",
                )
            except aiohttp.ClientResponseError as e:
                client.logger.error(
                    message=f"Ошибка HTTP {e.status} в {func.__name__}",
                    extra_data={e.message}
                )
            except json.JSONDecodeError:
                client.logger.error(
                    message=f"Ошибка JSON в {func.__name__}",
                )
            except KeyError as e:
                client.logger.error(
                    message=f"Отсутствует ключ {e} в {func.__name__}",
                )
            except Exception as e:
                client.logger.error(
                    message=f"Ошибка в {func.__name__}",
                    extra_data=f"{type(e).__name__}: {e}"
                )
            return None

        return wrapper
