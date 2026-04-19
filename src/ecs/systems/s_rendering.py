import pygame

from src.ecs.world import World


def system_rendering(world: World, screen: pygame.Surface) -> None:
    for entity in world.get_renderable_entities():
        surface = world.surfaces[entity]
        entity_rect = world.get_entity_rect(entity)
        screen.blit(surface.texture, entity_rect, surface.area)
