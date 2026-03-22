from collections.abc import Callable
from typing import Any

from PySide6.QtCore import QObject, QRunnable, Signal, Slot

from ..application.exception_handler import GlobalExceptionHandler


class WorkerSignals(QObject):
    succeeded = Signal(object)
    failed = Signal(str)
    finished = Signal()


class BaseWorker(QRunnable):
    def __init__(self, task: Callable[[], Any], error_prefix: str = "任务执行失败"):
        super().__init__()
        self._task = task
        self._error_prefix = error_prefix
        self.signals = WorkerSignals()

    @Slot()
    def run(self) -> None:
        try:
            result = self._task()
            self.signals.succeeded.emit(result)
        except Exception as e:
            msg = GlobalExceptionHandler.handle(e)
            self.signals.failed.emit(f"{self._error_prefix}：{msg}")
        finally:
            self.signals.finished.emit()
