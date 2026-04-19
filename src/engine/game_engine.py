from __future__ import annotations

import json
from pathlib import Path

import pygame

from src.ecs.components.c_enemy_spawner import CEnemySpawner, SpawnEvent
from src.ecs.systems.s_animation import system_animation
from src.ecs.systems.s_bullet_bounds import system_bullet_bounds
from src.ecs.systems.s_collision_enemy_bullet import system_collision_enemy_bullet
from src.ecs.systems.s_collision_player_enemy import system_collision_player_enemy
from src.ecs.systems.s_enemy_bounce import system_enemy_bounce
from src.ecs.systems.s_enemy_spawner import system_enemy_spawner
from src.ecs.systems.s_explosion_cleanup import system_explosion_cleanup
from src.ecs.systems.s_hunter_behavior import system_hunter_behavior
from src.ecs.systems.s_input import system_input
from src.ecs.systems.s_movement import system_movement
from src.ecs.systems.s_player_animation import system_player_animation
from src.ecs.systems.s_player_bounds import system_player_bounds
from src.ecs.systems.s_rendering import system_rendering
from src.ecs.world import World


class GameEngine:
    def __init__(self, config_dir: str | Path | None = None) -> None:
        default_config_dir = Path(__file__).resolve().parents[2] / "assets" / "cfg"
        self.config_dir = Path(config_dir) if config_dir is not None else default_config_dir

        try:
            self.project_root = self.config_dir.parents[1]
        except IndexError:
            self.project_root = self.config_dir.parent

        self.window_config = self._load_window_config()
        self.enemy_definitions = self._load_enemy_definitions()
        self.level_config = self._load_level_config()
        self.player_config = self._load_player_config()
        self.bullet_config = self._load_bullet_config()
        self.explosion_config = self._load_explosion_config()

        pygame.init()
        self.screen = pygame.display.set_mode(tuple(self.window_config["size"]))
        pygame.display.set_caption(str(self.window_config["title"]))
        self.clock = pygame.time.Clock()
        self.is_running = True
        self.delta_time = 0.0
        self.events: list[pygame.event.Event] = []
        self.frame_rate = int(self.window_config["frame_rate"])
        self.background_color = tuple(self.window_config["background_color"])
        self.world: World | None = None

    def run(self) -> None:
        self._create()

        try:
            while self.is_running:
                self._calculate_time()
                self._process_events()
                self._update()
                self._draw()
        finally:
            self._clean()

    def _create(self) -> None:
        spawn_events = self._build_spawn_events()
        self.world = World(
            enemy_templates=self.enemy_definitions,
            explosion_template=self.explosion_config,
            project_root=self.project_root,
        )

        spawner_entity = self.world.create_entity()
        self.world.add_enemy_spawner(
            spawner_entity,
            CEnemySpawner(events=spawn_events),
        )
        self.world.create_player(
            position=self.level_config["player_spawn"],
            player_config=self.player_config,
            bullet_config=self.bullet_config,
            bullet_limit=int(self.level_config["bullet_limit"]),
        )

    def _calculate_time(self) -> None:
        self.delta_time = self.clock.tick(self.frame_rate) / 1000.0

    def _process_events(self) -> None:
        self.events = []

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            else:
                self.events.append(event)

    def _update(self) -> None:
        if self.world is None:
            return

        system_input(self.world, self.events)
        system_enemy_spawner(self.world, self.delta_time)
        system_hunter_behavior(self.world, self.delta_time)
        system_player_animation(self.world)
        system_movement(self.world, self.delta_time, self.screen.get_rect())
        system_enemy_bounce(self.world, self.screen.get_rect())
        system_player_bounds(self.world, self.screen.get_rect())
        system_collision_enemy_bullet(self.world)
        system_collision_player_enemy(self.world)
        system_bullet_bounds(self.world, self.screen.get_rect())
        system_animation(self.world, self.delta_time)
        system_explosion_cleanup(self.world)

    def _draw(self) -> None:
        if self.world is None:
            return

        self.screen.fill(self.background_color)
        system_rendering(self.world, self.screen)
        pygame.display.flip()

    def _clean(self) -> None:
        pygame.quit()

    def _build_spawn_events(self) -> list[SpawnEvent]:
        events: list[SpawnEvent] = []

        for event_data in self.level_config["events"]:
            events.append(
                SpawnEvent(
                    enemy_name=str(event_data["enemy"]),
                    time=float(event_data["time"]),
                    position=pygame.Vector2(event_data["position"]),
                )
            )

        events.sort(key=lambda event: event.time)
        return events

    def _load_window_config(self) -> dict[str, object]:
        window_config = self._load_json("window.json")

        if "size" in window_config and isinstance(window_config["size"], dict):
            size = (
                int(window_config["size"]["w"]),
                int(window_config["size"]["h"]),
            )
        else:
            size = tuple(window_config["size"])

        if "bg_color" in window_config and isinstance(window_config["bg_color"], dict):
            background_color = (
                int(window_config["bg_color"]["r"]),
                int(window_config["bg_color"]["g"]),
                int(window_config["bg_color"]["b"]),
            )
        else:
            background_color = tuple(window_config["background_color"])

        frame_rate = int(
            window_config.get("framerate", window_config.get("frame_rate", 60))
        )

        return {
            "title": window_config["title"],
            "size": size,
            "background_color": background_color,
            "frame_rate": frame_rate,
        }

    def _load_enemy_definitions(self) -> dict[str, dict[str, object]]:
        enemy_config = self._load_json("enemies.json")
        definitions: dict[str, dict[str, object]] = {}

        if "enemies" in enemy_config:
            for enemy_data in enemy_config["enemies"]:
                definitions[str(enemy_data["name"])] = {
                    "enemy_kind": "asteroid",
                    "size": self._read_size(enemy_data),
                    "color": self._read_color(enemy_data),
                    "min_speed": float(enemy_data["min_speed"]),
                    "max_speed": float(enemy_data["max_speed"]),
                }
            return definitions

        for enemy_name, enemy_data in enemy_config.items():
            template: dict[str, object] = {
                "image_path": enemy_data.get("image"),
                "animations": self._read_animation_config(enemy_data),
            }

            if "velocity_chase" in enemy_data:
                template.update(
                    {
                        "enemy_kind": "hunter",
                        "chase_speed": float(enemy_data["velocity_chase"]),
                        "return_speed": float(enemy_data["velocity_return"]),
                        "distance_start_chase": float(enemy_data["distance_start_chase"]),
                        "distance_start_return": float(enemy_data["distance_start_return"]),
                    }
                )
            else:
                template.update(
                    {
                        "enemy_kind": "asteroid",
                        "min_speed": float(
                            self._read_value(
                                enemy_data,
                                ["velocity_min", "min_speed"],
                                default=0.0,
                            )
                        ),
                        "max_speed": float(
                            self._read_value(
                                enemy_data,
                                ["velocity_max", "max_speed"],
                                default=0.0,
                            )
                        ),
                    }
                )

            definitions[str(enemy_name)] = template

        return definitions

    def _load_level_config(self) -> dict[str, object]:
        level_config = self._load_json("level_01.json")
        raw_events = level_config.get("events", level_config.get("enemy_spawn_events", []))
        events: list[dict[str, object]] = []

        for event_data in raw_events:
            if isinstance(event_data["position"], dict):
                position = (
                    float(event_data["position"]["x"]),
                    float(event_data["position"]["y"]),
                )
            else:
                position = tuple(event_data["position"])

            events.append(
                {
                    "enemy": event_data.get("enemy", event_data.get("enemy_type")),
                    "time": float(event_data["time"]),
                    "position": position,
                }
            )

        player_spawn_data = level_config.get("player_spawn")

        if isinstance(player_spawn_data, dict) and "position" in player_spawn_data:
            player_spawn = self._read_position(
                player_spawn_data,
                ["position"],
                default=(0.0, 0.0),
            )
            bullet_limit = int(
                self._read_value(
                    player_spawn_data,
                    ["max_bullets", "bullet_limit", "max_player_bullets"],
                    default=3,
                )
            )
        else:
            player_spawn = self._read_position(
                level_config,
                [
                    "player_spawn",
                    "player_spawn_position",
                    "player_start",
                    "player_start_position",
                    "player_origin",
                ],
                default=(0.0, 0.0),
            )
            bullet_limit = int(
                self._read_value(
                    level_config,
                    ["bullet_limit", "max_bullets", "max_player_bullets"],
                    default=3,
                )
            )

        return {
            "events": events,
            "player_spawn": player_spawn,
            "bullet_limit": bullet_limit,
        }

    def _load_player_config(self) -> dict[str, object]:
        player_config = self._load_json("player.json")
        config: dict[str, object] = {
            "image_path": player_config.get("image"),
            "animations": self._read_animation_config(player_config),
            "speed": float(
                self._read_value(
                    player_config,
                    ["input_velocity", "movement_speed", "speed", "velocity"],
                    default=240.0,
                )
            ),
        }

        if "size" in player_config:
            config["size"] = self._read_size(player_config)

        if "color" in player_config:
            config["color"] = self._read_color(player_config)

        return config

    def _load_bullet_config(self) -> dict[str, object]:
        bullet_config = self._load_json("bullet.json")
        config: dict[str, object] = {
            "image_path": bullet_config.get("image"),
            "speed": float(
                self._read_value(
                    bullet_config,
                    ["bullet_speed", "speed", "velocity"],
                    default=420.0,
                )
            ),
        }

        if "size" in bullet_config:
            config["size"] = self._read_size(bullet_config)

        if "color" in bullet_config:
            config["color"] = self._read_color(bullet_config)

        return config

    def _load_explosion_config(self) -> dict[str, object]:
        explosion_config = self._load_json("explosion.json")
        config: dict[str, object] = {
            "image_path": explosion_config.get("image"),
            "animations": self._read_animation_config(explosion_config),
        }

        if "size" in explosion_config:
            config["size"] = self._read_size(explosion_config)

        if "color" in explosion_config:
            config["color"] = self._read_color(explosion_config)

        return config


    def _read_animation_config(self, data: dict[str, object]) -> dict[str, object] | None:
        raw_animations = data.get("animations")

        if raw_animations is None:
            return None

        number_frames = int(raw_animations["number_frames"])
        if number_frames <= 0:
            raise ValueError("Animation number_frames must be greater than zero.")

        clips: dict[str, dict[str, object]] = {}

        for clip_data in raw_animations["list"]:
            name = str(clip_data["name"])
            start = int(clip_data["start"])
            end = int(clip_data["end"])
            framerate = float(clip_data["framerate"])

            if end < start:
                raise ValueError(f"Animation '{name}' has an invalid frame range.")
            if framerate <= 0:
                raise ValueError(f"Animation '{name}' must have a positive framerate.")

            clips[name] = {
                "name": name,
                "start": start,
                "end": end,
                "framerate": framerate,
                "loop": bool(clip_data.get("loop", name != "EXPLODE")),
            }

        return {
            "number_frames": number_frames,
            "clips": clips,
        }

    def _read_size(self, data: dict[str, object]) -> tuple[int, int]:
        size_data = data["size"]

        if isinstance(size_data, dict):
            return (int(size_data["x"]), int(size_data["y"]))

        return (int(size_data[0]), int(size_data[1]))

    def _read_color(self, data: dict[str, object]) -> tuple[int, int, int]:
        color_data = data.get("color", data.get("bg_color", data.get("background_color")))

        if isinstance(color_data, dict):
            return (
                int(color_data["r"]),
                int(color_data["g"]),
                int(color_data["b"]),
            )

        return (
            int(color_data[0]),
            int(color_data[1]),
            int(color_data[2]),
        )

    def _read_position(
        self,
        data: dict[str, object],
        keys: list[str],
        default: tuple[float, float],
    ) -> tuple[float, float]:
        position_data = self._read_value(data, keys, default=default)

        if isinstance(position_data, dict):
            return (
                float(position_data["x"]),
                float(position_data["y"]),
            )

        return (float(position_data[0]), float(position_data[1]))

    def _read_value(
        self,
        data: dict[str, object],
        keys: list[str],
        default: object,
    ) -> object:
        for key in keys:
            if key in data:
                return data[key]

        return default

    def _load_json(self, filename: str) -> dict[str, object]:
        file_path = self.config_dir / filename

        with file_path.open("r", encoding="utf-8") as config_file:
            return json.load(config_file)
