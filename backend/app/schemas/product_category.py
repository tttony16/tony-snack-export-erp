from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ProductCategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    parent_id: uuid.UUID | None = None
    sort_order: int = 0


class ProductCategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    sort_order: int | None = None


class ProductCategoryRead(BaseModel):
    id: uuid.UUID
    name: str
    level: int
    parent_id: uuid.UUID | None = None
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProductCategoryTreeNode(ProductCategoryRead):
    children: list[ProductCategoryTreeNode] = []
