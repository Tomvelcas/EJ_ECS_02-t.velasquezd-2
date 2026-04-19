from dataclasses import dataclass

import pygame


Color = tuple[int, int, int]


@dataclass
class CSurface:
    surface: pygame.Surface
    color: Color
