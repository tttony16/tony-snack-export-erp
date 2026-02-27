import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.models.enums import AuditAction, UserRole

# --- User management schemas ---


class SystemUserCreate(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=6)
    display_name: str = Field(..., min_length=1, max_length=100)
    email: str | None = None
    phone: str | None = None
    role: UserRole = UserRole.VIEWER


class SystemUserUpdate(BaseModel):
    display_name: str | None = None
    email: str | None = None
    phone: str | None = None


class SystemUserRead(BaseModel):
    id: uuid.UUID
    username: str
    display_name: str
    email: str | None = None
    phone: str | None = None
    role: UserRole
    is_active: bool
    last_login_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SystemUserListParams(BaseModel):
    keyword: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    sort_by: str = "created_at"
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")


class UserRoleUpdate(BaseModel):
    role: UserRole


class UserStatusUpdate(BaseModel):
    is_active: bool


# --- Audit Log schemas ---


class AuditLogRead(BaseModel):
    id: int
    user_id: uuid.UUID | None = None
    action: AuditAction
    resource_type: str
    resource_id: str | None = None
    detail: dict | None = None
    ip_address: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AuditLogListParams(BaseModel):
    user_id: uuid.UUID | None = None
    action: AuditAction | None = None
    resource_type: str | None = None
    date_from: str | None = None
    date_to: str | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    sort_by: str = "created_at"
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")


# --- System Config schemas ---


class SystemConfigRead(BaseModel):
    id: int
    config_key: str
    config_value: Any
    description: str | None = None
    updated_at: datetime
    updated_by: uuid.UUID | None = None

    model_config = {"from_attributes": True}


class SystemConfigUpdate(BaseModel):
    config_value: Any
    description: str | None = None
