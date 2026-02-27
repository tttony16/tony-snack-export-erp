class AppError(Exception):
    """应用基础异常"""

    def __init__(self, code: int, message: str, detail: dict | None = None):
        self.code = code
        self.message = message
        self.detail = detail
        super().__init__(message)


class BusinessError(AppError):
    """业务规则异常（返回 422）"""

    pass


class NotFoundError(AppError):
    """资源不存在（返回 404）"""

    def __init__(self, resource: str, id: str):
        super().__init__(code=40400, message=f"{resource} {id} 不存在")


class PermissionDeniedError(AppError):
    """权限不足（返回 403）"""

    def __init__(self, message: str = "无权限执行此操作"):
        super().__init__(code=40301, message=message)


class ConflictError(AppError):
    """资源冲突（返回 409）"""

    pass
