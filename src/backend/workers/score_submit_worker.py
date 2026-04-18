"""成绩提交 Worker - 在后台线程执行网络请求。"""

from ..models.entity.session_stat import SessionStat
from ..ports.score_submitter import ScoreSubmitter
from .base_worker import BaseWorker


class ScoreSubmitWorker(BaseWorker):
    """成绩提交 Worker - 在后台线程执行 HTTP POST，避免阻塞 UI 主线程。"""

    def __init__(
        self,
        score_submitter: ScoreSubmitter,
        score_data: SessionStat,
        text_id: int,
    ):
        self._score_submitter = score_submitter
        self._score_data = score_data
        self._text_id = text_id
        super().__init__(task=self._submit, error_prefix="提交成绩失败")

    def _submit(self) -> bool:
        """在后台线程中提交成绩。"""
        return self._score_submitter.submit(
            self._score_data,
            text_id=self._text_id,
        )
