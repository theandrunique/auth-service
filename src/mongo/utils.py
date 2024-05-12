import os

from pymongo.errors import ConnectionFailure

from src.logger import logger

from .client import client
from .config import settings


async def ping_mongo() -> None:
    ping_success = False
    for i in range(settings.PING_ATTEMPTS):
        attempt_text = f"({i + 1} attempt)" if i > 0 else ""
        try:
            logger.info(f"Pinging MongoDB... {attempt_text}")
            await client.admin.command("ping")
            logger.info(f"MongoDB ping successful. Connected to {settings.URI}.")
            ping_success = True
            break
        except ConnectionFailure as e:
            logger.error(
                f"Failed to ping MongoDB at {settings.URI}. Error: {e}"  # noqa: E501
            )

    if not ping_success:
        os._exit(1)


async def mongodb_info() -> None:
    server_info = await client.server_info()
    formatted_info = (
        f"MongoDB cluster info:\n"
        f"  - Version: {server_info['version']}\n"
        f"  - Git Version: {server_info['gitVersion']}\n"
        f"  - OpenSSL Running: {server_info['openssl']['running']}\n"
        f"  - Compiled with: {server_info['buildEnvironment']['cc']}\n"
        f"  - Storage Engines: {', '.join(server_info['storageEngines'])}\n"
    )
    logger.info(formatted_info)
