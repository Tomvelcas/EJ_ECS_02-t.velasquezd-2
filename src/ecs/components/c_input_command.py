from __future__ import annotations

from dataclasses import dataclass, field

import pygame

from src.ecs.components.c_surface import Color


PLAYER_LEFT = "PLAYER_LEFT"
PLAYER_RIGHT = "PLAYER_RIGHT"
PLAYER_UP = "PLAYER_UP"
PLAYER_DOWN = "PLAYER_DOWN"
PLAYER_FIRE = "PLAYER_FIRE"


@dataclass
class InputAction:
    name: str
    target_position: pygame.Vector2 | None = None


@dataclass
class CInputCommand:
    move_speed: float
    bullet_size: tuple[int, int]
    bullet_color: Color
    bullet_speed: float
    bullet_limit: int
    pending_actions: list[InputAction] = field(default_factory=list)
