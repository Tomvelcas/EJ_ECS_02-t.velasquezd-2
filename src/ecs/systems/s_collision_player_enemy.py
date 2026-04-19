from __future__ import annotations

import pygame

from src.ecs.world import World


def system_collision_player_enemy(world: World) -> None:
    player_entity = world.get_player_entity()

    if player_entity is None:
        return

    player_tag = world.tag_players[player_entity]
    player_rect = world.get_entity_rect(player_entity)

    for enemy_entity in world.get_enemy_entities():
        enemy_rect = world.get_entity_rect(enemy_entity)

        if player_rect.colliderect(enemy_rect):
            overlap = player_rect.clip(enemy_rect)
            impact_center = overlap.center if overlap.width and overlap.height else player_rect.center
            world.create_explosion(pygame.Vector2(impact_center))
            respawn_position = player_tag.respawn_position.copy()
            world.destroy_entity(enemy_entity)
            world.destroy_entity(player_entity)
            world.respawn_player(respawn_position)
            return
