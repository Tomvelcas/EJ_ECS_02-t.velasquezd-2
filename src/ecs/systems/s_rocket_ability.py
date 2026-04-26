from __future__ import annotations

from src.ecs.world import World


def system_rocket_ability(world: World, delta_time: float) -> None:
    for ability in world.rocket_abilities.values():
        if ability.cooldown_remaining > 0:
            ability.cooldown_remaining = max(0.0, ability.cooldown_remaining - delta_time)
