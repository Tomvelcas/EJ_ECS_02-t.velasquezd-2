from __future__ import annotations

from src.ecs.world import World


def system_animation(world: World, delta_time: float) -> None:
    for entity, animation in list(world.animations.items()):
        clip = animation.get_current_clip()

        if animation.finished or clip.framerate <= 0:
            continue

        if clip.start == clip.end:
            animation.current_frame = clip.start
            world.sync_animation_frame(entity)
            continue

        frame_duration = 1.0 / clip.framerate
        animation.elapsed_time += delta_time

        while animation.elapsed_time >= frame_duration and not animation.finished:
            animation.elapsed_time -= frame_duration

            if animation.current_frame < clip.end:
                animation.current_frame += 1
            elif clip.loop:
                animation.current_frame = clip.start
            else:
                animation.finished = True

            world.sync_animation_frame(entity)
