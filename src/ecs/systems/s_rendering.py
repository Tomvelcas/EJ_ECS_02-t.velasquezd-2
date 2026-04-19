import pygame

from src.ecs.world import World


def system_rendering(world: World, screen: pygame.Surface) -> None:
    for entity in world.get_renderable_entities():
        transform = world.transforms[entity]
        surface = world.surfaces[entity]
        entity_rect = surface.surface.get_rect(
            topleft=(round(transform.position.x), round(transform.position.y))
        )
        screen.blit(surface.surface, entity_rect)
