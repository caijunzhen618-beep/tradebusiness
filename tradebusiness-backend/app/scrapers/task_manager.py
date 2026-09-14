"""
爬虫任务管理
处理爬虫任务的创建、调度和监控
"""

import asyncio
import uuid
from datetime import datetime
from typing import Any, List, Optional

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import get_logger
from app.models.scraping_task import ScrapingTask, TaskStatus

logger = get_logger(__name__)

MAX_EXECUTION_LOG_ITEMS = 80


class ScrapingTaskManager:
    """
    爬虫任务管理器

    管理爬虫任务的创建、执行和监控，使用数据库持久化
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_task(
        self,
        name: str,
        task_type: str,
        config: dict,
        created_by: str,
        keywords: Optional[List[str]] = None,
        countries: Optional[List[str]] = None,
        source_urls: Optional[List[str]] = None,
    ) -> ScrapingTask:
        """
        创建爬虫任务并保存到数据库

        Args:
            name: 任务名称
            task_type: 任务类型（google, kompass, yellow_pages, port_authorities等）
            config: 任务配置
            created_by: 创建者ID
            keywords: 关键词列表
            countries: 国家列表
            source_urls: 采集数据来源地址列表

        Returns:
            ScrapingTask对象
        """
        normalized_source_urls = source_urls or []
        task_config = dict(config)
        task_config["source_urls"] = normalized_source_urls

        task = ScrapingTask(
            id=str(uuid.uuid4()),
            name=name,
            task_type=task_type,
            config=task_config,
            keywords=keywords or [],
            countries=countries or [],
            source_urls=normalized_source_urls,
            status=TaskStatus.PENDING,
            created_by=created_by,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        self.session.add(task)
        await self.session.flush()

        logger.info(f"Scraping task created: {task.id} - {name}")

        return task

    async def get_task(self, task_id: str) -> Optional[ScrapingTask]:
        """
        从数据库获取任务

        Args:
            task_id: 任务ID

        Returns:
            ScrapingTask对象或None
        """
        result = await self.session.execute(select(ScrapingTask).where(ScrapingTask.id == task_id))
        return result.scalar_one_or_none()

    async def list_tasks(
        self,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
    ) -> tuple[List[ScrapingTask], int]:
        """
        从数据库列出任务

        Args:
            skip: 跳过的记录数
            limit: 返回的记录数
            status: 状态筛选

        Returns:
            (任务列表, 总数)
        """
        # 构建查询条件
        conditions = []
        if status:
            conditions.append(ScrapingTask.status == status)

        # 查询总数
        count_query = select(func.count(ScrapingTask.id))
        if conditions:
            count_query = count_query.where(and_(*conditions))

        total_result = await self.session.execute(count_query)
        total = total_result.scalar() or 0

        # 查询列表
        query = select(ScrapingTask)
        if conditions:
            query = query.where(and_(*conditions))

        query = query.order_by(ScrapingTask.created_at.desc())
        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        tasks = result.scalars().all()

        return list(tasks), total

    async def start_task(self, task_id: str) -> ScrapingTask:
        """
        启动任务并实际执行采集

        Args:
            task_id: 任务ID

        Returns:
            更新后的任务
        """
        task = await self.get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        if task.status != TaskStatus.PENDING:
            raise ValueError(f"Task {task_id} is not in pending status")

        task.status = TaskStatus.RUNNING
        task.started_at = datetime.utcnow()
        task.completed_at = None
        task.progress_current = 0
        task.progress_total = 0
        task.total_found = 0
        task.total_saved = 0
        task.status_message = "任务已启动，正在准备采集配置"
        task.error_message = None
        task.last_run_summary = None
        task.execution_log = [
            {
                "time": datetime.utcnow().isoformat(),
                "level": "info",
                "message": "任务已启动",
            }
        ]
        task.updated_at = datetime.utcnow()
        await self.session.commit()

        logger.info(f"Scraping task started: {task_id}")

        # 异步执行采集任务（不使用当前session）
        asyncio.create_task(self._execute_scraping_background(task_id))

        return task

    async def _execute_scraping_background(self, task_id: str):
        """
        在后台执行数据采集任务（使用独立的数据库会话）

        Args:
            task_id: 任务ID
        """
        from app.db.session import async_session_maker

        async with async_session_maker() as session:
            try:
                from app.scrapers.example_scraper import run_scraping_task

                # 重新加载任务对象
                task = await session.get(ScrapingTask, task_id)
                if not task:
                    logger.error(f"Task {task_id} not found in background task")
                    return

                # 进度回调函数
                async def progress_callback(
                    current: int,
                    total: int,
                    message: str,
                    level: str = "info",
                    extra: Optional[dict[str, Any]] = None,
                ):
                    # 更新任务进度
                    task.progress_current = current
                    task.progress_total = total
                    task.status_message = message
                    task.execution_log = self._append_task_log(
                        task.execution_log,
                        message=message,
                        level=level,
                        extra=extra,
                    )
                    task.updated_at = datetime.utcnow()
                    await session.commit()
                    logger.info(f"Task {task_id} progress: {current}/{total} - {message}")

                # 执行采集（传入session以保存数据到数据库）
                result = await run_scraping_task(
                    task_id=task_id,
                    task_type=task.task_type,
                    keywords=list(task.keywords) if task.keywords else [],
                    countries=list(task.countries) if task.countries else [],
                    config={
                        **dict(task.config),
                        "source_urls": list(task.source_urls) if task.source_urls else [],
                    },
                    progress_callback=progress_callback,
                    session=session,
                    save_to_db=True,
                )

                # 更新任务状态
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.utcnow()
                task.total_found = result["total_found"]
                task.total_saved = result["total_saved"]
                task.progress_current = result.get("progress_current") or task.progress_total or 1
                task.progress_total = result.get("progress_total") or task.progress_total or 1
                task.status_message = result.get("message") or self._build_completion_message(
                    result
                )
                task.last_run_summary = self._build_run_summary(result)
                task.execution_log = self._append_task_log(
                    task.execution_log,
                    message=task.status_message,
                    level="success" if result["total_saved"] else "warning",
                    extra=task.last_run_summary,
                )
                task.updated_at = datetime.utcnow()

                # 保存采集到的数据到日志（实际应用中应该保存到数据库）
                if result.get("companies"):
                    logger.info(f"Task {task_id} collected {len(result['companies'])} companies:")
                    for company in result["companies"][:5]:  # 只记录前5个
                        logger.info(f"  - {company.get('company_name')} ({company.get('country')})")
                    if len(result["companies"]) > 5:
                        logger.info(f"  ... and {len(result['companies']) - 5} more")

                await session.commit()
                logger.info(
                    f"Scraping task completed: {task_id} - found={result['total_found']}, saved={result['total_saved']}"
                )

            except Exception as e:
                logger.error(f"Scraping task {task_id} failed: {e}")

                try:
                    # 重新加载任务以更新状态
                    task = await session.get(ScrapingTask, task_id)
                    if task:
                        task.status = TaskStatus.FAILED
                        task.completed_at = datetime.utcnow()
                        task.error_message = str(e)
                        task.status_message = f"任务失败：{e}"
                        task.execution_log = self._append_task_log(
                            task.execution_log,
                            message=task.status_message,
                            level="error",
                        )
                        task.updated_at = datetime.utcnow()
                        await session.commit()
                except Exception as commit_error:
                    logger.error(f"Failed to update task status: {commit_error}")

    async def cancel_task(self, task_id: str) -> ScrapingTask:
        """
        取消任务

        Args:
            task_id: 任务ID

        Returns:
            更新后的任务
        """
        task = await self.get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        if task.status not in [TaskStatus.PENDING, TaskStatus.RUNNING]:
            raise ValueError(f"Cannot cancel task with status {task.status}")

        task.status = TaskStatus.CANCELLED
        task.updated_at = datetime.utcnow()

        if task.started_at and not task.completed_at:
            task.completed_at = datetime.utcnow()

        await self.session.flush()

        logger.info(f"Scraping task cancelled: {task_id}")

        return task

    async def update_task_progress(
        self,
        task_id: str,
        total_found: int = 0,
        total_saved: int = 0,
        error_message: Optional[str] = None,
    ):
        """
        更新任务进度

        Args:
            task_id: 任务ID
            total_found: 发现数据总数
            total_saved: 已保存数据数
            error_message: 错误信息
        """
        task = await self.get_task(task_id)
        if not task:
            return

        task.total_found = total_found
        task.total_saved = total_saved
        task.updated_at = datetime.utcnow()

        if error_message:
            task.error_message = error_message

        await self.session.flush()

    async def complete_task(
        self,
        task_id: str,
        total_found: int = 0,
        total_saved: int = 0,
    ):
        """
        标记任务为完成

        Args:
            task_id: 任务ID
            total_found: 发现数据总数
            total_saved: 已保存数据数
        """
        task = await self.get_task(task_id)
        if not task:
            return

        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.utcnow()
        task.total_found = total_found
        task.total_saved = total_saved
        task.updated_at = datetime.utcnow()

        await self.session.flush()

        logger.info(f"Scraping task completed: {task_id}")

    async def fail_task(
        self,
        task_id: str,
        error_message: str,
    ):
        """
        标记任务为失败

        Args:
            task_id: 任务ID
            error_message: 错误信息
        """
        task = await self.get_task(task_id)
        if not task:
            return

        task.status = TaskStatus.FAILED
        task.completed_at = datetime.utcnow()
        task.error_message = error_message
        task.updated_at = datetime.utcnow()

        await self.session.flush()

        logger.error(f"Scraping task failed: {task_id} - {error_message}")

    async def delete_task(self, task_id: str):
        """
        删除任务

        Args:
            task_id: 任务ID
        """
        task = await self.get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        await self.session.delete(task)
        await self.session.flush()

        logger.info(f"Scraping task deleted: {task_id}")

    @staticmethod
    def _append_task_log(
        execution_log: Optional[list],
        message: str,
        level: str = "info",
        extra: Optional[dict[str, Any]] = None,
    ) -> list:
        """Append one task log item and keep the latest entries."""
        items = list(execution_log or [])
        log_item: dict[str, Any] = {
            "time": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
        }
        if extra:
            log_item["extra"] = extra
        items.append(log_item)
        return items[-MAX_EXECUTION_LOG_ITEMS:]

    @staticmethod
    def _build_completion_message(result: dict[str, Any]) -> str:
        """Build a user-facing completion message."""
        if result.get("total_saved"):
            return f"采集完成，保存 {result['total_saved']} 条线索"
        diagnostics = result.get("diagnostics") or []
        if diagnostics:
            return f"采集完成但没有保存线索：{diagnostics[0]}"
        return "采集完成但没有发现可保存线索"

    @staticmethod
    def _build_run_summary(result: dict[str, Any]) -> dict[str, Any]:
        """Build compact run summary for the frontend."""
        return {
            "total_found": result.get("total_found", 0),
            "total_saved": result.get("total_saved", 0),
            "diagnostics": result.get("diagnostics", []),
            "source_checks": result.get("source_checks", []),
        }
