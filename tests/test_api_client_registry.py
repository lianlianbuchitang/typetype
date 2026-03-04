"""api_client_registry 模块测试。"""

from src.backend.core.api_client import ApiClient
from src.backend.core import api_client_registry as registry_module
from src.backend.core.api_client_registry import get_api_client, set_api_client


def _dummy_api_client() -> ApiClient:
    """构造空 ApiClient 对象用于注册测试。"""
    client = ApiClient.__new__(ApiClient)
    return client


def test_get_api_client_without_init_raises():
    """未初始化时读取 ApiClient 应报错。"""
    original = registry_module._api_client
    try:
        registry_module._api_client = None
        try:
            get_api_client()
            assert False, "expected RuntimeError"
        except RuntimeError:
            pass
    finally:
        registry_module._api_client = original


def test_set_and_get_api_client():
    """设置后应读取到同一 ApiClient 实例。"""
    original = registry_module._api_client
    client = _dummy_api_client()

    try:
        set_api_client(client)
        current = get_api_client()
        assert current is client
    finally:
        registry_module._api_client = original
