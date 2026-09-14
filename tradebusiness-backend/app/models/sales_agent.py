"""销售智能体模型。"""

from typing import Optional

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class SalesAgent(Base, UUIDMixin, TimestampMixin):
    """用户配置的销售智能体。"""

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    company_intro: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    product_intro: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    value_proposition: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    target_customer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tone: Mapped[str] = mapped_column(String(50), default="professional", nullable=False)
    forbidden_words: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    default_language: Mapped[str] = mapped_column(String(20), default="en", nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class AgentKnowledgeDocument(Base, UUIDMixin, TimestampMixin):
    """销售智能体知识库资料。"""

    agent_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("sales_agents.id", ondelete="CASCADE"), index=True
    )
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    content_text: Mapped[str] = mapped_column(Text, nullable=False)
    embedding_status: Mapped[str] = mapped_column(String(30), default="pending", nullable=False)


class AgentPromptTemplate(Base, UUIDMixin, TimestampMixin):
    """销售智能体话术模板。"""

    agent_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("sales_agents.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    channel: Mapped[str] = mapped_column(String(30), default="email", nullable=False)
    language: Mapped[str] = mapped_column(String(20), default="en", nullable=False)
    prompt_text: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
