from __future__ import annotations

import pygame

from src.ecs.world import World


def system_collision_enemy_bullet(world: World) -> None:
    bullets_to_destroy: set[int] = set()
    enemies_to_destroy: set[int] = set()

    for bullet_entity in world.get_bullet_entities():
        if bullet_entity in bullets_to_destroy:
            continue

        bullet_rect = world.get_entity_rect(bullet_entity)

        for enemy_entity in world.get_enemy_entities():
            if enemy_entity in enemies_to_destroy:
                continue

            enemy_rect = world.get_entity_rect(enemy_entity)

            if bullet_rect.colliderect(enemy_rect):
                overlap = bullet_rect.clip(enemy_rect)
                impact_center = overlap.center if overlap.width and overlap.height else enemy_rect.center
                world.create_explosion(pygame.Vector2(impact_center))
                bullets_to_destroy.add(bullet_entity)
                enemies_to_destroy.add(enemy_entity)
                break

    for entity in bullets_to_destroy | enemies_to_destroy:
        world.destroy_entity(entity)
