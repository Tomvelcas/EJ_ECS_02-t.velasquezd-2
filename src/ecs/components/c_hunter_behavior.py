from __future__ import annotations

from dataclasses import dataclass

import pygame


HUNTER_IDLE = "IDLE"
HUNTER_CHASE = "CHASE"
HUNTER_RETURN = "RETURN"


@dataclass
class CHunterBehavior:
    origin: pygame.Vector2
    chase_speed: float
    return_speed: float
    distance_start_chase: float
    distance_start_return: float
    sound_chase: str | None = None
    state: str = HUNTER_IDLE
