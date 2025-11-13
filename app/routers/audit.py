from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app import models, schemas
from app.auth import require_role

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("/communication-rules", response_model=List[schemas.CommunicationRuleResponse])
async def audit_communication_rules(
    skip: int = 0,
    limit: int = 100,
    dept_id: Optional[int] = None,
    user_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_role(["admin", "auditor"]))
):
    """
    Audit all communication rules with filters.
    """
    query = select(models.CommunicationRule)
    
    if dept_id:
        query = query.filter(
            or_(
                models.CommunicationRule.dept_a_id == dept_id,
                models.CommunicationRule.dept_b_id == dept_id
            )
        )
    
    if user_id:
        query = query.filter(
            or_(
                models.CommunicationRule.requester_id == user_id,
                models.CommunicationRule.approved_by_id == user_id
            )
        )
    
    query = query.offset(skip).limit(limit).order_by(models.CommunicationRule.created_at.desc())
    
    result = await db.execute(query)
    rules = result.scalars().all()
    return rules


@router.get("/message-logs", response_model=List[schemas.MessageLogResponse])
async def audit_message_logs(
    skip: int = 0,
    limit: int = 100,
    sender_id: Optional[int] = None,
    receiver_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_role(["admin", "auditor"]))
):
    """
    Comprehensive audit of all message logs with various filters.
    """
    query = select(models.MessageLog)
    
    if sender_id:
        query = query.filter(models.MessageLog.sender_id == sender_id)
    
    if receiver_id:
        query = query.filter(models.MessageLog.receiver_id == receiver_id)
    
    if status_filter:
        query = query.filter(models.MessageLog.status == status_filter)
    
    if start_date:
        query = query.filter(models.MessageLog.timestamp >= start_date)
    
    if end_date:
        query = query.filter(models.MessageLog.timestamp <= end_date)
    
    query = query.offset(skip).limit(limit).order_by(models.MessageLog.timestamp.desc())
    
    result = await db.execute(query)
    logs = result.scalars().all()
    return logs


@router.get("/user-activity/{user_id}")
async def audit_user_activity(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_role(["admin", "auditor"]))
):
    """
    Get comprehensive activity log for a specific user.
    """
    from sqlalchemy.orm import selectinload
    
    user_result = await db.execute(
        select(models.User)
        .filter(models.User.id == user_id)
        .options(selectinload(models.User.role), selectinload(models.User.department))
    )
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get all rules requested by user
    requested_rules_result = await db.execute(
        select(models.CommunicationRule).filter(models.CommunicationRule.requester_id == user_id)
    )
    requested_rules = requested_rules_result.scalars().all()
    
    # Get all rules approved by user
    approved_rules_result = await db.execute(
        select(models.CommunicationRule).filter(models.CommunicationRule.approved_by_id == user_id)
    )
    approved_rules = approved_rules_result.scalars().all()
    
    # Get all messages sent by user
    sent_messages_result = await db.execute(
        select(models.MessageLog).filter(models.MessageLog.sender_id == user_id)
    )
    sent_messages = sent_messages_result.scalars().all()
    
    # Get all messages received by user
    received_messages_result = await db.execute(
        select(models.MessageLog).filter(models.MessageLog.receiver_id == user_id)
    )
    received_messages = received_messages_result.scalars().all()
    
    return {
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "department": user.department.name,
            "role": user.role.name
        },
        "requested_rules": [schemas.CommunicationRuleResponse.model_validate(r) for r in requested_rules],
        "approved_rules": [schemas.CommunicationRuleResponse.model_validate(r) for r in approved_rules],
        "sent_messages_count": len(list(sent_messages)),
        "received_messages_count": len(list(received_messages)),
        "sent_messages": [schemas.MessageLogResponse.model_validate(m) for m in sent_messages],
        "received_messages": [schemas.MessageLogResponse.model_validate(m) for m in received_messages]
    }

