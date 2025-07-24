#!/usr/bin/env python3
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

async def clear_users():
    try:
        client = AsyncIOMotorClient("mongodb://localhost:27017")
        db = client["test_database"]
        
        # Drop the users collection to start fresh
        await db.users.drop()
        print("Users collection cleared successfully")
        
        client.close()
    except Exception as e:
        print(f"Error clearing users: {e}")

if __name__ == "__main__":
    asyncio.run(clear_users())