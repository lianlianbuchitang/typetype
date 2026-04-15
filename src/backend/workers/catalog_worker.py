"""目录加载 Worker - 在后台线程执行网络请求。"""

from ..application.gateways.leaderboard_gateway import LeaderboardGateway
from .base_worker import BaseWorker


class CatalogWorker(BaseWorker):
    """目录加载 Worker - 在后台线程执行网络请求。"""

    def __init__(self, leaderboard_gateway: LeaderboardGateway):
        self._leaderboard_gateway = leaderboard_gateway
        super().__init__(task=self._fetch_catalog, error_prefix="加载目录失败")

    def _fetch_catalog(self) -> list[dict]:
        """获取文本来源目录。"""
        catalog = self._leaderboard_gateway.get_catalog()
        if catalog is None:
            raise Exception("无法获取文本来源目录")
        return catalog
