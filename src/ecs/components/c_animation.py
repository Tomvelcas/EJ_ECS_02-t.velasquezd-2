from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AnimationClip:
    name: str
    start: int
    end: int
    framerate: float
    loop: bool = True


@dataclass
class CAnimation:
    clips: dict[str, AnimationClip]
    current_animation: str
    current_frame: int
    elapsed_time: float = 0.0
    finished: bool = False

    def set_animation(self, animation_name: str) -> None:
        if animation_name == self.current_animation:
            return

        clip = self.clips[animation_name]
        self.current_animation = animation_name
        self.current_frame = clip.start
        self.elapsed_time = 0.0
        self.finished = False

    def get_current_clip(self) -> AnimationClip:
        return self.clips[self.current_animation]
