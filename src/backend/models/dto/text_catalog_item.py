from dataclasses import dataclass


@dataclass
class TextCatalogItem:
    id: int
    text_id: str
    label: str
    description: str = ""
    has_ranking: bool = False
