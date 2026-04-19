from __future__ import annotations

from src.ecs.world import World


def system_explosion_cleanup(world: World) -> None:
    for entity in world.get_explosion_entities():
        animation = world.animations.get(entity)

        if animation is not None and animation.finished:
            world.destroy_entity(entity)
