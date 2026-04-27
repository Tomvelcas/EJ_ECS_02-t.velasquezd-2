# Guia de ejecucion, verificacion y distribucion

Este documento explica como correr el juego, verificar que esta listo para
entrega y generar builds para itch.io.

## Estado recomendado para la entrega

Para la entrega del curso se recomienda subir el codigo fuente del repositorio
y publicar el juego en itch.io como version web HTML. El `README.txt` debe
contener el enlace publico de itch.io.

No es necesario incluir en el ZIP del codigo los artefactos generados por build.
Estos archivos se pueden recrear y estan ignorados por git:

- `build/`
- `dist/`
- `RocketHunter.app/`
- `RocketHunter-web.zip`
- `RocketHunter-mac.zip`
- `*.spec`
- `__pycache__/`
- `.DS_Store`

## Requisitos

- Python 3.9 o superior
- pygame-ce

Instalar dependencias:

```bash
python3 -m pip install -r requirements.txt
```

## Ejecutar localmente

Desde la raiz del repositorio:

```bash
python3 main.py
```

Controles:

- `WASD` o flechas: mover el jugador
- Click izquierdo: disparar
- `E`: rocket autodirigido
- `P`: pausar o reanudar

## Verificacion rapida

Compilar todos los archivos Python:

```bash
python3 -m py_compile main.py src/engine/*.py src/ecs/components/*.py src/ecs/systems/*.py src/ecs/world.py
```

Validar los JSON:

```bash
for f in assets/cfg/*.json; do python3 -m json.tool "$f" >/dev/null || exit 1; done
```

Smoke test sin abrir ventana:

```bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python3 - <<'PY'
from src.engine.game_engine import GameEngine

game = GameEngine()
game._create()
game._update()
world = game.world
rocket = world.create_rocket_from_player()
print("texts:", len(world.texts))
print("rocket:", rocket)
print("rocket_size:", world.get_entity_rect(rocket).size if rocket is not None else None)
game._clean()
PY
```

## Build web para itch.io

Instalar pygbag:

```bash
python3 -m pip install pygbag
```

Generar y servir la version web:

```bash
python3 -m pygbag --ume_block 0 main.py
```

Abrir en el navegador:

```text
http://localhost:8000
```

Si hay errores, usar la consola interna de pygbag:

```text
http://localhost:8000/#debug
```

El build queda en:

```text
build/web/
```

Crear el ZIP para itch.io:

```bash
cd build/web
zip -r ../../RocketHunter-web.zip .
```

En itch.io, seleccionar:

- `Kind of project`: `HTML`
- Subir `RocketHunter-web.zip`
- Marcar el archivo como jugable en navegador
- Embed recomendado: `640 x 360`

El archivo `pygbag.ini` evita que pygbag empaquete builds de macOS, zips,
caches y otros artefactos que no pertenecen al juego web.

## Build macOS

Disclaimer: los builds de PyInstaller son especificos de la plataforma. Un
build de macOS debe generarse en macOS. Un `.exe` de Windows debe generarse
desde Windows. Para esta entrega, la version web en itch.io es la opcion mas
portable y recomendada.

Instalar PyInstaller:

```bash
python3 -m pip install pyinstaller
```

Generar una app de macOS:

```bash
python3 -m PyInstaller --windowed --name RocketHunter --add-data ./assets:./assets main.py
```

La app queda en:

```text
dist/RocketHunter.app
```

Probar la app:

```bash
open dist/RocketHunter.app
```

Si macOS bloquea la app:

```bash
xattr -dr com.apple.quarantine dist/RocketHunter.app
open dist/RocketHunter.app
```

Crear ZIP descargable para itch.io:

```bash
ditto -c -k --sequesterRsrc --keepParent dist/RocketHunter.app RocketHunter-mac.zip
```

Ese ZIP se puede subir a itch.io como archivo descargable para macOS, pero no
debe commitearse.

## Build Windows

No se recomienda generar Windows desde macOS. Para crear un `.exe`, abrir el
repositorio en Windows y ejecutar:

```bash
py -m pip install -r requirements.txt
py -m pip install pyinstaller
py -m PyInstaller --noconsole --add-data "assets;assets" --onefile main.py
```

El ejecutable queda normalmente en:

```text
dist/main.exe
```

Nota: en Windows, PyInstaller usa `;` en `--add-data`; en macOS/Linux usa `:`.

## Publicacion en itch.io

Despues de publicar el juego, actualizar `README.txt` con el enlace real. El
enlace actual esperado es:

```text
https://tomvelcas.itch.io/rocketfantasy-e04-misw
```

Configuracion recomendada en itch.io:

- `Classification`: `Games`
- `Kind of project`: `HTML`
- `Pricing`: `$0 or donate` o `No payments`
- `Visibility`: `Public`
- `Unlisted in search & browse`: opcional, recomendado si solo se compartira por enlace
- `Disable new downloads & purchases`: desactivado

## Que commitear

Si debe ir en git:

- `main.py`
- `src/`
- `assets/`
- `README.txt`
- `BUILD.md`
- `requirements.txt`
- `pygbag.ini`
- `.gitignore`

No debe ir en git:

- `build/`
- `dist/`
- `RocketHunter.app/`
- `RocketHunter-web.zip`
- `RocketHunter-mac.zip`
- `*.spec`
- `__pycache__/`
- `.DS_Store`
