from dataclasses import dataclass


@dataclass
class CRocketAbility:
    rocket_template: dict[str, object]
    cooldown: float
    cooldown_remaining: float = 0.0
