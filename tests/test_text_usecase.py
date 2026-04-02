from src.backend.application.usecases.load_text_usecase import LoadTextUseCase
from src.backend.models.config.text_source_config import TextSourceEntry


class DummyTextProvider:
    def __init__(self, text_result=None):
        self._text_result = text_result

    def get_catalog(self):
        return []

    def fetch_text_by_key(self, source_key):
        return self._text_result


class DummyLocalTextLoader:
    def __init__(self, result=None):
        self._result = result

    def load_text(self, path):
        return self._result


class DummyClipboardReader:
    def __init__(self, text=""):
        self._text = text

    def text(self):
        return self._text


def test_load_network_success():
    usecase = LoadTextUseCase(
        text_provider=DummyTextProvider(text_result="abc"),
        local_text_loader=DummyLocalTextLoader(),
        clipboard_reader=DummyClipboardReader(),
    )
    source = TextSourceEntry(key="test", label="Test Network")
    result = usecase.load_from_source(source)
    assert result.success
    assert result.text == "abc"


def test_load_from_clipboard():
    usecase = LoadTextUseCase(
        text_provider=DummyTextProvider(),
        local_text_loader=DummyLocalTextLoader(),
        clipboard_reader=DummyClipboardReader("clipboard text"),
    )
    result = usecase.load_from_clipboard()
    assert result.success
    assert result.text == "clipboard text"


def test_load_local_success():
    usecase = LoadTextUseCase(
        text_provider=DummyTextProvider(),
        local_text_loader=DummyLocalTextLoader("local text"),
        clipboard_reader=DummyClipboardReader(),
    )
    source = TextSourceEntry(
        key="test", label="Test Local", local_path="/path/to/file.txt"
    )
    result = usecase.load_from_source(source)
    assert result.success
    assert result.text == "local text"


def test_load_network_fetch_returns_none():
    usecase = LoadTextUseCase(
        text_provider=DummyTextProvider(text_result=None),
        local_text_loader=DummyLocalTextLoader(),
        clipboard_reader=DummyClipboardReader(),
    )
    source = TextSourceEntry(key="test", label="Test Network")
    result = usecase.load_from_source(source)
    assert not result.success
    assert "无法获取文本内容" in result.error_message


def test_load_clipboard_empty():
    usecase = LoadTextUseCase(
        text_provider=DummyTextProvider(),
        local_text_loader=DummyLocalTextLoader(),
        clipboard_reader=DummyClipboardReader(""),
    )
    result = usecase.load_from_clipboard()
    assert not result.success
    assert "剪贴板无文本" in result.error_message
