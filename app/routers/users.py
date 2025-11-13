from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_, select
from typing import List, Optional
from app.database import get_db
from app import models, schemas
from app.auth import get_current_active_user, require_role, get_password_hash
from app.permissions import get_communicable_users

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: schemas.UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_role(["admin"]))
):
    # Check if email already exists
    result = await db.execute(select(models.User).filter(models.User.email == user.email))
    db_user = result.scalar_one_or_none()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Check if department exists
    dept_result = await db.execute(select(models.Department).filter(models.Department.id == user.dept_id))
    dept = dept_result.scalar_one_or_none()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    
    # Check if role exists
    role_result = await db.execute(select(models.Role).filter(models.Role.id == user.role_id))
    role = role_result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        name=user.name,
        email=user.email,
        password_hash=hashed_password,
        dept_id=user.dept_id,
        role_id=user.role_id
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


@router.get("/", response_model=List[schemas.UserResponse])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_role(["admin", "auditor"]))
):
    result = await db.execute(select(models.User).offset(skip).limit(limit))
    users = result.scalars().all()
    return users


@router.get("/search", response_model=List[schemas.UserResponse])
async def search_communicable_users(
    q: Optional[str] = None,
    dept_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Search for users that the current user can send messages to.
    Only returns users based on communication rules and permissions.
    Can filter by search query (name/email) and department.
    """
    # Get all users the current user can communicate with
    communicable_users = await get_communicable_users(db, current_user.id)
    
    if not communicable_users:
        return []
    
    # Extract user IDs
    communicable_user_ids = [user.id for user in communicable_users]
    
    # Build query starting with communicable users
    query = select(models.User).filter(
        models.User.id.in_(communicable_user_ids)
    )
    
    # Apply search filter (name or email)
    if q:
        query = query.filter(
            or_(
                models.User.name.ilike(f"%{q}%"),
                models.User.email.ilike(f"%{q}%")
            )
        )
    
    # Apply department filter
    if dept_id:
        query = query.filter(models.User.dept_id == dept_id)
    
    # Apply pagination
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    users = result.scalars().all()
    
    return users


@router.get("/{user_id}", response_model=schemas.UserResponse)
async def read_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    # Users can only see their own profile unless they're admin/auditor
    if current_user.role.name.lower() not in ["admin", "auditor"] and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    result = await db.execute(select(models.User).filter(models.User.id == user_id))
    db_user = result.scalar_one_or_none()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

