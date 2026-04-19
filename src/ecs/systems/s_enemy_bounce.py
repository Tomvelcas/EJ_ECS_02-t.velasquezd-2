from __future__ import annotations

import pygame

from src.ecs.world import World


def system_enemy_bounce(world: World, play_area: pygame.Rect) -> None:
    for entity in world.get_enemy_entities():
        if entity in world.hunter_behaviors:
            continue

        transform = world.transforms[entity]
        velocity = world.velocities[entity]
        entity_rect = world.get_entity_rect(entity)

        if transform.position.x < play_area.left or entity_rect.right > play_area.right:
            if transform.position.x < play_area.left:
                transform.position.x = float(play_area.left)
            elif entity_rect.right > play_area.right:
                transform.position.x = float(play_area.right - entity_rect.width)
            velocity.velocity.x *= -1

        if transform.position.y < play_area.top or entity_rect.bottom > play_area.bottom:
            if transform.position.y < play_area.top:
                transform.position.y = float(play_area.top)
            elif entity_rect.bottom > play_area.bottom:
                transform.position.y = float(play_area.bottom - entity_rect.height)
            velocity.velocity.y *= -1
