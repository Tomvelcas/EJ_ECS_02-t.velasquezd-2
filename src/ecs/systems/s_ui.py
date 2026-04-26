from __future__ import annotations

from src.ecs.world import World


READY_COLOR = (126, 255, 178)
RELOADING_COLOR = (255, 218, 117)


def system_ui(world: World, is_paused: bool) -> None:
    for entity, text in world.texts.items():
        if text.kind == "pause":
            text.visible = is_paused
            continue

        if text.kind != "rocket_status":
            continue

        player_entity = world.get_player_entity()
        if player_entity is None or player_entity not in world.rocket_abilities:
            world.set_text(entity, "E Rocket: --", RELOADING_COLOR)
            continue

        ability = world.rocket_abilities[player_entity]
        if ability.cooldown_remaining <= 0:
            world.set_text(entity, "E Rocket: LISTO", READY_COLOR)
            continue

        ready_percent = round(
            (1.0 - ability.cooldown_remaining / ability.cooldown) * 100
        )
        world.set_text(entity, f"E Rocket: {ready_percent}%", RELOADING_COLOR)
