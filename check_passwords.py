"""
Script to check for duplicate password hashes in the database
and help identify users with the same passwords
"""
import asyncio
from app.database import AsyncSessionLocal
from app import models
from sqlalchemy import select
from collections import defaultdict

async def check_duplicate_passwords():
    async with AsyncSessionLocal() as db:
        # Get all users
        result = await db.execute(select(models.User))
        users = result.scalars().all()
        
        if not users:
            print("❌ No users found in database")
            return
        
        # Group users by password hash
        hash_groups = defaultdict(list)
        for user in users:
            hash_groups[user.password_hash].append({
                "id": user.id,
                "name": user.name,
                "email": user.email
            })
        
        # Find duplicates
        duplicates = {hash_val: users_list for hash_val, users_list in hash_groups.items() if len(users_list) > 1}
        
        print("=" * 70)
        print("PASSWORD HASH DUPLICATE CHECK")
        print("=" * 70)
        print(f"\nTotal users: {len(users)}")
        print(f"Unique password hashes: {len(hash_groups)}")
        print(f"Duplicate hashes found: {len(duplicates)}\n")
        
        if duplicates:
            print("⚠️  USERS WITH SAME PASSWORDS:\n")
            for hash_val, users_list in duplicates.items():
                print(f"Hash: {hash_val[:50]}...")
                for u in users_list:
                    print(f"  - ID: {u['id']}, Name: {u['name']}, Email: {u['email']}")
                print()
        else:
            print("✅ NO DUPLICATE PASSWORDS FOUND - All users have unique passwords!")
        
        print("\n" + "=" * 70)
        print("ALL USERS:")
        print("=" * 70)
        for user in users:
            print(f"ID: {user.id} | Email: {user.email} | Name: {user.name}")
            print(f"  Hash: {user.password_hash[:60]}...")
            print()

if __name__ == "__main__":
    asyncio.run(check_duplicate_passwords())
