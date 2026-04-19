from __future__ import annotations

from src.ecs.world import World


def system_collision_player_enemy(world: World) -> None:
    player_entity = world.get_player_entity()

    if player_entity is None:
        return

    player_transform = world.transforms[player_entity]
    player_surface = world.surfaces[player_entity]
    player_rect = player_surface.surface.get_rect(
        topleft=(round(player_transform.position.x), round(player_transform.position.y))
    )

    for enemy_entity in world.get_enemy_entities():
        enemy_transform = world.transforms[enemy_entity]
        enemy_surface = world.surfaces[enemy_entity]
        enemy_rect = enemy_surface.surface.get_rect(
            topleft=(round(enemy_transform.position.x), round(enemy_transform.position.y))
        )

        if player_rect.colliderect(enemy_rect):
            world.destroy_entity(enemy_entity)
            world.destroy_entity(player_entity)
            return
