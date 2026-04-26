from __future__ import annotations

import pygame

from src.ecs.world import World


def system_collision_rocket_enemy(world: World) -> None:
    rockets_to_destroy: set[int] = set()
    enemies_to_destroy: set[int] = set()

    for rocket_entity in world.get_rocket_entities():
        if rocket_entity in rockets_to_destroy:
            continue

        rocket_center = world.get_entity_center(rocket_entity)
        rocket = world.homing_rockets.get(rocket_entity)
        if rocket is None:
            continue

        for enemy_entity in world.get_enemy_entities():
            if enemy_entity in enemies_to_destroy:
                continue

            enemy_rect = world.get_entity_rect(enemy_entity)
            enemy_center = world.get_entity_center(enemy_entity)
            hit_distance = rocket.collision_radius + max(
                enemy_rect.width,
                enemy_rect.height,
            ) / 2

            if rocket_center.distance_to(enemy_center) > hit_distance:
                continue

            world.create_explosion(pygame.Vector2(enemy_rect.center))
            rockets_to_destroy.add(rocket_entity)
            enemies_to_destroy.add(enemy_entity)
            break

    for entity in rockets_to_destroy | enemies_to_destroy:
        world.destroy_entity(entity)
