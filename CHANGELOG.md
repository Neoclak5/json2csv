# Changelog

Todos los cambios notables de este proyecto se documentan aquí.
Formato basado en [Keep a Changelog](https://keepachangelog.com/es/1.0.0/).

## [0.1.0] - 2026-06-20

### Agregado

- Módulo `converter.py` con `convert()`, `load_json()`, `normalize_records()`, `write_csv()` y `_flatten()`
- Jerarquía de excepciones tipadas: `Json2CsvError`, `InputFileNotFoundError`, `InvalidJsonError`, `UnsupportedStructureError`
- CLI `json2csv` con argumentos `input` y `--output / -o`
- Aplanamiento automático de objetos anidados con notación de punto
- Serialización de arrays dentro de registros como strings JSON
- Suite de pruebas unitarias e integración con cobertura de ramas ≥ 85%
- Pipeline CI/CD en GitHub Actions: ruff, black, pycodestyle, pydocstyle, mypy, pyright, pytest, bandit, pdoc
- Documentación de la API generada con pdoc
- Licencia MIT
