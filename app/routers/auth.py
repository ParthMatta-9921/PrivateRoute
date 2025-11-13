from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from pydantic import BaseModel
from app.database import get_db, settings
from app import models, schemas
from app.auth import authenticate_user, create_access_token, get_current_active_user, get_password_hash, verify_password
from app.password_validator import validate_password_strength

router = APIRouter(prefix="/api/auth", tags=["authentication"])


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


@router.post("/login", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.UserResponse)
async def read_users_me(current_user: models.User = Depends(get_current_active_user)):
    return current_user


@router.post("/change-password", response_model=dict)
async def change_password(
    password_change: ChangePasswordRequest,
    current_user: models.User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Allow logged-in users to change their password.
    Requires current password verification and new password meeting strength requirements.
    """
    # Verify current password is correct
    if not verify_password(password_change.current_password, str(current_user.password_hash)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )
    
    # Validate new password is different
    if password_change.current_password == password_change.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
        )
    
    # Validate password strength
    is_valid, message = validate_password_strength(password_change.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # Update password in database
    await db.execute(
        update(models.User)
        .where(models.User.id == current_user.id)
        .values(password_hash=get_password_hash(password_change.new_password))
    )
    await db.commit()
    
    return {
        "message": "Password changed successfully",
        "email": current_user.email,
        "details": "Your password must contain: at least 8 characters, one uppercase letter, one lowercase letter, one digit, and one special character"
    }


