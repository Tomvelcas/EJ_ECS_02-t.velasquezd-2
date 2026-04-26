from __future__ import annotations

from pathlib import Path

import pygame


class ImageService:
    def __init__(self, project_root: str | Path) -> None:
        self.project_root = Path(project_root)
        self._cache: dict[str, pygame.Surface] = {}

    def load(self, image_path: str) -> pygame.Surface:
        if image_path not in self._cache:
            texture_path = self.project_root / image_path
            self._cache[image_path] = pygame.image.load(texture_path).convert_alpha()

        return self._cache[image_path]


class FontService:
    def __init__(self, project_root: str | Path) -> None:
        self.project_root = Path(project_root)
        self._cache: dict[tuple[str, int], pygame.font.Font] = {}

    def load(self, font_path: str, size: int) -> pygame.font.Font:
        key = (font_path, size)

        if key not in self._cache:
            self._cache[key] = pygame.font.Font(self.project_root / font_path, size)

        return self._cache[key]


class TextService:
    def __init__(self, font_service: FontService) -> None:
        self.font_service = font_service

    def render(
        self,
        text: str,
        font_path: str,
        size: int,
        color: tuple[int, int, int],
    ) -> pygame.Surface:
        font = self.font_service.load(font_path, size)
        return font.render(text, True, color)


class SoundService:
    def __init__(self, project_root: str | Path) -> None:
        self.project_root = Path(project_root)
        self._cache: dict[str, pygame.mixer.Sound] = {}
        self.enabled = True

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except pygame.error:
            self.enabled = False

    def load(self, sound_path: str) -> pygame.mixer.Sound | None:
        if not self.enabled:
            return None

        if sound_path not in self._cache:
            try:
                self._cache[sound_path] = pygame.mixer.Sound(
                    self.project_root / sound_path
                )
            except pygame.error:
                self.enabled = False
                return None

        return self._cache[sound_path]

    def play(self, sound_path: str | None) -> None:
        if sound_path is None:
            return

        sound = self.load(sound_path)
        if sound is not None:
            sound.play()
