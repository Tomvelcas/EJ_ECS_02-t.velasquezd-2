from __future__ import annotations

from typing import Any


class ServiceLocator:
    _services: dict[type[object], object] = {}

    @classmethod
    def register(cls, service_type: type[object], service: object) -> None:
        cls._services[service_type] = service

    @classmethod
    def get(cls, service_type: type[object]) -> Any:
        return cls._services[service_type]

    @classmethod
    def has(cls, service_type: type[object]) -> bool:
        return service_type in cls._services

    @classmethod
    def clear(cls) -> None:
        cls._services.clear()
