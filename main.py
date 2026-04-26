import asyncio
import os
import sys
from pathlib import Path

import pygame  # noqa: F401

from src.engine.game_engine import GameEngine


if __name__ == "__main__":
    os.chdir(Path(__file__).resolve().parent)
    game_engine = GameEngine()

    if sys.platform == "emscripten":
        asyncio.run(game_engine.run_async())
    else:
        game_engine.run()
