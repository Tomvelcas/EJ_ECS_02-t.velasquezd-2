import pygame

from src.ecs.world import World


def system_rendering(world: World, screen: pygame.Surface) -> None:
    renderable_entities = sorted(
        world.get_renderable_entities(),
        key=lambda entity: (world.surfaces[entity].layer, entity),
    )

    for entity in renderable_entities:
        text = world.texts.get(entity)
        if text is not None and not text.visible:
            continue

        surface = world.surfaces[entity]
        entity_rect = world.get_entity_rect(entity)
        screen.blit(surface.texture, entity_rect, surface.area)
