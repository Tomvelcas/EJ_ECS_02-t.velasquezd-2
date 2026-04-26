from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CHomingRocket:
    target_entity: int | None
    speed: float
    lifetime: float
    collision_radius: float
    explosion_radius: float
    image_path: str
    size: tuple[int, int]
