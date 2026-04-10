from ..application.usecases.load_text_usecase import (
    LoadTextResult,
    LoadTextUseCase,
    TextLoadPlan,
)
from .base_worker import BaseWorker


class TextLoadWorker(BaseWorker):
    """文本加载 Worker - 在后台线程执行网络请求。"""

    def __init__(self, load_text_usecase: LoadTextUseCase, plan: TextLoadPlan):
        self._load_text_usecase = load_text_usecase
        self._plan = plan
        super().__init__(task=self._load_text, error_prefix="加载文本失败")

    def _load_text(self) -> LoadTextResult:
        """在后台线程中加载文本，返回完整的 LoadTextResult。"""
        result = self._load_text_usecase.load(self._plan)
        if result.success:
            return result
        raise Exception(result.error_message)
