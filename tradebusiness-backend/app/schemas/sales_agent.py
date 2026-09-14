"""销售智能体 Schema。"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SalesAgentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    company_intro: Optional[str] = None
    product_intro: Optional[str] = None
    value_proposition: Optional[str] = None
    target_customer: Optional[str] = None
    tone: str = "professional"
    forbidden_words: Optional[str] = None
    default_language: str = "en"
    is_default: bool = False


class SalesAgentUpdate(SalesAgentCreate):
    pass


class SalesAgentResponse(SalesAgentCreate):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class KnowledgeDocumentResponse(BaseModel):
    id: str
    agent_id: str
    file_name: str
    content_text: str
    embedding_status: str
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class PromptTemplateCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    channel: str = "email"
    language: str = "en"
    prompt_text: str = Field(..., min_length=1)
    is_active: bool = True


class PromptTemplateResponse(PromptTemplateCreate):
    id: str
    agent_id: str
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}
