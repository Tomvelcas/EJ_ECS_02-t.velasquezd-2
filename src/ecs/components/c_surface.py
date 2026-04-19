from dataclasses import dataclass

import pygame


@dataclass
class CSurface:
    texture: pygame.Surface
    area: pygame.Rect
