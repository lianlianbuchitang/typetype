"""api_client 模块测试。"""

from src.backend.core.api_client import ApiClient


class DummyResponse:
    """模拟响应对象。"""

    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


class DummyHttpClient:
    """模拟 httpx.Client。"""

    def __init__(self, payload=None, should_raise=False):
        self._payload = payload or {}
        self._should_raise = should_raise
        self.last_call = None
        self.closed = False

    def request(self, method, url, params=None, json=None, data=None, headers=None):
        if self._should_raise:
            raise RuntimeError("network error")
        self.last_call = {
            "method": method,
            "url": url,
            "params": params,
            "json": json,
            "data": data,
            "headers": headers,
        }
        return DummyResponse(self._payload)

    def close(self):
        self.closed = True


def _build_api_client_with_dummy(dummy: DummyHttpClient) -> ApiClient:
    """构造 ApiClient 并注入假客户端，避免依赖真实网络环境。"""
    client = ApiClient.__new__(ApiClient)
    client._timeout = 20.0
    client._client = dummy
    return client


def test_request_success():
    """request 成功时应返回 JSON 并透传参数。"""
    dummy = DummyHttpClient(payload={"ok": True})
    client = _build_api_client_with_dummy(dummy)

    result = client.request(
        "POST",
        "https://example.com/api",
        params={"p": 1},
        json={"a": 1},
        data={"b": 2},
        headers={"X-Test": "1"},
    )

    assert result == {"ok": True}
    assert dummy.last_call == {
        "method": "POST",
        "url": "https://example.com/api",
        "params": {"p": 1},
        "json": {"a": 1},
        "data": {"b": 2},
        "headers": {"X-Test": "1"},
    }


def test_get_json_success():
    """get_json 应使用 GET 并返回 JSON。"""
    dummy = DummyHttpClient(payload={"msg": "hello"})
    client = _build_api_client_with_dummy(dummy)

    result = client.get_json("https://example.com/get", params={"q": "k"})

    assert result == {"msg": "hello"}
    assert dummy.last_call["method"] == "GET"
    assert dummy.last_call["url"] == "https://example.com/get"
    assert dummy.last_call["params"] == {"q": "k"}
    assert dummy.last_call["json"] is None


def test_post_json_success():
    """post_json 应使用 POST 并传递 json。"""
    dummy = DummyHttpClient(payload={"code": 0})
    client = _build_api_client_with_dummy(dummy)

    result = client.post_json("https://example.com/post", {"x": 1})

    assert result == {"code": 0}
    assert dummy.last_call["method"] == "POST"
    assert dummy.last_call["url"] == "https://example.com/post"
    assert dummy.last_call["json"] == {"x": 1}


def test_request_exception_returns_none():
    """request 异常时应返回 None。"""
    client = _build_api_client_with_dummy(DummyHttpClient(should_raise=True))

    result = client.request("GET", "https://example.com/error")

    assert result is None


def test_close_calls_underlying_client():
    """close 应关闭底层客户端。"""
    dummy = DummyHttpClient()
    client = _build_api_client_with_dummy(dummy)

    client.close()

    assert dummy.closed is True
