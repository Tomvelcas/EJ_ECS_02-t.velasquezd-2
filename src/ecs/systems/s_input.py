from __future__ import annotations

import pygame

from src.ecs.components.c_input_command import (
    PLAYER_DOWN,
    PLAYER_FIRE,
    PLAYER_LEFT,
    PLAYER_ROCKET,
    PLAYER_RIGHT,
    PLAYER_UP,
    CInputCommand,
    InputAction,
)
from src.ecs.world import World


def system_input(world: World, events: list[pygame.event.Event]) -> None:
    player_entity = world.get_player_entity()

    if player_entity is None or player_entity not in world.input_commands:
        return

    input_command = world.input_commands[player_entity]
    input_command.pending_actions.clear()
    _collect_keyboard_actions(input_command)
    _collect_event_actions(input_command, events)
    _execute_actions(world, player_entity, input_command)


def _collect_keyboard_actions(input_command: CInputCommand) -> None:
    pressed_keys = pygame.key.get_pressed()

    if pressed_keys[pygame.K_LEFT] or pressed_keys[pygame.K_a]:
        input_command.pending_actions.append(InputAction(PLAYER_LEFT))

    if pressed_keys[pygame.K_RIGHT] or pressed_keys[pygame.K_d]:
        input_command.pending_actions.append(InputAction(PLAYER_RIGHT))

    if pressed_keys[pygame.K_UP] or pressed_keys[pygame.K_w]:
        input_command.pending_actions.append(InputAction(PLAYER_UP))

    if pressed_keys[pygame.K_DOWN] or pressed_keys[pygame.K_s]:
        input_command.pending_actions.append(InputAction(PLAYER_DOWN))


def _collect_event_actions(
    input_command: CInputCommand,
    events: list[pygame.event.Event],
) -> None:
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            input_command.pending_actions.append(
                InputAction(PLAYER_FIRE, pygame.Vector2(event.pos))
            )

        if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            input_command.pending_actions.append(InputAction(PLAYER_ROCKET))


def _execute_actions(
    world: World,
    player_entity: int,
    input_command: CInputCommand,
) -> None:
    move_direction = pygame.Vector2()

    for action in input_command.pending_actions:
        COMMAND_HANDLERS[action.name](
            world,
            player_entity,
            input_command,
            move_direction,
            action,
        )

    player_velocity = world.velocities[player_entity].velocity

    if move_direction.length_squared() > 0:
        move_direction = move_direction.normalize() * input_command.move_speed

    player_velocity.x = move_direction.x
    player_velocity.y = move_direction.y


def _command_left(
    world: World,
    player_entity: int,
    input_command: CInputCommand,
    move_direction: pygame.Vector2,
    action: InputAction,
) -> None:
    move_direction.x -= 1


def _command_right(
    world: World,
    player_entity: int,
    input_command: CInputCommand,
    move_direction: pygame.Vector2,
    action: InputAction,
) -> None:
    move_direction.x += 1


def _command_up(
    world: World,
    player_entity: int,
    input_command: CInputCommand,
    move_direction: pygame.Vector2,
    action: InputAction,
) -> None:
    move_direction.y -= 1


def _command_down(
    world: World,
    player_entity: int,
    input_command: CInputCommand,
    move_direction: pygame.Vector2,
    action: InputAction,
) -> None:
    move_direction.y += 1


def _command_fire(
    world: World,
    player_entity: int,
    input_command: CInputCommand,
    move_direction: pygame.Vector2,
    action: InputAction,
) -> None:
    if action.target_position is None:
        return

    world.create_bullet_from_player(action.target_position)


def _command_rocket(
    world: World,
    player_entity: int,
    input_command: CInputCommand,
    move_direction: pygame.Vector2,
    action: InputAction,
) -> None:
    world.create_rocket_from_player()


COMMAND_HANDLERS = {
    PLAYER_LEFT: _command_left,
    PLAYER_RIGHT: _command_right,
    PLAYER_UP: _command_up,
    PLAYER_DOWN: _command_down,
    PLAYER_FIRE: _command_fire,
    PLAYER_ROCKET: _command_rocket,
}
