from __future__ import annotations

import pygame

from src.ecs.world import World


def system_movement(world: World, delta_time: float, play_area: pygame.Rect) -> None:
    for entity in world.get_movable_entities():
        transform = world.transforms[entity]
        velocity = world.velocities[entity]

        transform.position += velocity.velocity * delta_time
