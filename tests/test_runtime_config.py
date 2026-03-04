"""runtime_config_registry 模块测试。"""

from src.backend.config.runtime_config import RuntimeConfig
from src.backend.config.runtime_config_registry import get_runtime_config, set_runtime_config
from src.backend.config import runtime_config_registry as runtime_config_module


def test_get_runtime_config_without_init_raises():
    """未初始化时读取配置应报错。"""
    original = None
    try:
        try:
            original = get_runtime_config()
        except RuntimeError:
            original = None

        runtime_config_module._runtime_config = None
        try:
            get_runtime_config()
            assert False, "expected RuntimeError"
        except RuntimeError:
            pass
    finally:
        if original is not None:
            set_runtime_config(original)


def test_set_and_get_runtime_config():
    """设置后应能读取到同一配置对象。"""
    original = None
    try:
        original = get_runtime_config()
    except RuntimeError:
        original = None
    new_config = RuntimeConfig(
        text_source_url="https://example.com/api/text",
        api_timeout=10.0,
    )

    try:
        set_runtime_config(new_config)
        current = get_runtime_config()
        assert current is new_config
        assert current.text_source_url == "https://example.com/api/text"
        assert current.api_timeout == 10.0
    finally:
        if original is not None:
            set_runtime_config(original)
        else:
            runtime_config_module._runtime_config = None
