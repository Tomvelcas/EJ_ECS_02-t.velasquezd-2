from __future__ import annotations

from src.engine.resource_services import SoundService
from src.engine.service_locator import ServiceLocator
from src.ecs.world import World


def system_movement_sound(world: World, delta_time: float) -> None:
    sound_service = ServiceLocator.get(SoundService)

    for entity, movement_sound in world.movement_sounds.items():
        if entity not in world.velocities:
            continue

        is_moving = world.velocities[entity].velocity.length_squared() > 0
        if not is_moving:
            movement_sound.elapsed_time = 0.0
            continue

        movement_sound.elapsed_time -= delta_time
        if movement_sound.elapsed_time <= 0:
            sound_service.play(movement_sound.sound_path)
            movement_sound.elapsed_time = movement_sound.interval
