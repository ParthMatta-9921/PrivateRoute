from datetime import datetime, timezone
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, or_, select
from app import models
from fastapi import HTTPException, status


async def check_communication_permission(
    db: AsyncSession,
    sender_id: int,
    receiver_id: int,
    user_specific: bool = False
) -> tuple[bool, str]:
    """
    Check if sender has permission to communicate with receiver.
    Returns (is_allowed, reason)
    """
    # Get sender and receiver
    sender_result = await db.execute(select(models.User).filter(models.User.id == sender_id))
    sender = sender_result.scalar_one_or_none()
    receiver_result = await db.execute(select(models.User).filter(models.User.id == receiver_id))
    receiver = receiver_result.scalar_one_or_none()
    
    if not sender or not receiver:
        return False, "Sender or receiver not found"
    
    # Same department - always allowed
    if sender.dept_id == receiver.dept_id:
        return True, "Same department"
    
    sender_dept_id = sender.dept_id
    receiver_dept_id = receiver.dept_id
    
    # Check for active communication rules
    now = datetime.now(timezone.utc)
    
    # Check for permanent rules
    permanent_result = await db.execute(
        select(models.CommunicationRule).filter(
            and_(
                models.CommunicationRule.is_active == True,
                models.CommunicationRule.rule_type == "permanent",
                or_(
                    and_(
                        models.CommunicationRule.dept_a_id == sender_dept_id,
                        models.CommunicationRule.dept_b_id == receiver_dept_id
                    ),
                    and_(
                        models.CommunicationRule.dept_a_id == receiver_dept_id,
                        models.CommunicationRule.dept_b_id == sender_dept_id
                    )
                )
            )
        )
    )
    permanent_rule = permanent_result.scalar_one_or_none()
    
    if permanent_rule:
        return True, "Permanent rule exists"
    
    # Check for temporary rules
    temporary_result = await db.execute(
        select(models.CommunicationRule).filter(
            and_(
                models.CommunicationRule.is_active == True,
                models.CommunicationRule.rule_type == "temporary",
                or_(
                    models.CommunicationRule.expiry_timestamp == None,
                    models.CommunicationRule.expiry_timestamp > now
                ),
                or_(
                    and_(
                        models.CommunicationRule.dept_a_id == sender_dept_id,
                        models.CommunicationRule.dept_b_id == receiver_dept_id
                    ),
                    and_(
                        models.CommunicationRule.dept_a_id == receiver_dept_id,
                        models.CommunicationRule.dept_b_id == sender_dept_id
                    )
                )
            )
        )
    )
    temporary_rule = temporary_result.scalar_one_or_none()
    
    if temporary_rule:
        # If user_specific, check if requester matches sender
        if temporary_rule.user_specific:
            if temporary_rule.requester_id == sender_id:
                return True, "Temporary user-specific rule"
            else:
                return False, "Temporary rule is user-specific and doesn't match sender"
        else:
            return True, "Temporary department-wide rule"
    
    return False, "No communication rule found between departments"


async def get_communicable_users(
    db: AsyncSession,
    sender_id: int
) -> List[models.User]:
    """
    Get all users that the sender can communicate with based on rules and permissions.
    Returns a list of User objects.
    """
    sender_result = await db.execute(select(models.User).filter(models.User.id == sender_id))
    sender = sender_result.scalar_one_or_none()
    if not sender:
        return []
    
    sender_dept_id = sender.dept_id
    now = datetime.now(timezone.utc)
    
    # Start with users in the same department (always allowed)
    same_dept_result = await db.execute(
        select(models.User).filter(
            and_(
                models.User.dept_id == sender_dept_id,
                models.User.id != sender_id  # Exclude self
            )
        )
    )
    same_dept_users = same_dept_result.scalars().all()
    
    # Get all departments that have permanent rules with sender's department
    permanent_rules_result = await db.execute(
        select(models.CommunicationRule).filter(
            and_(
                models.CommunicationRule.is_active == True,
                models.CommunicationRule.rule_type == "permanent",
                or_(
                    models.CommunicationRule.dept_a_id == sender_dept_id,
                    models.CommunicationRule.dept_b_id == sender_dept_id
                )
            )
        )
    )
    permanent_rules = permanent_rules_result.scalars().all()
    
    # Collect department IDs from permanent rules
    allowed_dept_ids = set()
    for rule in permanent_rules:
        if rule.dept_a_id == sender_dept_id:
            allowed_dept_ids.add(rule.dept_b_id)
        else:
            allowed_dept_ids.add(rule.dept_a_id)
    
    # Get users from departments with permanent rules
    permanent_users = []
    if allowed_dept_ids:
        permanent_result = await db.execute(
            select(models.User).filter(models.User.dept_id.in_(allowed_dept_ids))
        )
        permanent_users = permanent_result.scalars().all()
    
    # Get temporary rules
    temporary_rules_result = await db.execute(
        select(models.CommunicationRule).filter(
            and_(
                models.CommunicationRule.is_active == True,
                models.CommunicationRule.rule_type == "temporary",
                or_(
                    models.CommunicationRule.expiry_timestamp == None,
                    models.CommunicationRule.expiry_timestamp > now
                ),
                or_(
                    models.CommunicationRule.dept_a_id == sender_dept_id,
                    models.CommunicationRule.dept_b_id == sender_dept_id
                )
            )
        )
    )
    temporary_rules = temporary_rules_result.scalars().all()
    
    # Collect users from temporary rules
    temporary_user_ids = set()
    temporary_dept_ids = set()
    
    for rule in temporary_rules:
        if rule.user_specific:
            # User-specific rule - only add if requester is the sender
            if rule.requester_id == sender_id:
                if rule.dept_a_id == sender_dept_id:
                    # Get users from dept_b (target department)
                    temp_result = await db.execute(
                        select(models.User).filter(models.User.dept_id == rule.dept_b_id)
                    )
                    temp_users = temp_result.scalars().all()
                    temporary_user_ids.update([u.id for u in temp_users])
                else:
                    # Get users from dept_a (target department)
                    temp_result = await db.execute(
                        select(models.User).filter(models.User.dept_id == rule.dept_a_id)
                    )
                    temp_users = temp_result.scalars().all()
                    temporary_user_ids.update([u.id for u in temp_users])
        else:
            # Department-wide temporary rule
            if rule.dept_a_id == sender_dept_id:
                temporary_dept_ids.add(rule.dept_b_id)
            else:
                temporary_dept_ids.add(rule.dept_a_id)
    
    # Get users from departments with temporary rules
    temporary_dept_users = []
    if temporary_dept_ids:
        temp_dept_result = await db.execute(
            select(models.User).filter(models.User.dept_id.in_(temporary_dept_ids))
        )
        temporary_dept_users = temp_dept_result.scalars().all()
    
    # Get specific users from temporary rules
    temporary_specific_users = []
    if temporary_user_ids:
        temp_specific_result = await db.execute(
            select(models.User).filter(models.User.id.in_(temporary_user_ids))
        )
        temporary_specific_users = temp_specific_result.scalars().all()
    
    # Combine all users and remove duplicates
    all_users = list(same_dept_users) + list(permanent_users) + list(temporary_dept_users) + list(temporary_specific_users)
    unique_users = {user.id: user for user in all_users}.values()
    
    return list(unique_users)

