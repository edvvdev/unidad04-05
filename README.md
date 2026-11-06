# INF-8239 · Ejercicio 05 · Motor recomendador reproducible

Autor académico: Edwin Ramón José Nolasco · Repositorio: https://github.com/edvvdev/unidad04-05

> **Este ejercicio es de la Unidad 03** (consolida LAB08 y LAB09): el nombre del repositorio
> `unidad04-05` heredó la numeración global de la Tarea INF-8239 y se conserva para no romper
> los enlaces ya publicados y los PDF que los citan.

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
| Notebook ejecutado | `notebooks/01_ejercicio05_recomendadores.ipynb` (21 celdas, con salidas) |
| Código reutilizable | `src/inf8239_u03/` (`data`, `recommenders`, `hybrid`, `metrics`) |
| Pruebas | `tests/` (`uv run pytest -q` → 7 passed) |
| Métricas y figuras | `reports/` |
| Requisitos | `requirements.txt` y `requirements-dev.txt` (exportados con `uv export`) |
| PDF breve de entrega | `docs/EJERCICIO_05_PDF_BRIEF.pdf` |
| Declaración de IA | `AI_USE_DECLARATION.md` |

Para ejecutar el notebook de principio a fin:

```bash
uv pip install --python .venv/bin/python jupyter nbformat ipykernel reportlab
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
uv run python scripts/lab09_hybrid.py --factors 20 --epochs 12 --alpha 0.75 --out hybrid_metrics.json
uv run python scripts/lab09_hybrid.py --factors 20 --epochs 12 --alpha 0.25 --out hybrid_metrics_alpha025.json
uv run python scripts/lab09_profiles.py            # tres perfiles de usuario
uv run python scripts/lab09_pareto.py              # tres semillas + frontera de Pareto

# Aplicación local
uv run streamlit run app/streamlit_app.py
```

`scripts/lab09_hybrid.py` acepta `--out` para nombrar el JSON de métricas (por defecto
`hybrid_metrics.json`); `scripts/lab09_pareto.py` escribe `reports/pareto_multiseed.csv` (18
configuraciones) y `reports/pareto.png`.

## Ejecución completa (un solo comando)

```bash
./scripts/run_all.sh          # macOS / Linux
```
```powershell
.\scripts\run_all.ps1        # Windows
```

El script hace, en este orden: entorno con uv → descarga del dataset y auditoría → LAB08 (las tres
consultas por contenido) → LAB09 (híbrido con α=0,75 y α=0,25, perfiles de usuario y frontera de
Pareto multistamillas) → notebook ejecutado de principio a fin → PDF de entrega → pruebas → resumen
final con las cifras clave de la corrida. Instala además Jupyter y `reportlab`, que **no** vienen en
el grupo de desarrollo del proyecto base del profesor (`uv sync` solo instala pytest, pytest-cov y
ruff). El paso de Pareto multistamillas entrena 18 configuraciones con 3 repeticiones cada una y
tarda varios minutos en CPU.

## Resultados de referencia (2026-11-05, CPU, semilla 42)

| Evidencia | Archivo | Resultado |
|---|---|---|
| Dataset y auditoría | `reports/audit_summary.json` | 100.836 valoraciones · 610 usuarios · 9.742 películas · densidad 1,70 % · rango temporal 1996-03-29 – 2018-09-24 · 0 nulos · 5 títulos duplicados · 18 ítems sin valoración |
| Baseline de popularidad | `reports/popular_top10.csv` | *Shawshank Redemption, The (1994)* (4,3952) · *Godfather, The (1972)* (4,2427) · *Fight Club (1999)* (4,2327) |
| Contenido (3 consultas) | `reports/content_recommendations_*.csv` | 10 películas con `content_score` 1,0 por coincidencia exacta de géneros |
| Híbrido α=0,75 | `reports/hybrid_metrics_alpha075.json` | RMSE 1,0264 · HitRate@10 0,03748 · cobertura 7,75 % · 7,75 s · 1.883 KB |
| Híbrido α=0,25 | `reports/hybrid_metrics_alpha025.json` | RMSE 1,0264 · HitRate@10 0,03237 · cobertura 10,65 % · 7,57 s · 1.883 KB |
| Tres perfiles | `reports/profile_recommendations.csv` | historial amplio (2.697 valoraciones), historial pequeño (19), usuario nuevo (fallback) |
| Pareto multistamillas | `reports/pareto_multiseed.csv`, `reports/pareto.png` | 18 configuraciones (3 semillas × 3 tamaños × 2 α): HitRate@10 de 0,02044 a 0,05111; frontera: 10 factores con α=0,75 (semillas 42, 2024) |
| Pareto de una semilla | `reports/pareto_results.csv` | 8 configuraciones (6 híbridas + 2 referencias) del corte temporal con semilla 42 |

`reports/hybrid_metrics.json` es la corrida principal (α=0,75, 20 factores) y
`reports/hybrid_metrics_alpha075.json` / `reports/hybrid_metrics_alpha025.json` separan cada α. Los
tiempos de ajuste son los medidos en la corrida del 2026-11-05; el valor vigente de cada corrida está
siempre en el JSON o CSV citado.

**Los tiempos de ajuste de las distintas tablas provienen de corridas distintas** (mismo código y misma
semilla, pero ejecuciones separadas), así que una misma configuración aparece con tiempos ligeramente
diferentes según el archivo. No es una contradicción: **la única fuente de verdad de cada cifra es su
archivo**. Para citar el tiempo de una configuración se usa el del JSON del híbrido —**7,75 s** para
α=0,75 (`reports/hybrid_metrics_alpha075.json`) y **7,57 s** para α=0,25
(`reports/hybrid_metrics_alpha025.json`)—; cada tabla de Pareto reproduce el tiempo de su propio CSV.

### Las dos tablas de Pareto

| Tabla | Archivo | Filas | Contenido |
|---|---|---|---|
| Consolidada (una semilla) | `reports/pareto_results.csv` | 8 | 6 configuraciones híbridas (3 tamaños × 2 α) + las 2 referencias (contenido y popularidad), todas con la semilla 42 |
| Multistamillas (frontera) | `reports/pareto_multiseed.csv` | 18 | 3 semillas × 3 tamaños × 2 α con la columna `is_pareto`: es la frontera de 18 configuraciones que se cita en el PDF |

La tabla consolidada la escribe el notebook y la tabla multistamillas la escribe
`scripts/lab09_pareto.py`: **nunca comparten nombre**, así que ejecutar una no pisa la otra.

### Tabla consolidada del Ejercicio 05 (`reports/pareto_results.csv`, 8 filas)

| Configuración | HitRate@10 | Cobertura | RMSE | Ajuste (s) | Modelo (KB) |
|---|---|---|---|---|---|
| mf40_alpha0.75 | 0,03918 | 10,06 % | 1,0211 | 7,96 | 3.494 |
| mf20_alpha0.75 | 0,03748 | 7,75 % | 1,0264 | 7,84 | 1.883 |
| mf20_alpha0.25 | 0,03237 | 10,65 % | 1,0264 | 7,84 | 1.883 |
| mf10_alpha0.75 | 0,03066 | 5,77 % | 1,0337 | 7,77 | 1.077 |
| mf10_alpha0.25 | 0,02896 | 8,38 % | 1,0337 | 7,77 | 1.077 |
| mf40_alpha0.25 | 0,02726 | 12,27 % | 1,0211 | 7,96 | 3.494 |
| popularidad | 0,02131 | 0,10 % | — | — | — |
| contenido | 0,00000 | 19,07 % | — | — | — |

Los tiempos de ajuste de esta tabla son los de `reports/pareto_results.csv` (corrida propia): ver la nota
de «Resultados de referencia» sobre las corridas distintas.

Lectura: `alpha=0,75` (más peso colaborativo) gana en acierto y **pierde** cobertura en las tres
comparaciones; el contenido tiene la mayor cobertura pero acierto nulo, y la popularidad acierta
poco y cubre 10 películas para todos los usuarios.

### Frontera multistamillas (`reports/pareto_multiseed.csv`, 18 filas)

| Semilla | Factores | α | HitRate@10 | Cobertura | Ajuste (s, mediana de 3) | Modelo (KB) |
|---|---|---|---|---|---|---|
| 42 | 10 | 0,75 | 0,03066 | 5,77 % | 7,42 s | 1.077 KB |
| 2024 | 10 | 0,75 | 0,05111 | 5,79 % | 7,50 s | 1.077 KB |

Los tiempos de esta tabla son los de `reports/pareto_multiseed.csv` (mediana de tres repeticiones,
corrida propia), no los de la tabla consolidada: la nota de «Resultados de referencia» explica por qué
conviven tiempos distintos de la misma configuración.

## Documentación

| Documento | Contenido |
|---|---|
| `docs/DATASET_CARD.md` | Procedencia, licencia, hash, diccionario, auditoría, sesgos y usos prohibidos |
| `docs/SYSTEM_CARD.md` | Usuarios, señales, modelos, fallback, métricas, riesgos y monitoreo |
| `docs/CIERRE_INTERPRETATIVO_LAB08.md` | Cierre interpretativo del LAB08 |
| `docs/CIERRE_INTERPRETATIVO_LAB09.md` | Cierre interpretativo del LAB09 |
| `REQUISITOS_LAB08.md`, `REQUISITOS_LAB09.md` | Requisitos y evidencia según el manual del profesor |
| `CAMBIOS_AL_BASE.md` | Cambios aplicados sobre el proyecto base y su justificación |
| `docs/EJERCICIO_05_PDF_BRIEF.pdf` | PDF breve de entrega (4 páginas) con las dos tablas de Pareto y las figuras |
| `AI_USE_DECLARATION.md` | Uso honesto del asistente de IA: herramienta, prompts, verificaciones con comando y salida, correcciones y límites |

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
