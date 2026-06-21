# CONTEXT — json2csv

Este archivo es para uso con asistentes de IA (Vibe Coding).
Describe el proyecto de forma suficiente para que un asistente pueda
contribuir sin leer todo el código.

## Propósito

`json2csv` convierte archivos JSON a formato CSV.
Es el proyecto espejo de `csv2json` visto en clase (Taller de Calidad de Software, UFASTA 2026).

## Estructura

```
src/json2csv/
    __init__.py      — API pública: expone convert() y las excepciones
    converter.py     — Toda la lógica: _flatten, load_json, normalize_records, write_csv, convert
    cli.py           — Interfaz de línea de comandos (argparse)
tests/
    test_converter.py — Tests unitarios e integración de converter.py
    test_cli.py       — Tests de main() y _build_parser()
```

## Decisiones de diseño clave

- **Sin dependencias de runtime**: usa solo `json`, `csv`, `pathlib`, `argparse` de la stdlib.
- **Jerarquía de excepciones**: todas derivan de `Json2CsvError` para que el caller pueda atrapar una sola excepción base.
- **Aplanamiento con dot-notation**: `{"address": {"city": "BA"}}` → columna `address.city`. Los arrays se serializan como JSON string.
- **Layout src/**: el paquete vive en `src/json2csv/`. Instalar con `pip install -e .` para que los tests lo encuentren.
- **Cobertura de ramas ≥ 85%**: configurada en `pyproject.toml` con `--cov-fail-under=85`.

## Restricciones del proyecto

- Python ≥ 3.11
- PEP 8 (pycodestyle), PEP 257 con convención Google (pydocstyle)
- Type-checked con mypy y pyright
- Sin Trufflehog en el pipeline de seguridad (usar solo bandit)

## Comandos frecuentes

```bash
pip install -e .              # instalar en modo editable
pytest                        # correr tests + cobertura
ruff check src/ tests/        # linting
black src/ tests/             # formatear
pydocstyle src/               # verificar docstrings PEP 257
mypy src/                     # tipos
bandit -r src/ -ll            # seguridad
pdoc --output-dir docs/ src/json2csv   # documentación
```

## Flujo de entrada/salida

```
JSON file  →  load_json()  →  normalize_records()  →  write_csv()  →  CSV file
               (parse)         (flatten + wrap)        (DictWriter)
```
