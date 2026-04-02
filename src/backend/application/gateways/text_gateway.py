from ...config.runtime_config import RuntimeConfig
from ...models.config.text_source_config import TextCatalogItem, TextSourceEntry
from ..ports.clipboard import ClipboardReader
from ..ports.local_text_loader import LocalTextLoader
from ..ports.text_provider import TextProvider


class TextGateway:
    def __init__(
        self,
        runtime_config: RuntimeConfig,
        clipboard: ClipboardReader,
        local_text_loader: LocalTextLoader,
        text_provider: TextProvider | None = None,
    ):
        self._runtime_config = runtime_config
        self._clipboard = clipboard
        self._local_text_loader = local_text_loader
        self._text_provider = text_provider

    def get_source(self, key: str) -> TextSourceEntry | None:
        return self._runtime_config.get_text_source(key)

    def get_source_options(self) -> list[dict[str, str]]:
        return self._runtime_config.get_text_source_options()

    def get_default_source_key(self) -> str:
        return self._runtime_config.default_text_source_key

    def fetch_from_network(self, source_key: str) -> str | None:
        if self._text_provider is None:
            return None
        return self._text_provider.fetch_text_by_key(source_key)

    def get_catalog(self) -> list[TextCatalogItem]:
        if self._text_provider is None:
            return []
        return self._text_provider.get_catalog()

    def fetch_from_clipboard(self) -> str:
        text = self._clipboard.text()
        return text if text else ""

    def fetch_from_local(self, path: str) -> str | None:
        return self._local_text_loader.load_text(path)
