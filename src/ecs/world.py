from __future__ import annotations

import random
from pathlib import Path

import pygame

from src.ecs.components.c_animation import AnimationClip, CAnimation
from src.ecs.components.c_enemy_spawner import CEnemySpawner
from src.ecs.components.c_hunter_behavior import CHunterBehavior
from src.ecs.components.c_input_command import CInputCommand
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_tag_bullet import CTagBullet
from src.ecs.components.c_tag_enemy import CTagEnemy
from src.ecs.components.c_tag_explosion import CTagExplosion
from src.ecs.components.c_tag_player import CTagPlayer
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity


class World:
    def __init__(
        self,
        enemy_templates: dict[str, dict[str, object]],
        explosion_template: dict[str, object],
        project_root: str | Path,
    ) -> None:
        self._next_entity_id = 0
        self.entities: set[int] = set()
        self.transforms: dict[int, CTransform] = {}
        self.surfaces: dict[int, CSurface] = {}
        self.velocities: dict[int, CVelocity] = {}
        self.input_commands: dict[int, CInputCommand] = {}
        self.enemy_spawners: dict[int, CEnemySpawner] = {}
        self.animations: dict[int, CAnimation] = {}
        self.hunter_behaviors: dict[int, CHunterBehavior] = {}
        self.tag_players: dict[int, CTagPlayer] = {}
        self.tag_bullets: dict[int, CTagBullet] = {}
        self.tag_enemies: dict[int, CTagEnemy] = {}
        self.tag_explosions: dict[int, CTagExplosion] = {}
        self.enemy_templates = enemy_templates
        self.explosion_template = explosion_template
        self.project_root = Path(project_root)
        self._image_cache: dict[str, pygame.Surface] = {}
        self.player_template: dict[str, object] | None = None
        self.player_bullet_template: dict[str, object] | None = None
        self.player_bullet_limit: int = 0

    def create_entity(self) -> int:
        entity = self._next_entity_id
        self._next_entity_id += 1
        self.entities.add(entity)
        return entity

    def add_transform(self, entity: int, component: CTransform) -> None:
        self.transforms[entity] = component

    def add_surface(self, entity: int, component: CSurface) -> None:
        self.surfaces[entity] = component

    def add_velocity(self, entity: int, component: CVelocity) -> None:
        self.velocities[entity] = component

    def add_input_command(self, entity: int, component: CInputCommand) -> None:
        self.input_commands[entity] = component

    def add_enemy_spawner(self, entity: int, component: CEnemySpawner) -> None:
        if self.enemy_spawners:
            raise ValueError("World only supports one CEnemySpawner entity.")

        self.enemy_spawners[entity] = component

    def add_animation(self, entity: int, component: CAnimation) -> None:
        self.animations[entity] = component
        self.sync_animation_frame(entity)

    def add_hunter_behavior(self, entity: int, component: CHunterBehavior) -> None:
        self.hunter_behaviors[entity] = component

    def add_tag_player(self, entity: int, component: CTagPlayer) -> None:
        self.tag_players[entity] = component

    def add_tag_bullet(self, entity: int, component: CTagBullet) -> None:
        self.tag_bullets[entity] = component

    def add_tag_enemy(self, entity: int, component: CTagEnemy) -> None:
        self.tag_enemies[entity] = component

    def add_tag_explosion(self, entity: int, component: CTagExplosion) -> None:
        self.tag_explosions[entity] = component

    def create_player(
        self,
        position: pygame.Vector2 | tuple[float, float],
        player_config: dict[str, object],
        bullet_config: dict[str, object],
        bullet_limit: int,
    ) -> int:
        entity = self.create_entity()
        self.player_template = player_config
        self.player_bullet_template = bullet_config
        self.player_bullet_limit = bullet_limit

        self.add_transform(entity, CTransform(pygame.Vector2(position)))
        self.add_surface(entity, self._build_surface_component(player_config))
        self.add_velocity(entity, CVelocity(pygame.Vector2()))
        self.add_input_command(
            entity,
            CInputCommand(
                move_speed=float(player_config["speed"]),
                bullet_template=bullet_config,
                bullet_speed=float(bullet_config["speed"]),
                bullet_limit=bullet_limit,
            ),
        )

        animation_component = self._build_animation_component(
            player_config,
            preferred_animation="IDLE",
        )
        if animation_component is not None:
            self.add_animation(entity, animation_component)

        self.add_tag_player(entity, CTagPlayer(respawn_position=pygame.Vector2(position)))
        return entity

    def respawn_player(
        self,
        position: pygame.Vector2 | tuple[float, float],
    ) -> int | None:
        if self.player_template is None or self.player_bullet_template is None:
            return None

        return self.create_player(
            position=position,
            player_config=self.player_template,
            bullet_config=self.player_bullet_template,
            bullet_limit=self.player_bullet_limit,
        )

    def create_bullet(
        self,
        position: pygame.Vector2 | tuple[float, float],
        bullet_config: dict[str, object],
        velocity: pygame.Vector2 | tuple[float, float],
    ) -> int:
        entity = self.create_entity()

        self.add_transform(entity, CTransform(pygame.Vector2(position)))
        self.add_surface(entity, self._build_surface_component(bullet_config))
        self.add_velocity(entity, CVelocity(pygame.Vector2(velocity)))
        self.add_tag_bullet(entity, CTagBullet())

        return entity

    def create_enemy_from_template(
        self,
        enemy_name: str,
        position: pygame.Vector2,
    ) -> int:
        enemy_template = self.enemy_templates[enemy_name]
        entity = self.create_entity()

        self.add_transform(entity, CTransform(pygame.Vector2(position)))
        self.add_surface(entity, self._build_surface_component(enemy_template))
        self.add_tag_enemy(entity, CTagEnemy(enemy_type=enemy_name))

        animation_component = self._build_animation_component(
            enemy_template,
            preferred_animation="IDLE",
        )
        if animation_component is not None:
            self.add_animation(entity, animation_component)

        if enemy_template["enemy_kind"] == "hunter":
            self.add_velocity(entity, CVelocity(pygame.Vector2()))
            self.add_hunter_behavior(
                entity,
                CHunterBehavior(
                    origin=pygame.Vector2(position),
                    chase_speed=float(enemy_template["chase_speed"]),
                    return_speed=float(enemy_template["return_speed"]),
                    distance_start_chase=float(enemy_template["distance_start_chase"]),
                    distance_start_return=float(enemy_template["distance_start_return"]),
                ),
            )
            return entity

        speed = random.uniform(
            float(enemy_template["min_speed"]),
            float(enemy_template["max_speed"]),
        )
        angle = random.uniform(0.0, 360.0)
        velocity = pygame.Vector2(speed, 0.0).rotate(angle)
        self.add_velocity(entity, CVelocity(velocity))

        return entity

    def create_explosion(
        self,
        center_position: pygame.Vector2 | tuple[float, float],
    ) -> int:
        entity = self.create_entity()
        frame_size = self.get_template_size(self.explosion_template)
        top_left = pygame.Vector2(center_position) - pygame.Vector2(
            frame_size[0] / 2,
            frame_size[1] / 2,
        )

        self.add_transform(entity, CTransform(top_left))
        self.add_surface(entity, self._build_surface_component(self.explosion_template))

        animation_component = self._build_animation_component(
            self.explosion_template,
            preferred_animation="EXPLODE",
        )
        if animation_component is not None:
            self.add_animation(entity, animation_component)

        self.add_tag_explosion(entity, CTagExplosion())
        return entity

    def create_bullet_from_player(self, target_position: pygame.Vector2) -> int | None:
        player_entity = self.get_player_entity()

        if player_entity is None:
            return None

        input_command = self.input_commands[player_entity]

        if len(self.get_bullet_entities()) >= input_command.bullet_limit:
            return None

        player_rect = self.get_entity_rect(player_entity)
        bullet_size = self.get_template_size(input_command.bullet_template)
        bullet_position = pygame.Vector2(
            player_rect.centerx - bullet_size[0] / 2,
            player_rect.centery - bullet_size[1] / 2,
        )
        bullet_direction = pygame.Vector2(target_position) - pygame.Vector2(player_rect.center)

        if bullet_direction.length_squared() == 0:
            bullet_direction = pygame.Vector2(1, 0)
        else:
            bullet_direction = bullet_direction.normalize()

        bullet_velocity = bullet_direction * input_command.bullet_speed

        return self.create_bullet(
            position=bullet_position,
            bullet_config=input_command.bullet_template,
            velocity=bullet_velocity,
        )

    def destroy_entity(self, entity: int) -> None:
        self.entities.discard(entity)
        self.transforms.pop(entity, None)
        self.surfaces.pop(entity, None)
        self.velocities.pop(entity, None)
        self.input_commands.pop(entity, None)
        self.enemy_spawners.pop(entity, None)
        self.animations.pop(entity, None)
        self.hunter_behaviors.pop(entity, None)
        self.tag_players.pop(entity, None)
        self.tag_bullets.pop(entity, None)
        self.tag_enemies.pop(entity, None)
        self.tag_explosions.pop(entity, None)

    def get_enemy_spawner(self) -> CEnemySpawner | None:
        if not self.enemy_spawners:
            return None

        return next(iter(self.enemy_spawners.values()))

    def get_player_entity(self) -> int | None:
        if not self.tag_players:
            return None

        return next(iter(self.tag_players.keys()))

    def get_enemy_entities(self) -> list[int]:
        return sorted(self.tag_enemies.keys())

    def get_bullet_entities(self) -> list[int]:
        return sorted(self.tag_bullets.keys())

    def get_hunter_entities(self) -> list[int]:
        return sorted(self.hunter_behaviors.keys())

    def get_explosion_entities(self) -> list[int]:
        return sorted(self.tag_explosions.keys())

    def get_movable_entities(self) -> list[int]:
        return [
            entity
            for entity in sorted(self.entities)
            if entity in self.transforms
            and entity in self.surfaces
            and entity in self.velocities
        ]

    def get_renderable_entities(self) -> list[int]:
        return [
            entity
            for entity in sorted(self.entities)
            if entity in self.transforms and entity in self.surfaces
        ]

    def set_animation(self, entity: int, animation_name: str) -> None:
        animation = self.animations.get(entity)

        if animation is None or animation_name not in animation.clips:
            return

        animation.set_animation(animation_name)
        self.sync_animation_frame(entity)

    def sync_animation_frame(self, entity: int) -> None:
        animation = self.animations.get(entity)
        surface = self.surfaces.get(entity)

        if animation is None or surface is None:
            return

        surface.area.x = surface.area.width * animation.current_frame

    def get_entity_rect(self, entity: int) -> pygame.Rect:
        transform = self.transforms[entity]
        surface = self.surfaces[entity]

        return pygame.Rect(
            round(transform.position.x),
            round(transform.position.y),
            surface.area.width,
            surface.area.height,
        )

    def get_entity_center(self, entity: int) -> pygame.Vector2:
        return pygame.Vector2(self.get_entity_rect(entity).center)

    def get_template_size(self, template: dict[str, object]) -> tuple[int, int]:
        if template.get("image_path") is not None:
            texture = self._load_texture(str(template["image_path"]))
            frame_count = 1

            if template.get("animations") is not None:
                frame_count = int(template["animations"]["number_frames"])

            return (texture.get_width() // frame_count, texture.get_height())

        size = template["size"]
        return (int(size[0]), int(size[1]))

    def _build_surface_component(self, template: dict[str, object]) -> CSurface:
        if template.get("image_path") is not None:
            texture = self._load_texture(str(template["image_path"]))
            frame_width, frame_height = self.get_template_size(template)
            return CSurface(
                texture=texture,
                area=pygame.Rect(0, 0, frame_width, frame_height),
            )

        size = self.get_template_size(template)
        texture = pygame.Surface(size, pygame.SRCALPHA)
        texture.fill(tuple(template["color"]))
        return CSurface(texture=texture, area=pygame.Rect(0, 0, size[0], size[1]))

    def _build_animation_component(
        self,
        template: dict[str, object],
        preferred_animation: str,
    ) -> CAnimation | None:
        animation_data = template.get("animations")

        if animation_data is None:
            return None

        clips: dict[str, AnimationClip] = {}

        for clip_data in animation_data["clips"].values():
            clip = AnimationClip(
                name=str(clip_data["name"]),
                start=int(clip_data["start"]),
                end=int(clip_data["end"]),
                framerate=float(clip_data["framerate"]),
                loop=bool(clip_data["loop"]),
            )
            clips[clip.name] = clip

        current_animation = preferred_animation
        if current_animation not in clips:
            current_animation = next(iter(clips))

        return CAnimation(
            clips=clips,
            current_animation=current_animation,
            current_frame=clips[current_animation].start,
        )

    def _load_texture(self, image_path: str) -> pygame.Surface:
        if image_path not in self._image_cache:
            texture_path = self.project_root / image_path
            self._image_cache[image_path] = pygame.image.load(texture_path).convert_alpha()

        return self._image_cache[image_path]
