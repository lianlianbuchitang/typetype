from .runtime_config import RuntimeConfig

_runtime_config: RuntimeConfig | None = None


def set_runtime_config(config: RuntimeConfig) -> None:
    """设置全局运行时配置。"""
    global _runtime_config
    _runtime_config = config


def get_runtime_config() -> RuntimeConfig:
    """获取当前运行时配置。"""
    if _runtime_config is None:
        raise RuntimeError("RuntimeConfig 尚未初始化，请先调用 set_runtime_config")
    return _runtime_config
