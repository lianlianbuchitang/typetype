from dataclasses import dataclass


@dataclass
class TextCatalogItem:
    text_id: str
    label: str
    description: str = ""
    has_ranking: bool = False
