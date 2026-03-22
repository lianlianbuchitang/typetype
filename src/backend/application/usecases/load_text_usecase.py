"""Load Text Use Case - 文本加载业务流程编排。

协调 TextGateway，完成文本加载的完整流程。

异常处理：
- 路由逻辑和业务验证在 UseCase 内完成
- 网络异常（NetworkTimeoutError 等）上浮，由 BaseWorker 通过 GlobalExceptionHandler 统一转换
"""

from dataclasses import dataclass

from ..ports.load_text_gateway import LoadTextGateway


@dataclass
class LoadTextResult:
    success: bool
    text: str
    error_message: str = ""


class LoadTextUseCase:
    def __init__(self, gateway: LoadTextGateway):
        self._gateway = gateway

    def load(self, source_key: str) -> LoadTextResult:
        source = self._gateway.get_source(source_key)
        if not source:
            return LoadTextResult(
                success=False, text="", error_message=f"未知载文来源({source_key})"
            )

        if source.type == "local":
            return self._load_from_local(source.local_path)
        elif source.type == "network_direct":
            if not source.url:
                return LoadTextResult(
                    success=False, text="", error_message="网络来源缺少 URL"
                )
            return LoadTextResult(
                success=True,
                text=self._gateway.fetch_from_network(source.url, source.fetcher_key)
                or "",
            )
        elif source.type == "network_catalog":
            if not source.text_id:
                return LoadTextResult(
                    success=False, text="", error_message="文本库来源缺少 text_id"
                )
            return LoadTextResult(
                success=True,
                text=self._gateway.fetch_from_catalog(source.text_id) or "",
            )
        else:
            return LoadTextResult(
                success=False, text="", error_message=f"未知载文来源类型({source_key})"
            )

    def _load_from_local(self, path: str | None) -> LoadTextResult:
        if not path:
            return LoadTextResult(
                success=False, text="", error_message="本地来源缺少路径"
            )
        text = self._gateway.fetch_from_local(path)
        if text is None:
            return LoadTextResult(
                success=False, text="", error_message="无法读取本地文章"
            )
        return LoadTextResult(success=True, text=text)

    def load_from_clipboard(self) -> LoadTextResult:
        text = self._gateway.fetch_from_clipboard()
        if not text:
            return LoadTextResult(
                success=False, text="", error_message="当前剪贴板无文本内容"
            )
        return LoadTextResult(success=True, text=text)
