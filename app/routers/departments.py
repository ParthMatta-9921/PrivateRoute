from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.database import get_db
from app import models, schemas
from app.auth import get_current_active_user, require_role

router = APIRouter(prefix="/api/departments", tags=["departments"])


@router.post("/", response_model=schemas.DepartmentResponse, status_code=status.HTTP_201_CREATED)
async def create_department(
    department: schemas.DepartmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_role(["admin"]))
):
    result = await db.execute(select(models.Department).filter(models.Department.name == department.name))
    db_dept = result.scalar_one_or_none()
    if db_dept:
        raise HTTPException(status_code=400, detail="Department already exists")
    
    db_dept = models.Department(name=department.name)
    db.add(db_dept)
    await db.commit()
    await db.refresh(db_dept)
    return db_dept


@router.get("/", response_model=List[schemas.DepartmentResponse])
async def read_departments(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    result = await db.execute(select(models.Department).offset(skip).limit(limit))
    departments = result.scalars().all()
    return departments


@router.get("/{dept_id}", response_model=schemas.DepartmentResponse)
async def read_department(
    dept_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    result = await db.execute(select(models.Department).filter(models.Department.id == dept_id))
    db_dept = result.scalar_one_or_none()
    if db_dept is None:
        raise HTTPException(status_code=404, detail="Department not found")
    return db_dept

