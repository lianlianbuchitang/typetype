from typing import Any

import httpx


class ApiClient:
    """通用 HTTP 客户端，集中处理请求和异常。"""

    def __init__(self, timeout: float = 20.0):
        self._timeout = timeout
        self._client = httpx.Client(timeout=self._timeout)

    def request(
        self,
        method: str,
        url: str,
        *,
        params: dict[Any, Any] | None = None,
        json: dict[Any, Any] | None = None,
        data: dict[Any, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any] | None:
        """
        发送通用 HTTP 请求并解析 JSON 响应。

        参数:
            method: HTTP 方法，如 GET/POST
            url: 请求地址
            params: 查询参数
            json: JSON 请求体
            data: 表单请求体
            headers: 请求头

        返回:
            解析后的 JSON 字典；失败时返回 None
        """
        try:
            response = self._client.request(
                method=method,
                url=url,
                params=params,
                json=json,
                data=data,
                headers=headers,
            )
            return response.json()
        except Exception as e:
            print(f"请求发生错误: {e}")
            return None

    def get_json(
        self, url: str, params: dict[Any, Any] | None = None
    ) -> dict[str, Any] | None:
        """
        发送 GET 请求并解析 JSON 响应。

        参数:
            url: 请求地址
            params: 查询参数

        返回:
            解析后的 JSON 字典；失败时返回 None
        """
        return self.request("GET", url, params=params)

    def post_json(self, url: str, payload: dict[Any, Any]) -> dict[str, Any] | None:
        """
        发送 POST JSON 请求。

        参数:
            url: 请求地址
            payload: JSON 请求体

        返回:
            解析后的 JSON 字典；失败时返回 None
        """
        return self.request("POST", url, json=payload)

    def close(self) -> None:
        """关闭 HTTP 客户端并释放连接资源。"""
        self._client.close()
