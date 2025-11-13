from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, or_, select, delete, update
from typing import List, Optional
from app.database import get_db
from app import models, schemas
from app.auth import get_current_active_user, require_role

router = APIRouter(prefix="/api/communication-rules", tags=["communication-rules"])


@router.post("/permanent", response_model=schemas.CommunicationRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_permanent_rule(
    rule: schemas.CommunicationRuleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_role(["admin"]))
):
    """
    Only admins can create permanent communication rules.
    """
    if rule.rule_type != "permanent":
        raise HTTPException(status_code=400, detail="This endpoint is for permanent rules only")
    
    # Validate departments exist
    dept_a_result = await db.execute(select(models.Department).filter(models.Department.id == rule.dept_a_id))
    dept_a = dept_a_result.scalar_one_or_none()
    dept_b_result = await db.execute(select(models.Department).filter(models.Department.id == rule.dept_b_id))
    dept_b = dept_b_result.scalar_one_or_none()
    
    if not dept_a or not dept_b:
        raise HTTPException(status_code=404, detail="One or both departments not found")
    
    if rule.dept_a_id == rule.dept_b_id:
        raise HTTPException(status_code=400, detail="Cannot create rule for same department")
    
    # Check if rule already exists
    existing_result = await db.execute(
        select(models.CommunicationRule).filter(
            and_(
                models.CommunicationRule.dept_a_id == rule.dept_a_id,
                models.CommunicationRule.dept_b_id == rule.dept_b_id,
                models.CommunicationRule.rule_type == "permanent",
                models.CommunicationRule.is_active == True
            )
        )
    )
    existing = existing_result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(status_code=400, detail="Permanent rule already exists between these departments")
    
    db_rule = models.CommunicationRule(
        dept_a_id=rule.dept_a_id,
        dept_b_id=rule.dept_b_id,
        rule_type="permanent",
        approved_by_id=current_user.id,
        reason=rule.reason,
        user_specific=False,
        expiry_timestamp=None
    )
    db.add(db_rule)
    await db.commit()
    await db.refresh(db_rule)
    return db_rule


@router.post("/request", response_model=schemas.CommunicationRuleResponse, status_code=status.HTTP_201_CREATED)
async def request_temporary_access(
    request: schemas.CommunicationRuleRequest,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Users can request temporary access to communicate with another department.
    """
    # Get current user's department - extract Python value
    sender_dept_id = current_user.dept_id
    
    # Validate target department exists
    target_dept_result = await db.execute(select(models.Department).filter(models.Department.id == request.target_dept_id))
    target_dept = target_dept_result.scalar_one_or_none()
    if not target_dept:
        raise HTTPException(status_code=404, detail="Target department not found")
    
    # Compare actual values, not SQLAlchemy columns
    if sender_dept_id == request.target_dept_id:  # type: ignore
        raise HTTPException(status_code=400, detail="Cannot request access to your own department")
    
    # If user_specific, validate target user exists and is in target department
    if request.target_user_id:
        target_user_result = await db.execute(
            select(models.User).filter(
                models.User.id == request.target_user_id,
                models.User.dept_id == request.target_dept_id
            )
        )
        target_user = target_user_result.scalar_one_or_none()
        if not target_user:
            raise HTTPException(status_code=404, detail="Target user not found in target department")
    
    # Calculate expiry
    expiry = datetime.now(timezone.utc) + timedelta(hours=request.expiry_hours) if request.expiry_hours else None
    
    # Create rule (pending approval)
    db_rule = models.CommunicationRule(
        dept_a_id=sender_dept_id,
        dept_b_id=request.target_dept_id,
        rule_type="temporary",
        requester_id=current_user.id,
        approved_by_id=current_user.id,  # Will be updated when manager approves
        reason=request.reason,
        user_specific=request.target_user_id is not None,
        expiry_timestamp=expiry,
        is_active=False  # Not active until approved
    )
    db.add(db_rule)
    await db.commit()
    await db.refresh(db_rule)
    return db_rule


@router.get("/pending", response_model=List[schemas.CommunicationRuleResponse])
async def get_pending_requests(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_role(["manager", "admin"]))
):
    """
    Managers and admins can see pending requests for their department.
    """
    # Get all pending temporary rules where current user's department is involved
    result = await db.execute(
        select(models.CommunicationRule).filter(
            and_(
                models.CommunicationRule.is_active == False,
                models.CommunicationRule.rule_type == "temporary",
                or_(
                    models.CommunicationRule.dept_a_id == current_user.dept_id,
                    models.CommunicationRule.dept_b_id == current_user.dept_id
                )
            )
        )
    )
    pending_rules = result.scalars().all()
    
    return pending_rules


@router.post("/approve", response_model=schemas.CommunicationRuleResponse)
async def approve_rule(
    approval: schemas.CommunicationRuleApproval,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_role(["manager", "admin"]))
):
    """
    Managers can approve temporary access requests for their department.
    Admins can approve any request.
    """
    result = await db.execute(select(models.CommunicationRule).filter(models.CommunicationRule.id == approval.rule_id))
    db_rule = result.scalar_one_or_none()
    if not db_rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    # Admins can approve any rule, managers can only approve rules involving their department
    # Access actual Python values from ORM objects
    if hasattr(current_user, 'role') and current_user.role and current_user.role.name.lower() != "admin":
        dept_a = db_rule.dept_a_id
        dept_b = db_rule.dept_b_id
        user_dept = current_user.dept_id
        if user_dept not in [dept_a, dept_b]:
            raise HTTPException(status_code=403, detail="You can only approve rules involving your department")
    
    # Build the updated reason
    reason_value = db_rule.reason
    current_reason = str(reason_value) if reason_value is not None else ""
    
    if approval.approve:
        new_reason = current_reason
        if approval.reason:
            new_reason = f"{current_reason} | Approval: {approval.reason}" if current_reason else f"Approval: {approval.reason}"
        
        await db.execute(
            update(models.CommunicationRule)
            .where(models.CommunicationRule.id == approval.rule_id)
            .values(
                is_active=True,
                approved_by_id=current_user.id,
                reason=new_reason
            )
        )
    else:
        new_reason = current_reason
        if approval.reason:
            new_reason = f"{current_reason} | Rejected: {approval.reason}" if current_reason else f"Rejected: {approval.reason}"
        
        await db.execute(
            update(models.CommunicationRule)
            .where(models.CommunicationRule.id == approval.rule_id)
            .values(
                is_active=False,
                reason=new_reason
            )
        )
    
    await db.commit()
    
    # Refresh the rule to return updated data
    result = await db.execute(select(models.CommunicationRule).filter(models.CommunicationRule.id == approval.rule_id))
    db_rule = result.scalar_one_or_none()
    return db_rule


@router.get("/", response_model=List[schemas.CommunicationRuleResponse])
async def read_rules(
    skip: int = 0,
    limit: int = 100,
    dept_id: Optional[int] = None,
    rule_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    List communication rules. Can filter by department and rule type.
    """
    query = select(models.CommunicationRule)
    
    if dept_id:
        query = query.filter(
            or_(
                models.CommunicationRule.dept_a_id == dept_id,
                models.CommunicationRule.dept_b_id == dept_id
            )
        )
    
    if rule_type:
        query = query.filter(models.CommunicationRule.rule_type == rule_type)
    
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    rules = result.scalars().all()
    return rules


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(
    rule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_role(["admin"]))
):
    """
    Only admins can delete rules.
    """
    result = await db.execute(select(models.CommunicationRule).filter(models.CommunicationRule.id == rule_id))
    db_rule = result.scalar_one_or_none()
    if not db_rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    await db.execute(delete(models.CommunicationRule).filter(models.CommunicationRule.id == rule_id))
    await db.commit()
    return None

