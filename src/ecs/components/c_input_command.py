from __future__ import annotations

from dataclasses import dataclass, field

import pygame


PLAYER_LEFT = "PLAYER_LEFT"
PLAYER_RIGHT = "PLAYER_RIGHT"
PLAYER_UP = "PLAYER_UP"
PLAYER_DOWN = "PLAYER_DOWN"
PLAYER_FIRE = "PLAYER_FIRE"
PLAYER_ROCKET = "PLAYER_ROCKET"


@dataclass
class InputAction:
    name: str
    target_position: pygame.Vector2 | None = None


@dataclass
class CInputCommand:
    move_speed: float
    bullet_template: dict[str, object]
    bullet_speed: float
    bullet_limit: int
    pending_actions: list[InputAction] = field(default_factory=list)
