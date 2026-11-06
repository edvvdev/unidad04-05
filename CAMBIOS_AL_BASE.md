# Cambios sobre el proyecto base del profesor (LAB08 y LAB09)

El manual de la Unidad 03 pide evidencia que el proyecto base no generaba, y una auditoría posterior
contra la rúbrica encontró inconsistencias en la entrega publicada. Estos cambios son mínimos, están
documentados aquí y en el diff, y **no tocan `pyproject.toml` ni `uv.lock`**. El proyecto base original
se conserva en `~/Downloads/INF8239_U03_Recomendadores_Proyecto_Base_uv.zip` (md5 idéntico a la copia
re-descargada el 2026-11-01).

## 1. `scripts/lab09_hybrid.py` — corrección de compatibilidad (LAB09)

**Síntoma:** el script base falla antes de producir resultados.

```
TypeError: np.matrix is not supported. Please convert to a numpy array with np.asarray.
```

**Causa:** `genre_matrix` es una matriz dispersa de SciPy; `.sum(axis=0)` sobre una matriz dispersa
devuelve un `numpy.matrix` (2-D), y `cosine_similarity` de scikit-learn ya no acepta `numpy.matrix`
con NumPy 2.

**Cambio (una línea):**

```python
-    profile = genre_matrix[history_rows].multiply(weights[:, None]).sum(axis=0) / weights.sum()
+    profile = np.asarray(genre_matrix[history_rows].multiply(weights[:, None]).sum(axis=0)) / weights.sum()
```

No altera la lógica del modelo: solo convierte el resultado a `ndarray`. Es el mismo cambio que ya
tenía la copia anterior de trabajo en `001/`.

## 2. `src/inf8239_u03/hybrid.py` (módulo nuevo) — lógica reutilizable

El cálculo del híbrido estaba embebido en el script base y no se podía reutilizar para los
experimentos que exige el manual (tres perfiles, tres semillas, tabla de Pareto). Se extrajo **sin
cambiar una sola fórmula** a un módulo nuevo; `scripts/lab09_hybrid.py` ahora lo importa.

Verificación de equivalencia: el script refactorizado reproduce exactamente las métricas del script
original con los mismos argumentos (semilla 42, 20 factores, 12 épocas, α=0,75):

| Métrica | Script original | Script refactorizado |
|---|---|---|
| RMSE | 1.0264183126391635 | 1.0264183126391635 |
| HitRate@10 | 0.03747870528109029 | 0.03747870528109029 |
| Cobertura | 0.07751778167199258 | 0.07751778167199258 |

## 3. `scripts/audit_data.py` — auditoría en archivo y con cifras verificables

El manual exige adjuntar la auditoría como evidencia, no solo como captura. El script **sigue
imprimiendo lo mismo** y además guarda `reports/audit_summary.json` con filas, usuarios, ítems,
densidad, rango temporal (en segundos Unix **y** en fechas), nulos, duplicados, ítems sin
valoración, distribución de valoraciones, histórico por año y el tamaño del modelo.

Campos añadidos en la revisión de la entrega:

| Campo | Qué mide |
|---|---|
| `nulos_ratings`, `nulos_movies`, `nulos_total` | Nulos por archivo (resultado: 0) |
| `duplicados_titulo`, `duplicados_titulo_distintos` | Títulos repetidos en `movies.csv` (resultado: 5) |
| `duplicados_usuario_pelicula`, `duplicados_filas_ratings` | Filas o pares repetidos (resultado: 0 y 0) |
| `items_sin_valoracion` | Ítems del catálogo sin ninguna valoración (resultado: 18) |
| `rating_counts`, `rating_mode`, `rating_mode_share`, `rating_distribution_unimodal` | Distribución de valoraciones y su forma (unimodal, moda 4,0 con 26,6 %) |
| `fecha_min`, `fecha_max` | Rango temporal legible: 1996-03-29 – 2018-09-24 |
| `valoraciones_por_anio`, `usuarios_con_valoracion_antes_2000` | Histórico y cola antigua del corpus |
| `generado_en` | Fecha real de la corrida, que usa el PDF como «Fecha de ejecución» |

## 4. `scripts/lab08_content.py` — tres consultas por contenido

El manual pide documentar **tres consultas** con películas de géneros distintos. Se añadieron los
argumentos `--title` y `--out` (con los valores por defecto del base, `Toy Story (1995)` y
`content_recommendations.csv`), de modo que el comportamiento original se conserva y cada consulta
puede guardarse en su propio CSV.

## 5. `scripts/lab09_hybrid.py` — semilla, modelo, tamaño y archivo de salida

Se añadieron `--seed` (por defecto 42, el mismo valor de la configuración), `--save-model` (guarda el
modelo en `models/`), el campo `model_size_kb` en el JSON de métricas y el argumento `--out`, que
permite nombrar el archivo de salida dentro de `reports/`. Con `--out` el flujo documentado produce
`reports/hybrid_metrics.json` (corrida principal α=0,75), `reports/hybrid_metrics_alpha075.json`
(α=0,75) y `reports/hybrid_metrics_alpha025.json` (α=0,25) sin ambigüedad: antes, el README
atribuía la fila α=0,75 a un archivo que contenía la corrida α=0,25.

## 6. `scripts/lab09_profiles.py` y `scripts/lab09_pareto.py` (nuevos)

El manual exige dos experimentos que el base no tenía:

| Script | Evidencia que produce |
|---|---|
| `lab09_profiles.py` | Tres perfiles (historial amplio, historial pequeño, usuario nuevo con fallback) → `reports/profile_recommendations.csv` y `reports/profile_summary.csv` |
| `lab09_pareto.py` | 18 configuraciones (3 semillas × 3 tamaños de modelo × 2 valores de α) → `reports/pareto_multiseed.csv` y `reports/pareto.png` con la frontera de Pareto |

`lab09_pareto.py` acepta `--reutilizar` para regenerar la figura desde `reports/pareto_multiseed.csv`
sin volver a entrenar, y mide el tiempo de ajuste **tres veces por configuración, reportando la
mediana** (con una sola medición la frontera de Pareto cambiaba entre ejecuciones por el ruido de
tiempo).

## 7. Separación de las dos tablas de Pareto (revisión de la entrega)

Antes, `scripts/lab09_pareto.py` escribía `reports/pareto_results.csv` con un esquema propio y el
notebook escribía **el mismo nombre** con otro esquema (8 filas, una semilla): ejecutar el comando
documentado en el README pisaba la tabla consolidada que citan el README y el PDF, y la frontera de
18 configuraciones solo quedaba trazable en un PNG.

| Tabla | Archivo | Filas | Quién la escribe |
|---|---|---|---|
| Consolidada (una semilla) | `reports/pareto_results.csv` | 8 | el notebook (6 configuraciones + 2 referencias) |
| Multistamillas (frontera) | `reports/pareto_multiseed.csv` | 18 | `scripts/lab09_pareto.py` (3 semillas × 3 tamaños × 2 α, con `is_pareto`) |

El notebook ahora **lee** `reports/pareto_multiseed.csv` (y lo genera con `scripts/lab09_pareto.py` si
no existe) sin sobrescribirlo, y copia su resumen —rango de HitRate@10 y frontera— a
`reports/ejercicio05_resumen.json` para que el PDF lo presente como tabla.

## 8. `scripts/run_all.sh` y `scripts/run_all.ps1` — flujo completo (revisión de la entrega)

El runner solo ejecutaba `download_data.py` → `audit_data.py` → notebook → PDF, de modo que
`hybrid_metrics*.json`, `profile_summary.csv`, `cold_start_fallback.csv` y el Pareto multistamillas no
se regeneraban con el flujo documentado y el PDF se construía con artefactos que el runner no
producía. Ahora el flujo es:

1. entorno con `uv` (más Jupyter y `reportlab`, que no vienen en el grupo dev del base);
2. `scripts/download_data.py` y `scripts/audit_data.py`;
3. LAB08: `scripts/lab08_content.py` con las tres consultas;
4. LAB09: `scripts/lab09_hybrid.py` con α=0,75 y α=0,25;
5. LAB09: `scripts/lab09_profiles.py`;
6. LAB09: `scripts/lab09_pareto.py` (las 18 configuraciones multistamillas);
7. notebook ejecutado de principio a fin;
8. `scripts/build_ejercicio05_pdf.py`;
9. `uv run pytest -q`;
10. `scripts/resumen_ejecutable.py`: resumen final con las cifras clave leídas de `reports/`.

## 9. `scripts/build_ejercicio05_pdf.py` — PDF sin literales fijos (revisión de la entrega)

| Defecto | Corrección |
|---|---|
| Fecha de ejecución fija (`2026-11-02`) | Se lee `generado_en` de `reports/audit_summary.json` (fecha real de la corrida) y, si no existe, se calcula al construir |
| «0 nulos, 18 duplicados de texto, clases balanceadas» | Se calcula desde `reports/audit_summary.json`: nulos, títulos duplicados, pares usuario–película repetidos, ítems sin valoración y forma de la distribución de valoraciones |
| Rango temporal «2017-01-01 – 2018-09-24» | Se toma de `fecha_min`/`fecha_max`: 1996-03-29 – 2018-09-24 |
| La fila α=0,75 tomada de `hybrid_metrics.json` | Se lee de `reports/hybrid_metrics_alpha075.json` (y la de α=0,25 de `reports/hybrid_metrics_alpha025.json`) |
| «18 configuraciones en `reports/pareto_results.csv`» | El PDF presenta las dos tablas: la consolidada (`reports/pareto_results.csv`, 8 filas) y la frontera multistamillas (`reports/pareto_multiseed.csv`, 18 filas) |
| Cifras de popularidad y contenido escritas a mano | Se leen de la tabla consolidada |
| Tablas markdown del cierre renderizadas como texto plano | Se convierten en tablas de ReportLab |

## 10. Documentación y declaración de IA (revisión de la entrega)

- `README.md`, `docs/DATASET_CARD.md`, `docs/SYSTEM_CARD.md` y los dos cierres interpretativos se
  actualizaron con las cifras de la corrida vigente, distinguiendo las dos tablas de Pareto y
  corrigiendo el rango temporal, la referencia del JSON de α=0,75 y el conteo de pruebas del
  subconjunto (4 passed, no 7).
- `AI_USE_DECLARATION.md` se reescribió para describir **solo este ejercicio**: se eliminaron las
  referencias a `reports/text_metrics.csv`, al Naive Bayes, a la centralidad de embeddings y a
  `scripts/train_ae_vae.py`, que no pertenecen a este repositorio, y se añadieron las verificaciones
  con comando y salida real y las correcciones de esta revisión.

## 11. `.gitignore` — la evidencia debe quedar versionada

El `.gitignore` del base ignoraba `reports/*` completo, de modo que las métricas, tablas y figuras
exigidas por el manual (auditoría, matriz de resultados, tabla de Pareto, figuras) **no**
podían commitearse. Ahora se ignoran solo los archivos generados que no son evidencia:

```
reports/*
!reports/.gitkeep
!reports/*.json
!reports/*.csv
!reports/*.png
```

Se mantienen fuera del repositorio `data/raw/*` (se regenera con `scripts/download_data.py`) y
`models/*` (binarios grandes; si el profesor los pide, `git add -f models/*.keras`).

## 12. Correcciones de estilo (ruff)

`uv run ruff check .` señalaba hallazgos en archivos del proyecto base (comillas redundantes en las
anotaciones de tipo de `src/inf8239_u03/recommenders.py` y un `import pandas` sin usar en
`tests/test_data.py`) y, en la entrega publicada, cuatro más: un `import numpy` sin usar, un formato
con `%` y un bloque de imports mal ordenado en el notebook, más el bloque de imports del builder del
PDF. Se corrigieron todos con `ruff check --fix` y edición directa: no cambian el comportamiento y
el verificador queda en verde (`All checks passed!`).

## 13. Un solo esquema por artefacto (scripts y notebook)

Con el runner ejecutando los scripts del LAB08/LAB09 **y** el notebook, cada CSV de `reports/` podía
quedar escrito con dos esquemas distintos según cuál de los dos writers hubiera corrido al final:
`reports/popular_top10.csv` (con o sin la columna `movieId`) y
`reports/profile_recommendations.csv` (con o sin las columnas de puntuación por señal). Se
igualaron: `scripts/lab08_content.py` escribe el mismo CSV que el notebook y la celda de perfiles
del notebook escribe las mismas columnas que `scripts/lab09_profiles.py`. Verificado ejecutando los
scripts después del notebook: los artefactos no cambian.

## 14. Figuras

`reports/pareto.png` usaba el mismo marcador para «10 / 20 / 40 factores» en la leyenda, lo que la
hacía ilegible. Ahora el color identifica α, el marcador identifica la semilla y el tamaño (y el
marcador de la leyenda) identifican el número de factores.

## Comandos ejecutados para verificar (en esta máquina)

```bash
cd ~/source/uasd/cienciadedatos/tareas/Unidad_3/INF8239_U03_Recomendadores
uv sync && uv run pytest -q                       # 7 passed
uv run ruff check .                              # All checks passed!
uv run python scripts/download_data.py            # SHA-256 696d65a3dfceac7c45750ad32df2c259311949efec81f0f144fdfb91ebc9e436
uv run python scripts/audit_data.py               # + reports/audit_summary.json
uv run python scripts/lab08_content.py --title "Toy Story (1995)"      --out content_recommendations_toy_story.csv
uv run python scripts/lab08_content.py --title "Matrix, The (1999)"   --out content_recommendations_matrix.csv
uv run python scripts/lab08_content.py --title "Godfather, The (1972)" --out content_recommendations_godfather.csv
uv run python scripts/lab09_hybrid.py --factors 20 --epochs 12 --alpha 0.75 --out hybrid_metrics.json
cp reports/hybrid_metrics.json reports/hybrid_metrics_alpha075.json
uv run python scripts/lab09_hybrid.py --factors 20 --epochs 12 --alpha 0.25 --out hybrid_metrics_alpha025.json
uv run python scripts/lab09_profiles.py
uv run python scripts/lab09_pareto.py             # reports/pareto_multiseed.csv (18 filas)
uv run python -m jupyter nbconvert --to notebook --execute --inplace \
  --ExecutePreprocessor.timeout=3600 notebooks/01_ejercicio05_recomendadores.ipynb
uv run python scripts/build_ejercicio05_pdf.py
bash scripts/run_all.sh                          # flujo completo + resumen final
```

## Resultados obtenidos (para redactar las conclusiones)

LAB08 (MovieLens Latest Small, 100.836 valoraciones, 610 usuarios,
9.742 películas, densidad 1,70 %, rango 1996-03-29 – 2018-09-24):

| Métrica | Valor |
|---|---|
| Ratings / movies / usuarios | 100.836 / 9.742 / 610 |
| Rango temporal | 828.124.615 – 1.537.799.250 (1996-03-29 – 2018-09-24) |
| Media de rating | 3,5016 (mín 0,5 · máx 5,0) |
| Calidad | 0 nulos · 5 títulos duplicados · 18 ítems sin valoración |
| Distribución | unimodal (moda 4,0 con 26,6 %) |
| Top-10 popularidad (1º) | *The Shawshank Redemption* (1994), `weighted_score` 4,3952 |
| Similares a *Toy Story* (1995) | 10 películas con `content_score` 1,0 (empate por géneros idénticos) |

El empate de puntuaciones es real y debe explicarse en el cierre interpretativo: el modelo de
contenido usa TF-IDF de géneros, por lo que películas con el mismo conjunto de géneros (dibujos
animados, terror, drama…) empatan.

LAB09 (corte temporal leave-one-out, 20 factores, 12 épocas):

| α | RMSE | HitRate@10 | Cobertura | Tiempo | Tamaño |
|---|---|---|---|---|---|
| 0,75 | 1,0264 | 0,03748 | 7,75 % | 7,43 s | 1.883 KB |
| 0,25 | 1,0264 | 0,03237 | 10,65 % | 7,74 s | 1.883 KB |

Lectura: el RMSE no cambia porque depende solo de la factorización; al subir α (más peso
colaborativo) sube el acierto en el Top-10 y baja la cobertura del catálogo; con α bajo ocurre lo
contrario. Con tres semillas y tres tamaños de modelo (18 configuraciones) el HitRate@10 va
de 0,02044 a 0,05111: la varianza entre semillas supera la diferencia entre
valores de α. La frontera de Pareto de esta corrida la ocupan:

| Semilla | Factores | α | HitRate@10 | Cobertura | Tiempo (mediana) | Modelo |
|---|---|---|---|---|---|---|
| 42 | 10 | 0,75 | 0,03066 | 5,77 % | 7,39 s | 1.077 KB |
| 2024 | 10 | 0,75 | 0,05111 | 5,79 % | 7,41 s | 1.077 KB |
