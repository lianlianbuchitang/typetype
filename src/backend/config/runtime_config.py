from dataclasses import dataclass


@dataclass
class RuntimeConfig:
    """运行时配置。"""

    jstext_source_url: str = "https://www.jsxiaoshi.com/index.php/Api/Text/getContent"
    api_timeout: float = 20.0
