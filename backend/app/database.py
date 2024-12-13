# backend/app/database.py
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from datetime import datetime

class Database:
    client: Optional[AsyncIOMotorClient] = None

    @classmethod
    async def connect_db(cls):
        # Connect to local MongoDB instance
        cls.client = AsyncIOMotorClient("mongodb://localhost:27017")
        cls.db = cls.client.parlay_pulse  # Create/use a database named parlay_pulse

    @classmethod
    async def close_db(cls):
        if cls.client is not None:
            cls.client.close()

    @classmethod
    async def save_analysis(cls, data: dict):
        # Add timestamp to the analysis
        data["timestamp"] = datetime.utcnow()
        return await cls.db.analyses.insert_one(data)

    @classmethod
    async def get_user_analyses(cls, wallet_address: str):
        cursor = cls.db.analyses.find({"wallet_address": wallet_address})
        return await cursor.to_list(length=20)  # Get last 20 analyses