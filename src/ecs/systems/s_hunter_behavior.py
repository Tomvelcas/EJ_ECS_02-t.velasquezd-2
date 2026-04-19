from __future__ import annotations

import pygame

from src.ecs.components.c_hunter_behavior import (
    HUNTER_CHASE,
    HUNTER_IDLE,
    HUNTER_RETURN,
)
from src.ecs.world import World


def system_hunter_behavior(world: World, delta_time: float) -> None:
    player_entity = world.get_player_entity()
    player_center = (
        world.get_entity_center(player_entity)
        if player_entity is not None
        else None
    )

    for entity in world.get_hunter_entities():
        transform = world.transforms[entity]
        velocity = world.velocities[entity]
        behavior = world.hunter_behaviors[entity]

        distance_from_origin = transform.position.distance_to(behavior.origin)

        if behavior.state != HUNTER_RETURN and distance_from_origin > behavior.distance_start_return:
            behavior.state = HUNTER_RETURN

        if behavior.state == HUNTER_RETURN:
            direction_to_origin = behavior.origin - transform.position
            snap_distance = behavior.return_speed * delta_time

            if direction_to_origin.length() <= snap_distance:
                transform.position = behavior.origin.copy()
                velocity.velocity = pygame.Vector2()
                behavior.state = HUNTER_IDLE
                world.set_animation(entity, "IDLE")
                continue

            velocity.velocity = direction_to_origin.normalize() * behavior.return_speed
            world.set_animation(entity, "MOVE")
            continue

        if player_center is None:
            velocity.velocity = pygame.Vector2()
            behavior.state = HUNTER_IDLE
            world.set_animation(entity, "IDLE")
            continue

        hunter_center = world.get_entity_center(entity)
        direction_to_player = player_center - hunter_center

        if direction_to_player.length() <= behavior.distance_start_chase:
            behavior.state = HUNTER_CHASE
            if direction_to_player.length_squared() > 0:
                velocity.velocity = direction_to_player.normalize() * behavior.chase_speed
            else:
                velocity.velocity = pygame.Vector2()
        else:
            behavior.state = HUNTER_IDLE
            velocity.velocity = pygame.Vector2()

        if velocity.velocity.length_squared() > 0:
            world.set_animation(entity, "MOVE")
        else:
            world.set_animation(entity, "IDLE")
