from dataclasses import dataclass

from ..ports.text_provider import TextProvider
from ..ports.local_text_loader import LocalTextLoader
from ..ports.clipboard import ClipboardReader
from ...models.config.text_source_config import TextSourceEntry


@dataclass
class LoadTextResult:
    success: bool
    text: str
    error_message: str = ""


class LoadTextUseCase:
    def __init__(
        self,
        text_provider: TextProvider,
        local_text_loader: LocalTextLoader,
        clipboard_reader: ClipboardReader,
    ):
        self._text_provider = text_provider
        self._local_text_loader = local_text_loader
        self._clipboard_reader = clipboard_reader

    def load_from_source(self, source: TextSourceEntry) -> LoadTextResult:
        if source.local_path:
            return self._load_from_local(source.local_path)
        else:
            text = self._text_provider.fetch_text_by_key(source.key)
            if text is None:
                return LoadTextResult(
                    success=False,
                    text="",
                    error_message=f"无法获取文本内容({source.key})",
                )
            return LoadTextResult(success=True, text=text)

    def _load_from_local(self, path: str | None) -> LoadTextResult:
        if not path:
            return LoadTextResult(
                success=False, text="", error_message="本地来源缺少路径"
            )
        text = self._local_text_loader.load_text(path)
        if text is None:
            return LoadTextResult(
                success=False, text="", error_message="无法读取本地文章"
            )
        return LoadTextResult(success=True, text=text)

    def load_from_clipboard(self) -> LoadTextResult:
        text = self._clipboard_reader.text()
        if not text:
            return LoadTextResult(
                success=False, text="", error_message="当前剪贴板无文本内容"
            )
        return LoadTextResult(success=True, text=text)
