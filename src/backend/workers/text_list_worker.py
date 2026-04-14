"""文本列表加载 Worker - 在后台线程执行网络请求。"""

from typing import Any

from ..application.gateways.leaderboard_gateway import LeaderboardGateway
from .base_worker import BaseWorker


class TextListWorker(BaseWorker):
    """文本列表加载 Worker - 在后台线程执行网络请求。"""

    def __init__(
        self,
        leaderboard_gateway: LeaderboardGateway,
        source_key: str,
    ):
        self._leaderboard_gateway = leaderboard_gateway
        self._source_key = source_key
        super().__init__(task=self._fetch_text_list, error_prefix="加载文本列表失败")

    def _fetch_text_list(self) -> dict[str, Any]:
        """获取来源下的文本列表。"""
        texts = self._leaderboard_gateway.get_texts_by_source(self._source_key)
        if texts is None:
            raise Exception(f"无法获取 {self._source_key} 的文本列表")

        return {
            "source_key": self._source_key,
            "texts": texts,
        }
