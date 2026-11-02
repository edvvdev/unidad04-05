# INF-8239 · Ejercicio 05 · Motor recomendador reproducible

Autor académico: Edwin Ramón José Nolasco · Repositorio: https://github.com/edvvdev/unidad04-05

Consolida LAB08 y LAB09 (proyecto único, según el manual de la Unidad 03) en una entrega ejecutable:
corpus y auditoría, baseline de popularidad, recomendación por contenido, factorización con corte
temporal, sistema híbrido, usuarios fríos y frontera de Pareto. MovieLens *Latest Small* se descarga
con script y **no se versiona en Git** (no se redistribuye).

## Inicio

```bash
uv python install 3.12
uv sync
uv run pytest -q                                  # 7 passed
uv run python scripts/download_data.py            # imprime el SHA-256
uv run python scripts/audit_data.py               # auditoría + reports/audit_summary.json
```

## Entrega del Ejercicio 05

| Elemento | Dónde está |
|---|---|
| Notebook ejecutado | `notebooks/01_ejercicio05_recomendadores.ipynb` (19 celdas, con salidas) |
| Código reutilizable | `src/inf8239_u03/` (`data`, `recommenders`, `hybrid`, `metrics`) |
| Pruebas | `tests/` (`uv run pytest -q` → 7 passed) |
| Métricas y figuras | `reports/` |
| Requisitos | `requirements.txt` y `requirements-dev.txt` (exportados con `uv export`) |
| PDF breve de entrega | `docs/EJERCICIO_05_PDF_BRIEF.pdf` |
| Declaración de IA | `AI_USE_DECLARATION.md` |

Para ejecutar el notebook de principio a fin:

```bash
uv pip install --python .venv/bin/python jupyter nbformat ipykernel reportlab   # o: uv sync --group dev
uv run python -m jupyter nbconvert --to notebook --execute --inplace \
  --ExecutePreprocessor.timeout=3600 notebooks/01_ejercicio05_recomendadores.ipynb
uv run python scripts/build_ejercicio05_pdf.py
```

## Laboratorios

```bash
# LAB08 · baseline de popularidad y recomendación por contenido (tres consultas)
uv run python scripts/lab08_content.py --title "Toy Story (1995)"      --out content_recommendations_toy_story.csv
uv run python scripts/lab08_content.py --title "Matrix, The (1999)"   --out content_recommendations_matrix.csv
uv run python scripts/lab08_content.py --title "Godfather, The (1972)" --out content_recommendations_godfather.csv

# LAB09 · factorización, corte temporal y sistema híbrido
uv run python scripts/lab09_hybrid.py --factors 20 --epochs 12 --alpha 0.75
uv run python scripts/lab09_hybrid.py --factors 20 --epochs 12 --alpha 0.25
uv run python scripts/lab09_profiles.py            # tres perfiles de usuario
uv run python scripts/lab09_pareto.py              # tres semillas + frontera de Pareto

# Aplicación local
uv run streamlit run app/streamlit_app.py
```

## Resultados de referencia (2026-11-02, CPU, semilla 42)

| Evidencia | Archivo | Resultado |
|---|---|---|
| Dataset | `reports/audit_summary.json` | 100.836 valoraciones · 610 usuarios · 9.742 películas · densidad 1,70 % |
| Baseline de popularidad | `reports/popular_top10.csv` | *The Shawshank Redemption* (4,3952) · *The Godfather* (4,2427) · *Fight Club* (4,2327) |
| Contenido (3 consultas) | `reports/content_recommendations_*.csv` | 10 películas con `content_score` 1,0 por coincidencia exacta de géneros |
| Híbrido α=0,75 | `reports/hybrid_metrics.json` | RMSE 1,0264 · HitRate@10 0,03748 · cobertura 7,75 % · 7,54 s · 1.883 KB |
| Híbrido α=0,25 | `reports/hybrid_metrics_alpha025.json` | RMSE 1,0264 · HitRate@10 0,03237 · cobertura 10,65 % |
| Tres perfiles | `reports/profile_recommendations.csv` | historial amplio (2.697 valoraciones), historial pequeño (19), usuario nuevo (fallback) |
| Pareto (3 semillas × 3 tamaños × 2 α) | `reports/pareto_results.csv`, `reports/pareto.png` | frontera: 10 factores con α=0,75 (semillas 7 y 2024) y 20 factores con α=0,75 (semilla 2024); tiempo = mediana de 3 repeticiones |

### Tabla consolidada del Ejercicio 05 (`reports/pareto_results.csv`)

| Configuración | HitRate@10 | Cobertura | RMSE | Ajuste (s) | Modelo (KB) |
|---|---|---|---|---|---|
| mf40 α=0,75 | 0,03918 | 10,06 % | 1,0211 | 7,92 | 3.494 |
| mf20 α=0,75 | 0,03748 | 7,75 % | 1,0264 | 7,52 | 1.883 |
| mf10 α=0,75 | 0,03066 | 5,77 % | 1,0337 | 7,45 | 1.077 |
| mf20 α=0,25 | 0,03237 | 10,65 % | 1,0264 | 7,52 | 1.883 |
| mf10 α=0,25 | 0,02896 | 8,38 % | 1,0337 | 7,45 | 1.077 |
| mf40 α=0,25 | 0,02726 | 12,27 % | 1,0211 | 7,92 | 3.494 |
| contenido (referencia) | 0,00000 | 19,07 % | — | — | — |
| popularidad (referencia) | 0,02131 | 0,10 % | — | — | — |

Lectura: `alpha=0,75` (más peso colaborativo) gana en acierto y **pierde** cobertura en las tres
comparaciones; el contenido tiene la mayor cobertura pero acierto nulo, y la popularidad acierta
poco y cubre 10 películas para todos los usuarios.

## Documentación

| Documento | Contenido |
|---|---|
| `docs/DATASET_CARD.md` | Procedencia, licencia, hash, diccionario, auditoría, sesgos y usos prohibidos |
| `docs/SYSTEM_CARD.md` | Usuarios, señales, modelos, fallback, métricas, riesgos y monitoreo |
| `docs/CIERRE_INTERPRETATIVO_LAB08.md` | Cierre interpretativo del LAB08 |
| `docs/CIERRE_INTERPRETATIVO_LAB09.md` | Cierre interpretativo del LAB09 |
| `REQUISITOS_LAB08.md`, `REQUISITOS_LAB09.md` | Requisitos y evidencia según el manual del profesor |
| `CAMBIOS_AL_BASE.md` | Cambios aplicados sobre el proyecto base y su justificación |
| `docs/EJERCICIO_05_PDF_BRIEF.pdf` | PDF breve de entrega (4 páginas) con la tabla principal y las figuras |
| `AI_USE_DECLARATION.md` | Uso honesto del asistente de IA y verificaciones pendientes del estudiante |

## Interpretación

No presente una recomendación como verdad. El recomendador por contenido mide coincidencia de
géneros y el colaborativo mide patrones de interacción: ninguno de los dos dice "le gustará". El
fallback de popularidad **no es personalizado** y debe declararse siempre. La cobertura del catálogo
se reporta junto al HitRate@10 para hacer visible la burbuja de filtro.

## Publicación

```bash
uv export --format requirements.txt --no-hashes --no-emit-project --output-file requirements.txt
uv export --format requirements.txt --no-hashes --no-emit-project --group dev --output-file requirements-dev.txt
git status
```

El dataset se obtiene por script o caché controlada, nunca desde una ruta personal. No se suben
`.venv`, credenciales ni archivos temporales; la plataforma debe permitir descargar ~1 MB de
GroupLens.
