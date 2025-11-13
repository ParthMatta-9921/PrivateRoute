from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)

    users = relationship("User", back_populates="department")
    rules_as_dept_a = relationship("CommunicationRule", foreign_keys="CommunicationRule.dept_a_id", back_populates="dept_a")
    rules_as_dept_b = relationship("CommunicationRule", foreign_keys="CommunicationRule.dept_b_id", back_populates="dept_b")


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)

    users = relationship("User", back_populates="role")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    dept_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    public_key = Column(Text, nullable=True)
    encrypted_private_key = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    department = relationship("Department", back_populates="users")
    role = relationship("Role", back_populates="users")
    requests_made = relationship("CommunicationRule", foreign_keys="CommunicationRule.requester_id", back_populates="requester")
    approvals_made = relationship("CommunicationRule", foreign_keys="CommunicationRule.approved_by_id", back_populates="approver")
    sent_messages = relationship("MessageLog", foreign_keys="MessageLog.sender_id", back_populates="sender")
    received_messages = relationship("MessageLog", foreign_keys="MessageLog.receiver_id", back_populates="receiver")


class CommunicationRule(Base):
    __tablename__ = "communication_rules"

    id = Column(Integer, primary_key=True, index=True)
    dept_a_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    dept_b_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    rule_type = Column(String(20), nullable=False)  # 'temporary' or 'permanent'
    requester_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    expiry_timestamp = Column(DateTime(timezone=True), nullable=True)
    user_specific = Column(Boolean, default=False)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)

    dept_a = relationship("Department", foreign_keys=[dept_a_id], back_populates="rules_as_dept_a")
    dept_b = relationship("Department", foreign_keys=[dept_b_id], back_populates="rules_as_dept_b")
    requester = relationship("User", foreign_keys=[requester_id], back_populates="requests_made")
    approver = relationship("User", foreign_keys=[approved_by_id], back_populates="approvals_made")


class MessageLog(Base):
    __tablename__ = "message_logs"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject = Column(String(255), nullable=True)
    message_content = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(50), nullable=False)  # 'sent', 'blocked', 'pending'
    reason = Column(Text, nullable=True)

    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_messages")

