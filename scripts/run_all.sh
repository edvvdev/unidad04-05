#!/usr/bin/env bash
# Ejecuta todo el flujo del Ejercicio 05 (motor recomendador reproducible).
#
#   ./scripts/run_all.sh            # todo: entorno → datos → LAB08/LAB09 → notebook → PDF → pruebas
#   SKIP_NOTEBOOK=1 ./scripts/run_all.sh   # omite el notebook (si solo quieres los scripts)
#
# El paso 6 (frontera de Pareto multistamillas) entrena 18 configuraciones con 3 repeticiones
# cada una: tarda varios minutos en CPU.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "==> 1/9. Entorno (uv)"
uv python install 3.12
uv sync
# Jupyter y reportlab no están en el grupo dev del proyecto base: se instalan aparte
uv pip install --python .venv/bin/python jupyter nbformat ipykernel reportlab

echo "==> 2/9. Datos y auditoría (MovieLens no se versiona: se descarga aquí)"
uv run python scripts/download_data.py
uv run python scripts/audit_data.py

echo "==> 3/9. LAB08 · recomendación por contenido (tres consultas)"
uv run python scripts/lab08_content.py --title "Toy Story (1995)"      --out content_recommendations_toy_story.csv
uv run python scripts/lab08_content.py --title "Matrix, The (1999)"   --out content_recommendations_matrix.csv
uv run python scripts/lab08_content.py --title "Godfather, The (1972)" --out content_recommendations_godfather.csv

echo "==> 4/9. LAB09 · híbrido (α=0,75 y α=0,25)"
uv run python scripts/lab09_hybrid.py --factors 20 --epochs 12 --alpha 0.75 --out hybrid_metrics.json
cp reports/hybrid_metrics.json reports/hybrid_metrics_alpha075.json
uv run python scripts/lab09_hybrid.py --factors 20 --epochs 12 --alpha 0.25 --out hybrid_metrics_alpha025.json

echo "==> 5/9. LAB09 · perfiles de usuario (historial amplio, pequeño y usuario nuevo)"
uv run python scripts/lab09_profiles.py

echo "==> 6/9. LAB09 · frontera de Pareto multistamillas (18 configuraciones; varios minutos)"
uv run python scripts/lab09_pareto.py

echo "==> 7/9. Notebook del Ejercicio 05 (ejecutado de principio a fin)"
if [ "${SKIP_NOTEBOOK:-0}" != "1" ]; then
  uv run python -m jupyter nbconvert --to notebook --execute --inplace \
    --ExecutePreprocessor.timeout=3600 notebooks/01_ejercicio05_recomendadores.ipynb
else
  echo "    OMITIDO por SKIP_NOTEBOOK=1"
fi

echo "==> 8/9. PDF breve de entrega"
REPO_URL="${REPO_URL:-https://github.com/edvvdev/unidad04-05}" \
  uv run python scripts/build_ejercicio05_pdf.py

echo "==> 9/9. Pruebas (esperado: 7 passed)"
uv run pytest -q

echo "==> Resumen final de la corrida"
uv run python scripts/resumen_ejecutable.py

echo "Listo. Revisa 'git status' y el PDF (nombre y matrícula ya vienen fijados en el builder)."
