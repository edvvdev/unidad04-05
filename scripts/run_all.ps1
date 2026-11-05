# Ejecuta todo el flujo del Ejercicio 05 (motor recomendador reproducible).
#   .\scripts\run_all.ps1
#   $env:SKIP_NOTEBOOK = "1"   # omite el notebook
# El paso 6 (frontera de Pareto multistamillas) entrena 18 configuraciones con 3 repeticiones
# cada una: tarda varios minutos en CPU.
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "==> 1/9. Entorno (uv)" -ForegroundColor Cyan
uv python install 3.12
uv sync
# Jupyter y reportlab no están en el grupo dev del proyecto base: se instalan aparte
uv pip install --python .venv/bin/python jupyter nbformat ipykernel reportlab

Write-Host "==> 2/9. Datos y auditoría (MovieLens no se versiona: se descarga aquí)" -ForegroundColor Cyan
uv run python scripts/download_data.py
uv run python scripts/audit_data.py

Write-Host "==> 3/9. LAB08 · recomendación por contenido (tres consultas)" -ForegroundColor Cyan
uv run python scripts/lab08_content.py --title "Toy Story (1995)"      --out content_recommendations_toy_story.csv
uv run python scripts/lab08_content.py --title "Matrix, The (1999)"   --out content_recommendations_matrix.csv
uv run python scripts/lab08_content.py --title "Godfather, The (1972)" --out content_recommendations_godfather.csv

Write-Host "==> 4/9. LAB09 · híbrido (α=0,75 y α=0,25)" -ForegroundColor Cyan
uv run python scripts/lab09_hybrid.py --factors 20 --epochs 12 --alpha 0.75 --out hybrid_metrics.json
Copy-Item reports/hybrid_metrics.json reports/hybrid_metrics_alpha075.json -Force
uv run python scripts/lab09_hybrid.py --factors 20 --epochs 12 --alpha 0.25 --out hybrid_metrics_alpha025.json

Write-Host "==> 5/9. LAB09 · perfiles de usuario (historial amplio, pequeño y usuario nuevo)" -ForegroundColor Cyan
uv run python scripts/lab09_profiles.py

Write-Host "==> 6/9. LAB09 · frontera de Pareto multistamillas (18 configuraciones; varios minutos)" -ForegroundColor Cyan
uv run python scripts/lab09_pareto.py

Write-Host "==> 7/9. Notebook del Ejercicio 05 (ejecutado de principio a fin)" -ForegroundColor Cyan
if ($env:SKIP_NOTEBOOK -ne "1") {
    uv run python -m jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=3600 notebooks/01_ejercicio05_recomendadores.ipynb
} else {
    Write-Host "    OMITIDO por SKIP_NOTEBOOK=1" -ForegroundColor DarkGray
}

Write-Host "==> 8/9. PDF breve de entrega" -ForegroundColor Cyan
if (-not $env:REPO_URL) { $env:REPO_URL = "https://github.com/edvvdev/unidad04-05" }
uv run python scripts/build_ejercicio05_pdf.py

Write-Host "==> 9/9. Pruebas (esperado: 7 passed)" -ForegroundColor Cyan
uv run pytest -q

Write-Host "==> Resumen final de la corrida" -ForegroundColor Cyan
uv run python scripts/resumen_ejecutable.py

Write-Host "Listo. Revisa 'git status' y el PDF (nombre y matrícula ya vienen fijados en el builder)." -ForegroundColor Green
