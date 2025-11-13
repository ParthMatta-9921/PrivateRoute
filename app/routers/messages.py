from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.database import get_db, settings
from app import models, schemas
from app.auth import get_current_active_user, require_role
from app.permissions import check_communication_permission
# Email functionality disabled - commented out for future updates
# from app.email_service import send_email

router = APIRouter(prefix="/api/messages", tags=["messages"])


@router.post("/send", response_model=schemas.MessageLogResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    message: schemas.MessageSend,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Send a message. The system will check permissions before allowing.
    Messages are stored in the database (MessageLog table).
    Email functionality is currently disabled (commented out for future updates).
    """
    # Check if receiver exists
    receiver_result = await db.execute(select(models.User).filter(models.User.id == message.receiver_id))
    receiver = receiver_result.scalar_one_or_none()
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")
    
    if current_user.id == message.receiver_id:
        raise HTTPException(status_code=400, detail="Cannot send message to yourself")
    
    # Check communication permission
    is_allowed, reason = await check_communication_permission(
        db, current_user.id, message.receiver_id
    )
    
    # Create message log
    db_message = models.MessageLog(
        sender_id=current_user.id,
        receiver_id=message.receiver_id,
        subject=message.subject,
        message_content=message.message_content,
        status="sent" if is_allowed else "blocked",
        reason=reason if not is_allowed else None
    )
    db.add(db_message)
    await db.commit()
    await db.refresh(db_message)
    
    # HOW MESSAGES ARE SENT:
    # Messages are "sent" by creating a record in the MessageLog table in the database.
    # The message is stored with sender_id, receiver_id, subject, message_content, 
    # status ("sent" or "blocked"), and timestamp.
    # Users can retrieve their messages using:
    # - GET /api/messages/sent - to see messages they sent
    # - GET /api/messages/received - to see messages they received
    # - GET /api/messages/logs - admins/auditors can see all messages
    
    if not is_allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Message blocked: {reason}. Please request access first."
        )
    
    # Email functionality disabled - commented out for future updates
    # Messages are currently only stored in the database (MessageLog table)
    # To re-enable email functionality:
    # 1. Uncomment the import: from app.email_service import send_email
    # 2. Uncomment the code below
    # 3. Set ENABLE_EMAIL=True in .env file
    # 4. Configure SMTP settings in .env file
    #
    # # Send email if enabled and message was allowed
    # if settings.enable_email and is_allowed:
    #     email_sent = await send_email(
    #         recipient_email=receiver.email,
    #         subject=message.subject or f"Message from {current_user.name}",
    #         body=message.message_content,
    #         sender_name=current_user.name,
    #         sender_email=current_user.email
    #     )
    #     # Update message log with email status if needed
    #     if not email_sent:
    #         # Log email failure but don't fail the request
    #         db_message.reason = f"{db_message.reason or ''} | Email delivery failed".strip()
    #         await db.commit()
    
    return db_message


@router.get("/sent", response_model=List[schemas.MessageLogResponse])
async def get_sent_messages(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get messages sent by current user.
    """
    result = await db.execute(
        select(models.MessageLog)
        .filter(models.MessageLog.sender_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .order_by(models.MessageLog.timestamp.desc())
    )
    messages = result.scalars().all()
    return messages


@router.get("/received", response_model=List[schemas.MessageLogResponse])
async def get_received_messages(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get messages received by current user.
    """
    result = await db.execute(
        select(models.MessageLog)
        .filter(models.MessageLog.receiver_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .order_by(models.MessageLog.timestamp.desc())
    )
    messages = result.scalars().all()
    return messages


@router.get("/logs", response_model=List[schemas.MessageLogResponse])
async def get_all_message_logs(
    skip: int = 0,
    limit: int = 100,
    sender_id: Optional[int] = None,
    receiver_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_role(["admin", "auditor"]))
):
    """
    Admins and auditors can view all message logs with filters.
    """
    query = select(models.MessageLog)
    
    if sender_id:
        query = query.filter(models.MessageLog.sender_id == sender_id)
    
    if receiver_id:
        query = query.filter(models.MessageLog.receiver_id == receiver_id)
    
    if status_filter:
        query = query.filter(models.MessageLog.status == status_filter)
    
    query = query.offset(skip).limit(limit).order_by(models.MessageLog.timestamp.desc())
    
    result = await db.execute(query)
    messages = result.scalars().all()
    return messages
