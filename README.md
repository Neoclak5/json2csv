# json2csv

Herramienta de línea de comandos para convertir archivos JSON a formato CSV.

## Características

- Convierte arrays JSON de objetos a CSV, un objeto por fila
- Aplana objetos anidados usando notación de punto (`address.city`)
- Serializa arrays dentro de registros como strings JSON
- Acepta también un único objeto JSON como entrada
- Sin dependencias de runtime (solo biblioteca estándar de Python)

## Instalación

```bash
git clone https://github.com/TU_USUARIO/json2csv.git
cd json2csv
python3 -m venv .venv          # usar python3 (no python, que puede ser 3.10 viejo)
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/Mac
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

## Uso

```bash
json2csv data.json --output data.csv
json2csv records.json -o output/results.csv
```

### Ejemplo

Dado `sample.json`:
```json
[
  {"id": 1, "name": "Alice", "address": {"city": "Buenos Aires"}},
  {"id": 2, "name": "Bob",   "address": {"city": "Córdoba"}}
]
```

Ejecutar:
```bash
json2csv sample.json -o sample.csv
```

Produce `sample.csv`:
```
id,name,address.city
1,Alice,Buenos Aires
2,Bob,Córdoba
```

## Uso programático

```python
from json2csv import convert

rows = convert("data.json", "output.csv")
print(f"Se escribieron {rows} filas.")
```

## Desarrollo

```bash
# Ejecutar la suite completa de calidad
ruff check src/ tests/
black --check src/ tests/
pycodestyle --max-line-length=88 src/
pydocstyle src/
mypy src/
pyright src/
pytest
bandit -r src/ -ll
pdoc --output-dir docs/ src/json2csv
```

## Pipeline CI/CD

Cada push y pull request ejecuta automáticamente en GitHub Actions:

- **Ruff** — linting
- **Black** — formato consistente
- **Pycodestyle** — conformidad PEP 8
- **Pydocstyle** — convenciones PEP 257 para docstrings
- **MyPy** y **PyRight** — verificación de tipos estática
- **Pytest** — suite de pruebas con cobertura de ramas ≥ 85%
- **Bandit** — análisis de seguridad estático
- **pdoc** — generación de documentación de la API

## Versión

0.1.0 — ver [CHANGELOG.md](CHANGELOG.md)

## Licencia

MIT — ver [LICENSE](LICENSE)
