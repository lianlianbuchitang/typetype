"""排行榜数据获取器。"""

from collections.abc import Callable
from typing import Any

from ..infrastructure.api_client import ApiClient
from ..utils.logger import log_warning


class LeaderboardFetcher:
    """排行榜数据获取器，从服务器获取排行榜数据。"""

    def __init__(
        self,
        api_client: ApiClient,
        base_url: str,
        token_provider: Callable[[], str] = lambda: "",
    ):
        self._api_client = api_client
        self._base_url = base_url
        self._token_provider = token_provider

    def _get_auth_headers(self) -> dict[str, str]:
        token = self._token_provider()
        if token:
            return {"Authorization": f"Bearer {token}"}
        return {}

    def get_catalog(self) -> list[dict[str, Any]] | None:
        """获取服务端文本来源目录。

        Returns:
            来源列表，每个元素包含 sourceKey, label 等字段，失败返回 None
        """
        url = f"{self._base_url}/api/v1/texts/catalog"
        response = self._api_client.request(
            "GET", url, headers=self._get_auth_headers()
        )
        if response is None:
            log_warning("[LeaderboardFetcher] 获取文本来源目录失败")
            return None
        if isinstance(response, dict):
            data = response.get("data")
            if isinstance(data, list):
                return data
        return None

    def get_latest_text_by_source(self, source_key: str) -> dict[str, Any] | None:
        """获取指定来源的最新文本。

        Args:
            source_key: 文本来源标识，如 "jisubei"

        Returns:
            包含 id, content, title 等字段的字典，失败返回 None
        """
        url = f"{self._base_url}/api/v1/texts/latest/{source_key}"
        response = self._api_client.request(
            "GET", url, headers=self._get_auth_headers()
        )
        if response is None:
            log_warning(f"[LeaderboardFetcher] 获取最新文本失败: {source_key}")
            return None
        if isinstance(response, dict):
            data = response.get("data")
            if isinstance(data, dict):
                return data
        return None

    def get_texts_by_source(self, source_key: str) -> list[dict[str, Any]] | None:
        """获取来源下所有文本的摘要列表。

        Args:
            source_key: 文本来源标识，如 "jisubei"

        Returns:
            文本摘要列表，每个元素包含 id, title 等字段，失败返回 None
        """
        url = f"{self._base_url}/api/v1/texts/by-source/{source_key}"
        response = self._api_client.request(
            "GET", url, headers=self._get_auth_headers()
        )
        if response is None:
            log_warning(f"[LeaderboardFetcher] 获取文本列表失败: {source_key}")
            return None
        if isinstance(response, dict):
            data = response.get("data")
            if isinstance(data, list):
                return data
        return None

    def get_text_by_id(self, text_id: int) -> dict[str, Any] | None:
        """通过文本 ID 获取文本详情。

        Args:
            text_id: 文本 ID

        Returns:
            包含 id, content, title 等字段的字典，失败返回 None
        """
        url = f"{self._base_url}/api/v1/texts/{text_id}"
        response = self._api_client.request(
            "GET", url, headers=self._get_auth_headers()
        )
        if response is None:
            log_warning(f"[LeaderboardFetcher] 获取文本详情失败: text_id={text_id}")
            return None
        if isinstance(response, dict):
            data = response.get("data")
            if isinstance(data, dict):
                return data
        return None

    def get_leaderboard(
        self, text_id: int, page: int = 1, size: int = 50
    ) -> dict[str, Any] | None:
        """获取指定文本的排行榜。

        Args:
            text_id: 文本ID
            page: 页码（从1开始）
            size: 每页大小

        Returns:
            包含 records, total, page, size 等字段的分页数据，失败返回 None
        """
        url = f"{self._base_url}/api/v1/texts/{text_id}/leaderboard"
        response = self._api_client.request(
            "GET",
            url,
            params={"page": page, "size": size},
            headers=self._get_auth_headers(),
        )
        if response is None:
            log_warning(f"[LeaderboardFetcher] 获取排行榜失败: text_id={text_id}")
            return None
        if isinstance(response, dict):
            data = response.get("data")
            if isinstance(data, dict):
                return data
        return None
