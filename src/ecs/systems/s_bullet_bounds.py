from __future__ import annotations

import pygame

from src.ecs.world import World


def system_bullet_bounds(world: World, play_area: pygame.Rect) -> None:
    bullets_to_destroy: list[int] = []

    for entity in world.get_bullet_entities():
        transform = world.transforms[entity]
        surface = world.surfaces[entity]
        entity_rect = surface.surface.get_rect(
            topleft=(transform.position.x, transform.position.y)
        )

        if (
            entity_rect.left <= play_area.left
            or entity_rect.right >= play_area.right
            or entity_rect.top <= play_area.top
            or entity_rect.bottom >= play_area.bottom
        ):
            bullets_to_destroy.append(entity)

    for entity in bullets_to_destroy:
        world.destroy_entity(entity)
