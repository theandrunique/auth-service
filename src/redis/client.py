from redis.asyncio import ConnectionPool

from .config import settings

pool = ConnectionPool.from_url(str(settings.URL))
