from __future__ import annotations

from src.ecs.world import World


def system_enemy_spawner(world: World, delta_time: float) -> None:
    spawner = world.get_enemy_spawner()

    if spawner is None:
        return

    spawner.elapsed_time += delta_time

    for event in spawner.events:
        if event.triggered:
            continue

        if spawner.elapsed_time >= event.time:
            world.create_enemy_from_template(event.enemy_name, event.position)
            event.triggered = True
