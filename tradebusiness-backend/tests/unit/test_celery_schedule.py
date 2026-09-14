"""Celery 调度配置测试。"""

import inspect

from app.tasks import automation_tasks
from app.tasks.automation_tasks import celery_app


def test_beat_tasks_are_registered() -> None:
    """Beat 中的每个任务都必须能被当前 worker 注册表找到。"""
    scheduled_names = {entry["task"] for entry in celery_app.conf.beat_schedule.values()}

    assert scheduled_names
    assert scheduled_names.issubset(celery_app.tasks)


def test_lead_followup_task_is_scheduled() -> None:
    """到期潜客跟进任务必须由 Beat 定时触发。"""
    tasks = {entry["task"] for entry in celery_app.conf.beat_schedule.values()}

    assert "send-due-lead-followups" in tasks


def test_automated_followup_excludes_invalid_leads() -> None:
    """自动跟进源码必须保留无效潜客拦截条件。"""
    assert 'Lead.status != "invalid"' in inspect.getsource(
        automation_tasks.send_due_lead_followups_task
    )


def test_async_celery_tasks_dispose_engine_between_event_loops() -> None:
    """Celery 异步任务应隔离不同事件循环的连接池。"""
    source = inspect.getsource(automation_tasks.run_async_task)

    assert "await engine.dispose()" in source
