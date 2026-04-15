"""text_uploader 模块测试。"""

from unittest.mock import MagicMock

from src.backend.integration.text_uploader import NoopTextUploader, TextUploader


# ---------------------------------------------------------------------------
# TextUploader 测试（mock ApiClient）
# ---------------------------------------------------------------------------


class TestTextUploader:
    """TextUploader 应正确处理上传逻辑和异常响应。"""

    def _make_uploader(self, token: str = "valid_token"):
        api_client = MagicMock()
        uploader = TextUploader(
            api_client=api_client,
            upload_url="https://example.com/api/v1/texts/upload",
            token_provider=lambda: token,
        )
        return uploader, api_client

    def test_upload_success(self):
        uploader, api_client = self._make_uploader()
        api_client.request.return_value = {"code": 200, "data": {"id": 123}}

        result = uploader.upload(content="hello", title="T", source_key="src")
        assert result == 123

        call_kwargs = api_client.request.call_args
        assert call_kwargs[0] == ("POST", "https://example.com/api/v1/texts/upload")
        assert call_kwargs[1]["json"] == {
            "content": "hello",
            "title": "T",
            "sourceKey": "src",
        }
        assert call_kwargs[1]["headers"] == {"Authorization": "Bearer valid_token"}

    def test_upload_no_token_returns_none(self):
        uploader, api_client = self._make_uploader(token="")

        result = uploader.upload(content="hello", title="T", source_key="src")
        assert result is None
        api_client.request.assert_not_called()

    def test_upload_api_returns_none(self):
        uploader, api_client = self._make_uploader()
        api_client.request.return_value = None

        result = uploader.upload(content="hello", title="T", source_key="src")
        assert result is None

    def test_upload_server_returns_non_200(self):
        uploader, api_client = self._make_uploader()
        api_client.request.return_value = {"code": 403, "message": "forbidden"}

        result = uploader.upload(content="hello", title="T", source_key="src")
        assert result is None

    def test_upload_data_format_invalid(self):
        uploader, api_client = self._make_uploader()
        # code 200 但 data 不是 dict
        api_client.request.return_value = {"code": 200, "data": "bad format"}

        result = uploader.upload(content="hello", title="T", source_key="src")
        assert result is None

    def test_upload_data_missing_id(self):
        uploader, api_client = self._make_uploader()
        api_client.request.return_value = {"code": 200, "data": {"not_id": 1}}

        result = uploader.upload(content="hello", title="T", source_key="src")
        # data 是 dict 但没有 id 字段，get("id") 返回 None
        assert result is None


# ---------------------------------------------------------------------------
# NoopTextUploader 测试
# ---------------------------------------------------------------------------


class TestNoopTextUploader:
    """NoopTextUploader 始终返回 None。"""

    def test_upload_returns_none(self):
        uploader = NoopTextUploader()
        result = uploader.upload(content="any", title="any", source_key="any")
        assert result is None
