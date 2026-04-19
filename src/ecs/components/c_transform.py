from dataclasses import dataclass

import pygame


@dataclass
class CTransform:
    position: pygame.Vector2
