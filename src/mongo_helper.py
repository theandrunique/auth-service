import motor.motor_asyncio

from src.config import settings

mongo_client = motor.motor_asyncio.AsyncIOMotorClient(
    settings.MONGO_URL,
    uuidRepresentation='standard'
)
db = mongo_client[settings.MONGO_DATABASE_NAME]
