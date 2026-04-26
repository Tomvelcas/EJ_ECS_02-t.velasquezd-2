from dataclasses import dataclass


@dataclass
class CText:
    content: str
    font_path: str
    size: int
    color: tuple[int, int, int]
    kind: str = "static"
    visible: bool = True
