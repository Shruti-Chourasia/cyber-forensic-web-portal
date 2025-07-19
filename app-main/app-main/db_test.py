#!/usr/bin/env python3
"""
Database Connectivity Test for Cyber Forensic Portal
Tests MongoDB connection and basic database operations
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path('/app/backend')
load_dotenv(ROOT_DIR / '.env')

async def test_mongodb_connection():
    """Test MongoDB connection and basic operations"""
    print("=" * 60)
    print("MONGODB CONNECTIVITY TEST")
    print("=" * 60)
    
    try:
        # Get MongoDB URL from environment
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        db_name = os.environ.get('DB_NAME', 'test_database')
        
        print(f"MongoDB URL: {mongo_url}")
        print(f"Database Name: {db_name}")
        print("-" * 60)
        
        # Connect to MongoDB
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        # Test connection
        await client.admin.command('ping')
        print("✅ MongoDB connection successful")
        
        # Test collections access
        collections = await db.list_collection_names()
        print(f"✅ Available collections: {collections}")
        
        # Test users collection
        users_count = await db.users.count_documents({})
        print(f"✅ Users collection accessible - Document count: {users_count}")
        
        # Test evidence_submissions collection
        evidence_count = await db.evidence_submissions.count_documents({})
        print(f"✅ Evidence submissions collection accessible - Document count: {evidence_count}")
        
        # Test basic insert operation (cleanup after)
        test_doc = {"test": "connectivity_test", "timestamp": "2024-01-15T10:00:00Z"}
        result = await db.test_collection.insert_one(test_doc)
        print(f"✅ Insert operation successful - ID: {result.inserted_id}")
        
        # Cleanup test document
        await db.test_collection.delete_one({"_id": result.inserted_id})
        print("✅ Cleanup successful")
        
        # Close connection
        client.close()
        print("✅ Database connectivity test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Database connectivity test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_mongodb_connection())
    if success:
        print("\n🎉 MongoDB is properly configured and accessible!")
    else:
        print("\n⚠️  MongoDB connectivity issues detected.")