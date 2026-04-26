from dataclasses import dataclass


@dataclass
class CMovementSound:
    sound_path: str
    interval: float
    elapsed_time: float = 0.0
