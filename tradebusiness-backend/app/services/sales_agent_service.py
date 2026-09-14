"""销售智能体业务服务。"""

from fastapi import HTTPException, status

from app.repositories.sales_agent_repo import SalesAgentRepository


class SalesAgentService:
    """销售智能体 CRUD。"""

    def __init__(self, session):
        self.repo = SalesAgentRepository(session)

    async def list(self, user_id: str):
        return await self.repo.list_by_user(user_id)

    async def create(self, user_id: str, data: dict):
        if data.get("is_default"):
            await self.repo.clear_default(user_id)
        return await self.repo.create(user_id=user_id, **data)

    async def update(self, agent_id: str, user_id: str, data: dict):
        agent = await self.repo.get_owned(agent_id, user_id)
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Sales agent not found"
            )
        if data.get("is_default"):
            await self.repo.clear_default(user_id)
        return await self.repo.update(agent, **data)
