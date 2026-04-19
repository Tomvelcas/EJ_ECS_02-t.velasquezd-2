from dataclasses import dataclass, field

import pygame


@dataclass
class SpawnEvent:
    enemy_name: str
    time: float
    position: pygame.Vector2
    triggered: bool = False


@dataclass
class CEnemySpawner:
    events: list[SpawnEvent] = field(default_factory=list)
    elapsed_time: float = 0.0
