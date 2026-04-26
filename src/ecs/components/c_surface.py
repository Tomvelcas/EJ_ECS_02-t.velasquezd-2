from dataclasses import dataclass

import pygame

from src.engine.resource_services import TextService
from src.engine.service_locator import ServiceLocator


@dataclass
class CSurface:
    texture: pygame.Surface
    area: pygame.Rect
    layer: int = 0

    @classmethod
    def from_text(
        cls,
        text: str,
        font_path: str,
        size: int,
        color: tuple[int, int, int],
        layer: int = 100,
    ) -> "CSurface":
        texture = ServiceLocator.get(TextService).render(text, font_path, size, color)
        return cls(texture=texture, area=texture.get_rect(), layer=layer)
