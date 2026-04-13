"""成绩提交协议。

定义成绩提交的抽象接口，供集成层实现。
"""

from typing import Protocol

from ..models.entity.session_stat import SessionStat


class ScoreSubmitter(Protocol):
    """成绩提交协议。

    实现：
    - ApiClientScoreSubmitter: 通过 HTTP API 提交到 Spring Boot 后端
    - NoopScoreSubmitter: 空实现，用于未登录或禁用提交场景
    """

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
        ...
