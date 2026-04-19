from __future__ import annotations

import pygame

from src.ecs.world import World


def system_player_bounds(world: World, play_area: pygame.Rect) -> None:
    player_entity = world.get_player_entity()

    if player_entity is None:
        return

    transform = world.transforms[player_entity]
    entity_rect = world.get_entity_rect(player_entity)

    if transform.position.x < play_area.left:
        transform.position.x = float(play_area.left)
    elif entity_rect.right > play_area.right:
        transform.position.x = float(play_area.right - entity_rect.width)

    if transform.position.y < play_area.top:
        transform.position.y = float(play_area.top)
    elif entity_rect.bottom > play_area.bottom:
        transform.position.y = float(play_area.bottom - entity_rect.height)
