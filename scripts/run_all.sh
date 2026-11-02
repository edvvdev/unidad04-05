#!/usr/bin/env bash
# Ejecuta todo el flujo del Ejercicio 05 (motor recomendador reproducible).
#
#   ./scripts/run_all.sh            # todo: entorno → datos → auditoría → notebook → PDF
#   SKIP_NOTEBOOK=1 ./scripts/run_all.sh   # omite el notebook (si solo quieres los scripts)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "==> 1/5. Entorno (uv)"
uv python install 3.12
uv sync
# Jupyter y reportlab no están en el grupo dev del proyecto base: se instalan aparte
uv pip install --python .venv/bin/python jupyter nbformat ipykernel reportlab

echo "==> 2/5. Pruebas (esperado: 7 passed)"
uv run pytest -q

echo "==> 3/5. Datos y auditoría (MovieLens no se versiona: se descarga aquí)"
uv run python scripts/download_data.py
uv run python scripts/audit_data.py

echo "==> 4/5. Notebook del Ejercicio 05 (ejecutado de principio a fin)"
if [ "${SKIP_NOTEBOOK:-0}" != "1" ]; then
  uv run python -m jupyter nbconvert --to notebook --execute --inplace \
    --ExecutePreprocessor.timeout=3600 notebooks/01_ejercicio05_recomendadores.ipynb
else
  echo "    OMITIDO por SKIP_NOTEBOOK=1"
fi

echo "==> 5/5. PDF breve de entrega"
REPO_URL="${REPO_URL:-https://github.com/edvvdev/unidad04-05}" \
  uv run python scripts/build_ejercicio05_pdf.py

echo "Listo. Revisa 'git status' y completa los campos PENDIENTE del PDF (nombre y matrícula)."
