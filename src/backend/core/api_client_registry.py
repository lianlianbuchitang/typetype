from .api_client import ApiClient

_api_client: ApiClient | None = None


def set_api_client(api_client: ApiClient) -> None:
    """设置全局 ApiClient。"""
    global _api_client
    _api_client = api_client


def get_api_client() -> ApiClient:
    """获取全局 ApiClient。"""
    if _api_client is None:
        raise RuntimeError("ApiClient 尚未初始化，请先调用 set_api_client")
    return _api_client
