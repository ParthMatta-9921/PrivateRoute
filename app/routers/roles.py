from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.database import get_db
from app import models, schemas
from app.auth import get_current_active_user, require_role

router = APIRouter(prefix="/api/roles", tags=["roles"])


@router.post("/", response_model=schemas.RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    role: schemas.RoleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_role(["admin"]))
):
    result = await db.execute(select(models.Role).filter(models.Role.name == role.name))
    db_role = result.scalar_one_or_none()
    if db_role:
        raise HTTPException(status_code=400, detail="Role already exists")
    
    db_role = models.Role(name=role.name)
    db.add(db_role)
    await db.commit()
    await db.refresh(db_role)
    return db_role


@router.get("/", response_model=List[schemas.RoleResponse])
async def read_roles(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    result = await db.execute(select(models.Role).offset(skip).limit(limit))
    roles = result.scalars().all()
    return roles


@router.get("/{role_id}", response_model=schemas.RoleResponse)
async def read_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    result = await db.execute(select(models.Role).filter(models.Role.id == role_id))
    db_role = result.scalar_one_or_none()
    if db_role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return db_role

