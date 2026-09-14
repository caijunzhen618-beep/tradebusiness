"""
自定义异常类
定义应用中使用的所有异常
"""

from typing import Any, Optional


class AppException(Exception):
    """
    应用基础异常类

    所有自定义异常的基类
    """

    def __init__(
        self,
        message: str,
        code: str = "ERROR",
        status_code: int = 400,
        details: Optional[dict[str, Any]] = None,
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


# ==================== 认证异常 ====================


class AuthenticationException(AppException):
    """认证异常基类"""

    def __init__(
        self,
        message: str = "Authentication failed",
        code: str = "AUTH_FAILED",
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(message, code, status_code=401, details=details)


class InvalidCredentialsException(AuthenticationException):
    """无效凭证异常"""

    def __init__(
        self,
        message: str = "Invalid username or password",
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(message, code="INVALID_CREDENTIALS", details=details)


class TokenExpiredException(AuthenticationException):
    """Token 过期异常"""

    def __init__(
        self,
        message: str = "Token has expired",
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(message, code="TOKEN_EXPIRED", details=details)


class InvalidTokenException(AuthenticationException):
    """无效 Token 异常"""

    def __init__(
        self,
        message: str = "Invalid token",
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(message, code="INVALID_TOKEN", details=details)


class PermissionDeniedException(AuthenticationException):
    """权限不足异常"""

    def __init__(
        self,
        message: str = "Permission denied",
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(message, code="PERMISSION_DENIED", status_code=403, details=details)


# ==================== 用户异常 ====================


class UserNotFoundException(AppException):
    """用户不存在异常"""

    def __init__(
        self,
        user_id: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        message = f"User {user_id} not found" if user_id else "User not found"
        super().__init__(message, code="USER_NOT_FOUND", status_code=404, details=details)


class UserExistsException(AppException):
    """用户已存在异常"""

    def __init__(
        self,
        field: str = "email",
        value: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        message = f"User with this {field} already exists"
        if value:
            message = f"User with {field} '{value}' already exists"
        super().__init__(message, code="USER_EXISTS", details=details)


class InvalidPasswordException(AppException):
    """无效密码异常"""

    def __init__(
        self,
        message: str = "Invalid password",
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(message, code="INVALID_PASSWORD", details=details)


# ==================== 客户异常 ====================


class CustomerNotFoundException(AppException):
    """客户不存在异常"""

    def __init__(
        self,
        customer_id: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        message = f"Customer {customer_id} not found" if customer_id else "Customer not found"
        super().__init__(message, code="CUSTOMER_NOT_FOUND", status_code=404, details=details)


class DuplicateCustomerException(AppException):
    """重复客户异常"""

    def __init__(
        self,
        field: str = "email",
        value: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        message = f"Customer with this {field} already exists"
        if value:
            message = f"Customer with {field} '{value}' already exists"
        super().__init__(message, code="DUPLICATE_CUSTOMER", status_code=409, details=details)


class InvalidEmailException(AppException):
    """无效邮箱异常"""

    def __init__(
        self,
        email: str,
        details: Optional[dict[str, Any]] = None,
    ):
        message = f"Invalid email: {email}"
        super().__init__(message, code="INVALID_EMAIL", details=details)


# ==================== 邮件异常 ====================


class EmailServiceException(AppException):
    """邮件服务异常"""

    def __init__(
        self,
        message: str = "Failed to send email",
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(message, code="EMAIL_SEND_FAILED", details=details)


class EmailTemplateNotFoundException(AppException):
    """邮件模板不存在异常"""

    def __init__(
        self,
        template_id: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        message = (
            f"Email template {template_id} not found" if template_id else "Email template not found"
        )
        super().__init__(message, code="TEMPLATE_NOT_FOUND", status_code=404, details=details)


# ==================== 数据采集异常 ====================


class ScrapingException(AppException):
    """数据采集异常"""

    def __init__(
        self,
        message: str = "Scraping failed",
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(message, code="SCRAPING_FAILED", details=details)


class ScrapingTaskNotFoundException(AppException):
    """采集任务不存在异常"""

    def __init__(
        self,
        task_id: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ):
        message = f"Scraping task {task_id} not found" if task_id else "Scraping task not found"
        super().__init__(message, code="SCRAPING_TASK_NOT_FOUND", status_code=404, details=details)


# ==================== 验证异常 ====================


class ValidationException(AppException):
    """验证异常"""

    def __init__(
        self,
        message: str = "Validation failed",
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(message, code="VALIDATION_ERROR", details=details)


# ==================== 数据库异常 ====================


class DatabaseException(AppException):
    """数据库异常"""

    def __init__(
        self,
        message: str = "Database operation failed",
        details: Optional[dict[str, Any]] = None,
    ):
        super().__init__(message, code="DATABASE_ERROR", status_code=500, details=details)
