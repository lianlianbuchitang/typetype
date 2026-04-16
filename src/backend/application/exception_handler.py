"""全局异常处理器。

将基础设施层异常（网络错误等）转换为用户友好的提示消息。
类似于 Spring Boot 的 @ControllerAdvice / @RestControllerAdvice。

使用方式：
    from src.backend.application.exception_handler import GlobalExceptionHandler
    msg = GlobalExceptionHandler.handle(exception)
"""

from ..infrastructure.network_errors import (
    CatalogServiceError,
    NetworkDecodeError,
    NetworkHttpStatusError,
    NetworkRequestError,
    NetworkTimeoutError,
    SubmitScoreError,
)

# 异常 → 用户消息映射（可扩展，新增异常类型时在此添加）
_EXCEPTION_MESSAGE_MAP: dict[type[Exception], str] = {
    NetworkTimeoutError: "网络连接超时，请检查网络后重试",
    NetworkRequestError: "网络请求失败，请检查网络连接",
    NetworkDecodeError: "服务器响应异常，请稍后重试",
    SubmitScoreError: "提交成绩失败，请稍后重试",
    CatalogServiceError: "文本库服务异常，请稍后重试",
    IOError: "文件读取失败，请检查文件是否存在",
}


class GlobalExceptionHandler:
    """全局异常处理器。"""

    @staticmethod
    def handle(exc: Exception) -> str:
        """将异常转换为用户可读消息。"""
        msg = _EXCEPTION_MESSAGE_MAP.get(type(exc))
        if msg is not None:
            if isinstance(exc, NetworkHttpStatusError):
                return f"服务器状态异常({exc.status_code})"
            return msg
        return str(exc)
