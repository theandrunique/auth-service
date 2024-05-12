import motor.motor_asyncio

from .config import settings

client = motor.motor_asyncio.AsyncIOMotorClient(
    settings.URI.unicode_string(),
    uuidRepresentation="standard",
    serverSelectionTimeoutMS=5000,
)

db = client[settings.DATABASE_NAME]
