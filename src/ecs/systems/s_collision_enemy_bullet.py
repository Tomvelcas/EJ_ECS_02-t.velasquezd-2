from __future__ import annotations

from src.ecs.world import World


def system_collision_enemy_bullet(world: World) -> None:
    bullets_to_destroy: set[int] = set()
    enemies_to_destroy: set[int] = set()

    for bullet_entity in world.get_bullet_entities():
        bullet_transform = world.transforms[bullet_entity]
        bullet_surface = world.surfaces[bullet_entity]
        bullet_rect = bullet_surface.surface.get_rect(
            topleft=(round(bullet_transform.position.x), round(bullet_transform.position.y))
        )

        for enemy_entity in world.get_enemy_entities():
            enemy_transform = world.transforms[enemy_entity]
            enemy_surface = world.surfaces[enemy_entity]
            enemy_rect = enemy_surface.surface.get_rect(
                topleft=(round(enemy_transform.position.x), round(enemy_transform.position.y))
            )

            if bullet_rect.colliderect(enemy_rect):
                bullets_to_destroy.add(bullet_entity)
                enemies_to_destroy.add(enemy_entity)
                break

    for entity in bullets_to_destroy | enemies_to_destroy:
        world.destroy_entity(entity)
