from __future__ import annotations

import pygame

from src.ecs.world import World


def system_enemy_bounce(world: World, play_area: pygame.Rect) -> None:
    for entity in world.get_enemy_entities():
        transform = world.transforms[entity]
        surface = world.surfaces[entity]
        velocity = world.velocities[entity]
        entity_rect = surface.surface.get_rect()

        if transform.position.x < play_area.left or transform.position.x + entity_rect.width > play_area.right:
            if transform.position.x < play_area.left:
                transform.position.x = float(play_area.left)
            elif transform.position.x + entity_rect.width > play_area.right:
                transform.position.x = float(play_area.right - entity_rect.width)
            velocity.velocity.x *= -1

        if transform.position.y < play_area.top or transform.position.y + entity_rect.height > play_area.bottom:
            if transform.position.y < play_area.top:
                transform.position.y = float(play_area.top)
            elif transform.position.y + entity_rect.height > play_area.bottom:
                transform.position.y = float(play_area.bottom - entity_rect.height)
            velocity.velocity.y *= -1
