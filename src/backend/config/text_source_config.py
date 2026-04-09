from dataclasses import dataclass, field


@dataclass
class TextSourceEntry:
    key: str
    label: str
    has_ranking: bool = False
    local_path: str | None = None
    text_id: str = ""


@dataclass
class TextSourceConfig:
    sources: dict[str, TextSourceEntry] = field(default_factory=dict)
    default_key: str = ""

    def get_source(self, key: str) -> TextSourceEntry | None:
        return self.sources.get(key)

    def get_default_source(self) -> TextSourceEntry | None:
        if self.default_key:
            return self.sources.get(self.default_key)
        return None

    def get_source_options(self) -> list[dict[str, str]]:
        return [
            {"key": source.key, "label": source.label}
            for source in self.sources.values()
        ]

    def get_ranking_sources(self) -> list[TextSourceEntry]:
        return [source for source in self.sources.values() if source.has_ranking]
