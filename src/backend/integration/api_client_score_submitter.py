"""基于 ApiClient 的成绩提交实现。"""

from collections.abc import Callable
from typing import Any

from ..infrastructure.api_client import ApiClient
from ..models.entity.session_stat import SessionStat
from ..utils.logger import log_warning


class ApiClientScoreSubmitter:
    """通过 HTTP API 提交成绩到 Spring Boot 后端。

    服务端一站式 findOrCreate：客户端把 content + sourceKey 一起发给服务端，
    服务端在 ScoreService.submitScore() 中完成"查找或创建文本 + 记录成绩"。
    """

    def __init__(
        self,
        api_client: ApiClient,
        submit_url: str,
        token_provider: Callable[[], str] = lambda: "",
    ):
        self._api_client = api_client
        self._submit_url = submit_url
        self._token_provider = token_provider

    def submit(
        self,
        score_data: SessionStat,
        text_content: str = "",
        source_key: str = "",
        text_title: str = "",
    ) -> bool:
        """提交成绩到服务器。

        Args:
            score_data: 会话统计数据
            text_content: 文本内容（用于服务端 findOrCreate）
            source_key: 文本来源 key（用于服务端 findOrCreate）
            text_title: 文本标题

        Returns:
            bool: 提交是否成功
        """
        token = self._token_provider()
        if not token:
            log_warning("[ScoreSubmitter] 无法提交成绩：未登录")
            return False

        payload = self._build_payload(score_data, text_content, source_key)
        headers = {"Authorization": f"Bearer {token}"}

        data = self._api_client.request(
            "POST",
            self._submit_url,
            json=payload,
            headers=headers,
        )

        return self._parse_response(data)

    def _build_payload(
        self,
        score_data: SessionStat,
        text_content: str,
        source_key: str,
    ) -> dict[str, Any]:
        """构建请求体。"""
        payload = {
            "speed": round(score_data.speed, 2),
            "effectiveSpeed": round(score_data.effectiveSpeed, 2),
            "keyStroke": round(score_data.keyStroke, 2),
            "codeLength": round(score_data.codeLength, 4),
            "accuracyRate": round(score_data.accuracy, 2),
            "charCount": score_data.char_count,
            "wrongCharCount": score_data.wrong_char_count,
            "duration": round(score_data.time, 2),
        }
        if text_content:
            payload["textContent"] = text_content
        if source_key:
            payload["sourceKey"] = source_key
        return payload

    def _parse_response(
        self,
        data: dict[str, Any] | None,
    ) -> bool:
        """解析响应。"""
        if data is None:
            log_warning(
                f"[ScoreSubmitter] 提交失败: {self._api_client.last_error or '网络错误'}"
            )
            return False

        code = data.get("code")
        if code == 200:
            return True

        log_warning(f"[ScoreSubmitter] 提交失败: {data.get('message', '未知错误')}")
        return False


class NoopScoreSubmitter:
    """空实现，用于未登录或禁用提交场景。"""

    def submit(
        self,
        score_data: SessionStat,
        text_content: str = "",
        source_key: str = "",
        text_title: str = "",
    ) -> bool:
        return False
