from __future__ import annotations

import math

import pygame

from src.engine.resource_services import ImageService
from src.engine.service_locator import ServiceLocator
from src.ecs.world import World


def system_homing_rocket(world: World, delta_time: float) -> None:
    rockets_to_destroy: set[int] = set()

    for rocket_entity in world.get_rocket_entities():
        if rocket_entity not in world.homing_rockets:
            continue

        rocket = world.homing_rockets[rocket_entity]
        rocket.lifetime -= delta_time

        if rocket.lifetime <= 0:
            rockets_to_destroy.add(rocket_entity)
            continue

        if rocket.target_entity not in world.tag_enemies:
            rocket.target_entity = world.find_nearest_enemy(rocket_entity)

        if rocket.target_entity is None:
            continue

        direction = (
            world.get_entity_center(rocket.target_entity)
            - world.get_entity_center(rocket_entity)
        )

        if direction.length_squared() == 0:
            continue

        direction = direction.normalize()
        world.velocities[rocket_entity].velocity = direction * rocket.speed
        _rotate_rocket_towards(
            world,
            rocket_entity,
            direction,
            rocket.image_path,
            rocket.size,
        )

    for rocket_entity in rockets_to_destroy:
        world.destroy_entity(rocket_entity)


def _rotate_rocket_towards(
    world: World,
    rocket_entity: int,
    direction: pygame.Vector2,
    image_path: str,
    size: tuple[int, int],
) -> None:
    surface = world.surfaces[rocket_entity]
    transform = world.transforms[rocket_entity]
    center = world.get_entity_center(rocket_entity)
    base_texture = ServiceLocator.get(ImageService).load(image_path)
    base_texture = pygame.transform.scale(base_texture, size)

    angle = -(math.degrees(math.atan2(direction.y, direction.x)) + 90)
    rotated_texture = pygame.transform.rotate(base_texture, angle)
    rotated_rect = rotated_texture.get_rect(center=(round(center.x), round(center.y)))

    surface.texture = rotated_texture
    surface.area = rotated_texture.get_rect()
    transform.position = pygame.Vector2(rotated_rect.topleft)
