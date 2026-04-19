from __future__ import annotations

from src.ecs.world import World


def system_player_animation(world: World) -> None:
    player_entity = world.get_player_entity()

    if player_entity is None or player_entity not in world.animations:
        return

    player_velocity = world.velocities[player_entity].velocity

    if player_velocity.length_squared() > 0:
        world.set_animation(player_entity, "MOVE")
    else:
        world.set_animation(player_entity, "IDLE")
