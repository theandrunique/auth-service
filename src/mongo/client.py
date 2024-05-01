import motor.motor_asyncio

from .config import settings

client = motor.motor_asyncio.AsyncIOMotorClient(
    settings.MONGO_URI,
    uuidRepresentation="standard",
    serverSelectionTimeoutMS=5000,
)

db = client[settings.DATABASE_NAME]
