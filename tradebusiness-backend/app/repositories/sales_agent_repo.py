"""销售智能体和知识库数据访问。"""

from sqlalchemy import select, update

from app.models.sales_agent import AgentKnowledgeDocument, AgentPromptTemplate, SalesAgent
from app.repositories.base import BaseRepository


class SalesAgentRepository(BaseRepository[SalesAgent]):
    """销售智能体 Repository。"""

    def __init__(self, session):
        super().__init__(SalesAgent, session)

    async def list_by_user(self, user_id: str) -> list[SalesAgent]:
        result = await self.session.execute(
            select(SalesAgent)
            .where(SalesAgent.user_id == user_id)
            .order_by(SalesAgent.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_owned(self, agent_id: str, user_id: str) -> SalesAgent | None:
        result = await self.session.execute(
            select(SalesAgent).where(SalesAgent.id == agent_id, SalesAgent.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def clear_default(self, user_id: str) -> None:
        await self.session.execute(
            update(SalesAgent).where(SalesAgent.user_id == user_id).values(is_default=False)
        )


class KnowledgeDocumentRepository(BaseRepository[AgentKnowledgeDocument]):
    """知识库资料 Repository。"""

    def __init__(self, session):
        super().__init__(AgentKnowledgeDocument, session)

    async def list_by_agent(self, agent_id: str) -> list[AgentKnowledgeDocument]:
        result = await self.session.execute(
            select(AgentKnowledgeDocument)
            .where(AgentKnowledgeDocument.agent_id == agent_id)
            .order_by(AgentKnowledgeDocument.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_owned_document(
        self, document_id: str, agent_id: str
    ) -> AgentKnowledgeDocument | None:
        result = await self.session.execute(
            select(AgentKnowledgeDocument).where(
                AgentKnowledgeDocument.id == document_id,
                AgentKnowledgeDocument.agent_id == agent_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_context_text(
        self, agent_id: str, keywords: list[str] | None = None, max_length: int = 8000
    ) -> str:
        documents = await self.list_by_agent(agent_id)
        if keywords:
            normalized = [keyword.lower() for keyword in keywords if keyword]
            documents.sort(
                key=lambda doc: sum(word in doc.content_text.lower() for word in normalized),
                reverse=True,
            )
        return "\n\n".join(document.content_text for document in documents)[:max_length]


class PromptTemplateRepository(BaseRepository[AgentPromptTemplate]):
    """话术模板 Repository。"""

    def __init__(self, session):
        super().__init__(AgentPromptTemplate, session)

    async def get_owned(self, template_id: str, agent_id: str):
        result = await self.session.execute(
            select(AgentPromptTemplate).where(
                AgentPromptTemplate.id == template_id, AgentPromptTemplate.agent_id == agent_id
            )
        )
        return result.scalar_one_or_none()

    async def list_by_agent(self, agent_id: str):
        result = await self.session.execute(
            select(AgentPromptTemplate)
            .where(AgentPromptTemplate.agent_id == agent_id)
            .order_by(AgentPromptTemplate.created_at.desc())
        )
        return list(result.scalars().all())
