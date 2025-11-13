"""
Script to initialize the database with default roles and optionally an admin user.
Run this once after setting up the database.
"""
import asyncio
from app.database import engine, Base, AsyncSessionLocal
from app import models
from sqlalchemy import select

async def init_db():
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as db:
        try:
            # Create default roles if they don't exist
            roles = ["admin", "manager", "user", "auditor"]
            for role_name in roles:
                result = await db.execute(select(models.Role).filter(models.Role.name == role_name))
                existing_role = result.scalar_one_or_none()
                if not existing_role:
                    new_role = models.Role(name=role_name)
                    db.add(new_role)
                    print(f"Created role: {role_name}")
            
            await db.commit()
            print("Database initialized successfully!")
            print("\nDefault roles created: admin, manager, user, auditor")
            print("\nNext steps:")
            print("1. Create departments using POST /api/departments")
            print("2. Create an admin user using POST /api/users")
            print("3. Start the server with: uvicorn app.main:app --reload")
            
        except Exception as e:
            print(f"Error initializing database: {e}")
            await db.rollback()
            raise

if __name__ == "__main__":
    asyncio.run(init_db())

