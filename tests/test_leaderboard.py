"""leaderboard_gateway 和 leaderboard_fetcher 模块测试。"""

from unittest.mock import MagicMock

from src.backend.application.gateways.leaderboard_gateway import LeaderboardGateway
from src.backend.integration.leaderboard_fetcher import LeaderboardFetcher


# ---------------------------------------------------------------------------
# LeaderboardGateway 测试（mock LeaderboardProvider）
# ---------------------------------------------------------------------------


class TestLeaderboardGateway:
    """LeaderboardGateway 应透传 LeaderboardProvider 的返回值。"""

    def _make_gateway(self):
        provider = MagicMock()
        gateway = LeaderboardGateway(leaderboard_provider=provider)
        return gateway, provider

    def test_get_catalog_returns_data(self):
        gateway, provider = self._make_gateway()
        expected = [{"sourceKey": "a", "label": "A"}]
        provider.get_catalog.return_value = expected

        result = gateway.get_catalog()
        assert result == expected
        provider.get_catalog.assert_called_once()

    def test_get_catalog_returns_none(self):
        gateway, provider = self._make_gateway()
        provider.get_catalog.return_value = None

        result = gateway.get_catalog()
        assert result is None

    def test_get_latest_text_by_source(self):
        gateway, provider = self._make_gateway()
        expected = {"id": 1, "content": "hello"}
        provider.get_latest_text_by_source.return_value = expected

        result = gateway.get_latest_text_by_source("jisubei")
        assert result == expected
        provider.get_latest_text_by_source.assert_called_once_with("jisubei")

    def test_get_texts_by_source(self):
        gateway, provider = self._make_gateway()
        expected = [{"id": 1, "title": "T1"}, {"id": 2, "title": "T2"}]
        provider.get_texts_by_source.return_value = expected

        result = gateway.get_texts_by_source("jisubei")
        assert result == expected
        provider.get_texts_by_source.assert_called_once_with("jisubei")

    def test_get_text_by_id(self):
        gateway, provider = self._make_gateway()
        expected = {"id": 42, "content": "text"}
        provider.get_text_by_id.return_value = expected

        result = gateway.get_text_by_id(42)
        assert result == expected
        provider.get_text_by_id.assert_called_once_with(42)

    def test_get_leaderboard_with_pagination(self):
        gateway, provider = self._make_gateway()
        expected = {"records": [], "total": 0, "page": 2, "size": 10}
        provider.get_leaderboard.return_value = expected

        result = gateway.get_leaderboard(text_id=7, page=2, size=10)
        assert result == expected
        provider.get_leaderboard.assert_called_once_with(7, 2, 10)

    def test_get_leaderboard_default_pagination(self):
        gateway, provider = self._make_gateway()
        provider.get_leaderboard.return_value = {"records": []}

        gateway.get_leaderboard(text_id=1)
        provider.get_leaderboard.assert_called_once_with(1, 1, 50)


# ---------------------------------------------------------------------------
# LeaderboardFetcher 测试（mock ApiClient）
# ---------------------------------------------------------------------------


class TestLeaderboardFetcher:
    """LeaderboardFetcher 应正确调用 api_client 并解析响应。"""

    def _make_fetcher(self, token: str = ""):
        api_client = MagicMock()
        api_client.last_error = None  # 默认无网络错误
        fetcher = LeaderboardFetcher(
            api_client=api_client,
            base_url="https://example.com",
            token_provider=lambda: token,
        )
        return fetcher, api_client

    # get_catalog

    def test_get_catalog_success(self):
        fetcher, api_client = self._make_fetcher()
        api_client.request.return_value = {"data": [{"sourceKey": "a", "label": "A"}]}

        result = fetcher.get_catalog()
        assert result == [{"sourceKey": "a", "label": "A"}]

    def test_get_catalog_api_returns_none(self):
        fetcher, api_client = self._make_fetcher()
        api_client.request.return_value = None

        result = fetcher.get_catalog()
        assert result is None

    def test_get_catalog_response_not_dict(self):
        fetcher, api_client = self._make_fetcher()
        api_client.request.return_value = "unexpected"

        result = fetcher.get_catalog()
        assert result is None

    def test_get_catalog_data_not_list(self):
        fetcher, api_client = self._make_fetcher()
        api_client.request.return_value = {"data": "not a list"}

        result = fetcher.get_catalog()
        assert result is None

    # get_latest_text_by_source

    def test_get_latest_text_by_source_success(self):
        fetcher, api_client = self._make_fetcher()
        expected = {"id": 1, "content": "hello"}
        api_client.request.return_value = {"data": expected}

        result = fetcher.get_latest_text_by_source("jisubei")
        assert result == expected

    def test_get_latest_text_by_source_failure(self):
        fetcher, api_client = self._make_fetcher()
        api_client.request.return_value = None

        result = fetcher.get_latest_text_by_source("jisubei")
        assert result is None

    # get_texts_by_source

    def test_get_texts_by_source_success(self):
        fetcher, api_client = self._make_fetcher()
        api_client.request.return_value = {"data": [{"id": 1}, {"id": 2}]}

        result = fetcher.get_texts_by_source("jisubei")
        assert result == [{"id": 1}, {"id": 2}]

    def test_get_texts_by_source_failure(self):
        fetcher, api_client = self._make_fetcher()
        api_client.request.return_value = None

        result = fetcher.get_texts_by_source("jisubei")
        assert result is None

    # get_text_by_id

    def test_get_text_by_id_success(self):
        fetcher, api_client = self._make_fetcher()
        api_client.request.return_value = {"data": {"id": 42, "content": "t"}}

        result = fetcher.get_text_by_id(42)
        assert result == {"id": 42, "content": "t"}

    def test_get_text_by_id_failure(self):
        fetcher, api_client = self._make_fetcher()
        api_client.request.return_value = None

        result = fetcher.get_text_by_id(42)
        assert result is None

    # get_leaderboard

    def test_get_leaderboard_success(self):
        fetcher, api_client = self._make_fetcher()
        data = {"records": [{"rank": 1}], "total": 1}
        api_client.request.return_value = {"data": data}

        result = fetcher.get_leaderboard(text_id=7, page=2, size=10)
        assert result == {
            "leaderboard": [{"rank": 1}],
            "total": 1,
            "text_info": None,
        }
        call_kwargs = api_client.request.call_args
        assert call_kwargs[1]["params"] == {"page": 2, "size": 10}

    def test_get_leaderboard_failure(self):
        fetcher, api_client = self._make_fetcher()
        api_client.request.return_value = None

        result = fetcher.get_leaderboard(text_id=7)
        assert result is None

    # _get_auth_headers

    def test_auth_headers_with_token(self):
        fetcher, _ = self._make_fetcher(token="abc123")
        headers = fetcher._get_auth_headers()
        assert headers == {"Authorization": "Bearer abc123"}

    def test_auth_headers_without_token(self):
        fetcher, _ = self._make_fetcher(token="")
        headers = fetcher._get_auth_headers()
        assert headers == {}
