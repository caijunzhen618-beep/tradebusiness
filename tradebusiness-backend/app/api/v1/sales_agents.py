"""销售智能体 API。"""

from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.repositories.sales_agent_repo import KnowledgeDocumentRepository, PromptTemplateRepository
from app.schemas.sales_agent import (
    KnowledgeDocumentResponse,
    PromptTemplateCreate,
    PromptTemplateResponse,
    SalesAgentCreate,
    SalesAgentResponse,
    SalesAgentUpdate,
)
from app.services.sales_agent_service import SalesAgentService

router = APIRouter()


@router.get("", response_model=list[SalesAgentResponse])
async def list_sales_agents(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    return await SalesAgentService(db).list(str(current_user.id))


@router.post("", response_model=SalesAgentResponse, status_code=status.HTTP_201_CREATED)
async def create_sales_agent(
    data: SalesAgentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await SalesAgentService(db).create(str(current_user.id), data.model_dump())


@router.patch("/{agent_id}", response_model=SalesAgentResponse)
async def update_sales_agent(
    agent_id: str,
    data: SalesAgentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await SalesAgentService(db).update(agent_id, str(current_user.id), data.model_dump())


@router.get("/{agent_id}/documents", response_model=list[KnowledgeDocumentResponse])
async def list_agent_documents(
    agent_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    agent = await SalesAgentService(db).repo.get_owned(agent_id, str(current_user.id))
    if not agent:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Sales agent not found")
    return await KnowledgeDocumentRepository(db).list_by_agent(agent_id)


@router.post(
    "/{agent_id}/documents",
    response_model=KnowledgeDocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_agent_document(
    agent_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    agent = await SalesAgentService(db).repo.get_owned(agent_id, str(current_user.id))
    if not agent:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Sales agent not found")
    content = (await file.read()).decode("utf-8-sig", errors="ignore")
    if not content.strip():
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail="Document is empty")
    return await KnowledgeDocumentRepository(db).create(
        agent_id=agent_id,
        file_name=file.filename or "document.txt",
        content_text=content[:100000],
        embedding_status="ready",
    )


@router.delete("/{agent_id}/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent_document(
    agent_id: str,
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from fastapi import HTTPException

    agent = await SalesAgentService(db).repo.get_owned(agent_id, str(current_user.id))
    if not agent:
        raise HTTPException(status_code=404, detail="Sales agent not found")
    document = await KnowledgeDocumentRepository(db).get_owned_document(document_id, agent_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    await db.delete(document)


@router.get("/{agent_id}/templates", response_model=list[PromptTemplateResponse])
async def list_agent_templates(
    agent_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    agent = await SalesAgentService(db).repo.get_owned(agent_id, str(current_user.id))
    if not agent:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Sales agent not found")
    return await PromptTemplateRepository(db).list_by_agent(agent_id)


@router.post(
    "/{agent_id}/templates",
    response_model=PromptTemplateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_agent_template(
    agent_id: str,
    data: PromptTemplateCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    agent = await SalesAgentService(db).repo.get_owned(agent_id, str(current_user.id))
    if not agent:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Sales agent not found")
    return await PromptTemplateRepository(db).create(agent_id=agent_id, **data.model_dump())
