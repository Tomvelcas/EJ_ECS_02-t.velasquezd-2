from __future__ import annotations

import random

import pygame

from src.ecs.components.c_enemy_spawner import CEnemySpawner
from src.ecs.components.c_input_command import CInputCommand
from src.ecs.components.c_surface import CSurface, Color
from src.ecs.components.c_tag_bullet import CTagBullet
from src.ecs.components.c_tag_enemy import CTagEnemy
from src.ecs.components.c_tag_player import CTagPlayer
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity


class World:
    def __init__(
        self,
        enemy_templates: dict[str, dict[str, object]],
    ) -> None:
        self._next_entity_id = 0
        self.entities: set[int] = set()
        self.transforms: dict[int, CTransform] = {}
        self.surfaces: dict[int, CSurface] = {}
        self.velocities: dict[int, CVelocity] = {}
        self.input_commands: dict[int, CInputCommand] = {}
        self.enemy_spawners: dict[int, CEnemySpawner] = {}
        self.tag_players: dict[int, CTagPlayer] = {}
        self.tag_bullets: dict[int, CTagBullet] = {}
        self.tag_enemies: dict[int, CTagEnemy] = {}
        self.enemy_templates = enemy_templates

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

    def add_tag_player(self, entity: int, component: CTagPlayer) -> None:
        self.tag_players[entity] = component

    def add_tag_bullet(self, entity: int, component: CTagBullet) -> None:
        self.tag_bullets[entity] = component

    def add_tag_enemy(self, entity: int, component: CTagEnemy) -> None:
        self.tag_enemies[entity] = component

    def create_enemy(
        self,
        position: pygame.Vector2 | tuple[float, float],
        size: tuple[int, int],
        velocity: pygame.Vector2 | tuple[float, float],
        color: Color,
    ) -> int | None:
        entity = self.create_entity()
        surface = pygame.Surface(size)
        surface.fill(color)

        self.add_transform(entity, CTransform(pygame.Vector2(position)))
        self.add_surface(entity, CSurface(surface, color))
        self.add_velocity(entity, CVelocity(pygame.Vector2(velocity)))
        self.add_tag_enemy(entity, CTagEnemy())

        return entity

    def create_player(
        self,
        position: pygame.Vector2 | tuple[float, float],
        player_config: dict[str, object],
        bullet_config: dict[str, object],
        bullet_limit: int,
    ) -> int:
        entity = self.create_entity()
        surface = pygame.Surface(player_config["size"])
        surface.fill(player_config["color"])

        self.add_transform(entity, CTransform(pygame.Vector2(position)))
        self.add_surface(entity, CSurface(surface, player_config["color"]))
        self.add_velocity(entity, CVelocity(pygame.Vector2()))
        self.add_input_command(
            entity,
            CInputCommand(
                move_speed=player_config["speed"],
                bullet_size=bullet_config["size"],
                bullet_color=bullet_config["color"],
                bullet_speed=bullet_config["speed"],
                bullet_limit=bullet_limit,
            ),
        )
        self.add_tag_player(entity, CTagPlayer())

        return entity

    def create_bullet(
        self,
        position: pygame.Vector2 | tuple[float, float],
        size: tuple[int, int],
        color: Color,
        velocity: pygame.Vector2 | tuple[float, float],
    ) -> int:
        entity = self.create_entity()
        surface = pygame.Surface(size)
        surface.fill(color)

        self.add_transform(entity, CTransform(pygame.Vector2(position)))
        self.add_surface(entity, CSurface(surface, color))
        self.add_velocity(entity, CVelocity(pygame.Vector2(velocity)))
        self.add_tag_bullet(entity, CTagBullet())

        return entity

    def create_enemy_from_template(
        self,
        enemy_name: str,
        position: pygame.Vector2,
    ) -> int | None:
        enemy_template = self.enemy_templates[enemy_name]
        speed = random.uniform(
            enemy_template["min_speed"],
            enemy_template["max_speed"],
        )
        angle = random.uniform(0.0, 360.0)
        velocity = pygame.Vector2(speed, 0.0).rotate(angle)

        return self.create_enemy(
            position=position,
            size=enemy_template["size"],
            velocity=velocity,
            color=enemy_template["color"],
        )

    def create_bullet_from_player(self, target_position: pygame.Vector2) -> int | None:
        player_entity = self.get_player_entity()

        if player_entity is None:
            return None

        input_command = self.input_commands[player_entity]

        if len(self.get_bullet_entities()) >= input_command.bullet_limit:
            return None

        player_transform = self.transforms[player_entity]
        player_surface = self.surfaces[player_entity]
        player_rect = player_surface.surface.get_rect(
            topleft=(player_transform.position.x, player_transform.position.y)
        )

        bullet_position = pygame.Vector2(
            player_rect.centerx - input_command.bullet_size[0] / 2,
            player_rect.centery - input_command.bullet_size[1] / 2,
        )
        bullet_direction = pygame.Vector2(target_position) - pygame.Vector2(player_rect.center)

        if bullet_direction.length_squared() == 0:
            bullet_direction = pygame.Vector2(1, 0)
        else:
            bullet_direction = bullet_direction.normalize()

        bullet_velocity = bullet_direction * input_command.bullet_speed

        return self.create_bullet(
            position=bullet_position,
            size=input_command.bullet_size,
            color=input_command.bullet_color,
            velocity=bullet_velocity,
        )

    def destroy_entity(self, entity: int) -> None:
        self.entities.discard(entity)
        self.transforms.pop(entity, None)
        self.surfaces.pop(entity, None)
        self.velocities.pop(entity, None)
        self.input_commands.pop(entity, None)
        self.enemy_spawners.pop(entity, None)
        self.tag_players.pop(entity, None)
        self.tag_bullets.pop(entity, None)
        self.tag_enemies.pop(entity, None)

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
