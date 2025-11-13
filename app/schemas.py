from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# User Schemas
class UserBase(BaseModel):
    name: str
    email: EmailStr
    dept_id: int
    role_id: int


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    public_key: Optional[str] = None
    encrypted_private_key: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Department Schemas
class DepartmentBase(BaseModel):
    name: str


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentResponse(DepartmentBase):
    id: int

    class Config:
        from_attributes = True


# Role Schemas
class RoleBase(BaseModel):
    name: str


class RoleCreate(RoleBase):
    pass


class RoleResponse(RoleBase):
    id: int

    class Config:
        from_attributes = True


# Communication Rule Schemas
class CommunicationRuleBase(BaseModel):
    dept_a_id: int
    dept_b_id: int
    rule_type: str = Field(..., pattern="^(temporary|permanent)$")
    reason: Optional[str] = None
    user_specific: bool = False


class CommunicationRuleCreate(CommunicationRuleBase):
    expiry_timestamp: Optional[datetime] = None


class CommunicationRuleRequest(BaseModel):
    target_dept_id: int
    target_user_id: Optional[int] = None
    reason: str
    expiry_hours: Optional[int] = 24
    max_messages: Optional[int] = None


class CommunicationRuleResponse(CommunicationRuleBase):
    id: int
    requester_id: Optional[int] = None
    approved_by_id: int
    expiry_timestamp: Optional[datetime] = None
    is_active: bool
    created_at: datetime
    user_specific: bool

    class Config:
        from_attributes = True


class CommunicationRuleApproval(BaseModel):
    rule_id: int
    approve: bool
    reason: Optional[str] = None


# Message Schemas
class MessageSend(BaseModel):
    receiver_id: int
    subject: Optional[str] = None
    message_content: str


class MessageLogResponse(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    subject: Optional[str] = None
    message_content: Optional[str] = None
    timestamp: datetime
    status: str
    reason: Optional[str] = None

    class Config:
        from_attributes = True


# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


# Audit/Logging Schemas
class AuditLogResponse(BaseModel):
    id: int
    action_type: str
    user_id: int
    details: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True

