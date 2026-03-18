from datetime import datetime

from PySide6.QtCore import QObject, QTimer, Signal
from PySide6.QtGui import QColor, QTextCharFormat, QTextCursor
from PySide6.QtQuick import QQuickTextDocument

from ..application.usecases.score_usecase import ScoreUseCase
from ..typing.score_data import ScoreData


class TypingService(QObject):
    """打字统计领域服务。

    负责：
    - ScoreData 状态管理
    - 计时器控制（开始/停止/累积）
    - 键数/字数统计
    - 文本上色逻辑
    - 历史记录构建
    """

    # 信号：供 Bridge 转发到 QML
    typeSpeedChanged = Signal()
    keyStrokeChanged = Signal()
    codeLengthChanged = Signal()
    charNumChanged = Signal()
    totalTimeChanged = Signal()
    typingEnded = Signal()
    readOnlyChanged = Signal()
    historyRecordUpdated = Signal(dict)

    def __init__(self, score_usecase: ScoreUseCase, time_interval: float = 0.15):
        super().__init__()
        self._score_data = ScoreData(
            time=0.0,
            key_stroke_count=0,
            char_count=0,
            wrong_char_count=0,
            date="",
        )
        self._score_usecase = score_usecase
        self.timeInterval = time_interval

        self._total_chars = 0
        self._start_status = False
        self._text_read_only = False  # LowerPane 只读状态：打字中可编辑，打印完只读
        self._wrong_char_prefix_sum: list[int] = []

        # 文本上色相关
        self._rich_doc = None
        self._cursor = None
        self._plain_doc = ""
        self._no_fmt = QTextCharFormat()
        self._correct_fmt = QTextCharFormat()
        self._error_fmt = QTextCharFormat()
        self._match_color_format()

        # 秒数累积计时器
        self._second_timer = QTimer()
        self._second_timer.timeout.connect(self._accumulate_time)
        self._second_timer.setInterval(int(self.timeInterval * 1000))

    def _set_read_only(self, status: bool) -> None:
        if self._text_read_only != status:
            self._text_read_only = status
            self.readOnlyChanged.emit()

    def _match_color_format(self) -> None:
        """配置文字背景色"""
        self._no_fmt.setBackground(QColor("transparent"))
        self._correct_fmt.setBackground(QColor("gray"))
        self._error_fmt.setBackground(QColor("red"))

    def _color_text(self, beginPos: int, n: int, fmt: QTextCharFormat) -> None:
        """给文本上色"""
        if self._cursor and self._rich_doc:
            self._cursor.setPosition(beginPos)
            self._cursor.movePosition(
                QTextCursor.MoveOperation.Right, QTextCursor.KeepAnchor, n
            )
            self._cursor.setCharFormat(fmt)

    def _accumulate_key_num(self) -> None:
        """累积键数"""
        self._score_data.key_stroke_count += 1
        self.codeLengthChanged.emit()
        self.keyStrokeChanged.emit()

    def _accumulate_time(self) -> None:
        """累积时间"""
        self._score_data.time += self.timeInterval
        self.totalTimeChanged.emit()
        self.typeSpeedChanged.emit()
        self.keyStrokeChanged.emit()

    def _reset_score_data(self) -> None:
        """将成绩数据归零（不销毁对象）。

        注意：char_count 和 wrong_char_count 不在此处归零。
        它们由 handleCommittedText 触发更新对应方法隐式归零。
        若在此提前归零，QML 侧尚未完成的 onTextChanged 事件会以 char_count=0
        计算出负数 beginPos，导致 QTextCursor 越界。
        """
        self._score_data.time = 0.0
        self._score_data.key_stroke_count = 0
        self._score_data.date = ""

    def _get_new_record(self) -> dict:
        """获取新的记录"""
        self._score_data.date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return self._score_usecase.build_history_record(self._score_data)

    def _update_wrong_num(self, committedString: str, beginPos: int) -> None:
        """更新错字数"""
        for i in range(len(committedString)):
            if beginPos + i >= self._total_chars:
                break

            realPosition = beginPos + i
            pre_sum = 0
            newNotMatch = 0
            if realPosition > 0:
                pre_sum = self._wrong_char_prefix_sum[realPosition - 1]
            if committedString[i] != self._plain_doc[realPosition]:
                newNotMatch = 1

            self._wrong_char_prefix_sum[realPosition] = pre_sum + newNotMatch
            self._score_data.wrong_char_count = self._wrong_char_prefix_sum[
                realPosition
            ]

    def _update_current_char_num(
        self, committedString: str, growLength: int, beginPos: int
    ) -> None:
        """更新当前字数"""
        self._score_data.char_count += growLength
        self.charNumChanged.emit()

        self._update_wrong_num(committedString, beginPos)

        self.codeLengthChanged.emit()
        self.typeSpeedChanged.emit()
        self.keyStrokeChanged.emit()

        # 检查是否打完
        if self._score_data.char_count >= self._total_chars and self._start_status:
            self._stop()
            self._set_read_only(True)
            self.typingEnded.emit()
            self.historyRecordUpdated.emit(self._get_new_record())

    def _update_total_char_num(self, totalNum: int) -> None:
        """更新总字数"""
        self._total_chars = totalNum
        self._score_data.char_count = 0
        self._score_data.wrong_char_count = 0
        self._wrong_char_prefix_sum = [0 for _ in range(totalNum)]
        self.charNumChanged.emit()

    def _start(self) -> None:
        """开始打字"""
        self._second_timer.start()
        self._start_status = True

    def _stop(self) -> None:
        """停止打字"""
        self._second_timer.stop()
        self._start_status = False

    def _clear(self) -> None:
        """清空数据"""
        self._reset_score_data()
        self.codeLengthChanged.emit()
        self.keyStrokeChanged.emit()
        self.totalTimeChanged.emit()
        self.typeSpeedChanged.emit()

    # ── 对外公开的 Slot 方法（供 Bridge 调用） ──

    def handlePressed(self) -> None:
        """处理按键事件"""
        if self._start_status:
            self._accumulate_key_num()

    def handleCommittedText(self, s: str, growLength: int) -> None:
        """处理提交的文本(可能增也可能删)"""
        beginPos = self._score_data.char_count + growLength - len(s)
        self._update_current_char_num(s, growLength, beginPos)

        # 渲染变动文本
        for i in range(len(s)):
            if beginPos + i >= self._total_chars:
                break

            if s[i] == self._plain_doc[beginPos + i]:
                self._color_text(beginPos + i, 1, self._correct_fmt)
            else:
                self._color_text(beginPos + i, 1, self._error_fmt)

        if growLength < 0:
            char_count = self._score_data.char_count
            for i in range(char_count, char_count - growLength):
                self._color_text(i, 1, self._no_fmt)

    def handleLoadedText(self, quickDoc: QQuickTextDocument) -> None:
        """处理载文内容"""
        if quickDoc:
            self._rich_doc = quickDoc.textDocument()
            self._plain_doc = self._rich_doc.toPlainText()
            self._cursor = QTextCursor(self._rich_doc)
        self._update_total_char_num(len(self._plain_doc))
        self._clear()
        self._start_status = False

    def handleStartStatus(self, status: bool) -> None:
        if self._start_status != status:
            if status:
                self._clear()
                self._start()
            else:
                self._stop()
                self._clear()
        elif not status:
            self._clear()
        # 无论开始还是停止，都重置为可编辑状态
        self._set_read_only(False)

    # ==== 只读属性 ====
    @property
    def cursor_position(self) -> int:
        return self.score_data.char_count

    @property
    def text_read_only(self) -> bool:
        return self._text_read_only

    @property
    def score_data(self) -> ScoreData:
        return self._score_data

    @property
    def total_chars(self) -> int:
        return self._total_chars

    @property
    def is_started(self) -> bool:
        return self._start_status

    @property
    def type_speed(self) -> float:
        return self._score_data.speed

    @property
    def key_stroke(self) -> float:
        return self._score_data.keyStroke

    @property
    def code_length(self) -> float:
        return self._score_data.codeLength

    @property
    def wrong_num(self) -> int:
        return self._score_data.wrong_char_count

    @property
    def char_num(self) -> str:
        return f"{self._score_data.char_count}/{self._total_chars}"

    @property
    def total_time(self) -> float:
        return self._score_data.time

    def get_score_message(self) -> str:
        return self._score_usecase.build_score_message(self._score_data)

    def copy_score_message(self) -> None:
        self._score_usecase.copy_score_message(self._score_data)
