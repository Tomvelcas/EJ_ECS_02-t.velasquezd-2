# Guia de ejecucion y distribucion

## Ejecutar local

```bash
python3 main.py
```

Si falta pygame:

```bash
python3 -m pip install pygame-ce
python3 main.py
```

## Ejecutable para macOS

Instalar PyInstaller:

```bash
python3 -m pip install pyinstaller
```

Opcion recomendada para macOS: generar una app:

```bash
python3 -m PyInstaller --windowed --name RocketHunter --add-data ./assets:./assets main.py
```

La app queda en:

```text
dist/RocketHunter.app
```

Para probarla:

```bash
open dist/RocketHunter.app
```

Opcion alternativa: generar un binario de un solo archivo:

```bash
python3 -m PyInstaller --noconsole --add-data ./assets:./assets --onefile main.py
```

El archivo queda en:

```text
dist/main
```

Para probarlo:

```bash
./dist/main
```

Si macOS bloquea el ejecutable o la app, probar desde Finder con click derecho > Abrir,
o desde terminal, ajustando la ruta segun lo que se vaya a probar:

```bash
xattr -dr com.apple.quarantine dist/main
./dist/main
```

## Version web con pygbag

Instalar pygbag:

```bash
python3 -m pip install pygbag
```

Generar y servir build web:

```bash
python3 -m pygbag --ume_block 0 main.py
```

Abrir en el navegador:

```text
http://localhost:8000
```

Para ver errores internos de Python en el navegador:

```text
http://localhost:8000/#debug
```

El build web queda normalmente en:

```text
build/web/
```

Esa carpeta se puede subir como HTML/Web a itch.io.
