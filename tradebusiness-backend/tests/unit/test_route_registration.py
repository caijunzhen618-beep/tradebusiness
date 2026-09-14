"""验证关键 API 路由已注册。"""

from app.main import app


def test_operational_routes_are_registered() -> None:
    """关键业务路由应挂载到 FastAPI 应用。"""
    routes = set()
    for route in app.routes:
        if not hasattr(route, "methods"):
            continue
        for method in route.methods:
            routes.add((method, route.path))

    assert ("POST", "/api/v1/files/upload/logo") in routes
    assert ("POST", "/api/v1/files/upload/attachment") in routes
    assert ("GET", "/api/v1/export/stats") in routes
    assert ("GET", "/api/v1/leads") in routes
    assert ("DELETE", "/api/v1/notifications/delete-read") in routes
    assert ("DELETE", "/api/v1/scraping/tasks/{task_id}") in routes
    assert ("POST", "/api/v1/emails/templates") in routes
    assert ("GET", "/api/v1/emails/templates/{template_id}") in routes
    assert ("PUT", "/api/v1/emails/templates/{template_id}") in routes
    assert ("DELETE", "/api/v1/emails/templates/{template_id}") in routes
