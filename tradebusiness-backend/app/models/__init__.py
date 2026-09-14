"""
数据库模型模块
包含所有 SQLAlchemy ORM 模型
"""

from app.models.base import Base, TimestampMixin
from app.models.customer import Customer
from app.models.email import Email, EmailTemplate
from app.models.holiday import Holiday
from app.models.lead_generation import (
    CompanyResearchReport,
    FollowupTask,
    Lead,
    LeadContact,
    LeadSearchTask,
    SalesCopy,
)
from app.models.notification import Notification
from app.models.scraped_lead import ScrapedLead
from app.models.scraping_task import ScrapingTask, TaskStatus
from app.models.task import Task
from app.models.user import User

__all__ = [
    "Base",
    "TimestampMixin",
    "User",
    "Customer",
    "Email",
    "EmailTemplate",
    "Holiday",
    "LeadSearchTask",
    "Lead",
    "LeadContact",
    "CompanyResearchReport",
    "SalesCopy",
    "Task",
    "Notification",
    "ScrapingTask",
    "TaskStatus",
    "ScrapedLead",
]

from app.models.billing import (
    CreditTransaction,
    CreditWallet,
    PaymentOrder,
    SubscriptionPlan,
    UserSubscription,
)
from app.models.sales_agent import AgentKnowledgeDocument, AgentPromptTemplate, SalesAgent
