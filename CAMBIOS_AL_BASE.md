# Cambios sobre el proyecto base del profesor (LAB08 y LAB09)

El manual de la Unidad 03 pide evidencia que el proyecto base no generaba. Estos cambios son
mínimos, están documentados aquí y en el diff, y **no tocan `pyproject.toml` ni `uv.lock`**. El
proyecto base original se conserva en `~/Downloads/INF8239_U03_Recomendadores_Proyecto_Base_uv.zip`
(md5 idéntico a la copia re-descargada el 2026-11-01).

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
| RMSE | 1,0264183126391635 | 1,0264183126391635 |
| HitRate@10 | 0,03747870528109029 | 0,03747870528109029 |
| Cobertura | 0,07751778167199258 | 0,07751778167199258 |

## 3. `scripts/audit_data.py` — auditoría en archivo

El manual exige adjuntar la auditoría como evidencia, no solo como captura. Ahora el script **sigue
imprimiendo lo mismo** y además guarda `reports/audit_summary.json` con filas, usuarios, ítems,
densidad, rango temporal, distribución de valoraciones y número de valoraciones por usuario.

## 4. `scripts/lab08_content.py` — tres consultas por contenido

El manual pide documentar **tres consultas** con películas de géneros distintos. Se añadieron los
argumentos `--title` y `--out` (con los valores por defecto del base, `Toy Story (1995)` y
`content_recommendations.csv`), de modo que el comportamiento original se conserva y cada consulta
puede guardarse en su propio CSV.

## 5. `scripts/lab09_hybrid.py` — semilla, modelo y tamaño

Se añadieron `--seed` (por defecto 42, el mismo valor de la configuración), `--save-model` (guarda el
modelo en `models/`) y el campo `model_size_kb` en `reports/hybrid_metrics.json`, porque el manual
pide registrar «tiempo, métricas y tamaño del modelo».

## 6. `scripts/lab09_profiles.py` y `scripts/lab09_pareto.py` (nuevos)

El manual exige dos experimentos que el base no tenía:

| Script | Evidencia que produce |
|---|---|
| `lab09_profiles.py` | Tres perfiles (historial amplio, historial pequeño, usuario nuevo con fallback) → `reports/profile_recommendations.csv` y `reports/profile_summary.csv` |
| `lab09_pareto.py` | 18 configuraciones (3 semillas × 3 tamaños de modelo × 2 valores de α) → `reports/pareto_results.csv` y `reports/pareto.png` con la frontera de Pareto |

`lab09_pareto.py` acepta `--reutilizar` para regenerar la figura desde `reports/pareto_results.csv`
sin volver a entrenar, y mide el tiempo de ajuste **tres veces por configuración, reportando la
mediana** (con una sola medición la frontera de Pareto cambiaba entre ejecuciones por el ruido de
tiempo).

## 7. `.gitignore` — la evidencia debe quedar versionada

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

## 8. Correcciones de estilo (ruff)

`uv run ruff check .` señalaba tres avisos en archivos del proyecto base: comillas redundantes en las
anotaciones de tipo de `src/inf8239_u03/recommenders.py` (`-> "ContentRecommender"`) y un `import
pandas` sin usar en `tests/test_data.py`. Se corrigieron con `ruff check --fix`: no cambian el
comportamiento y el archivo usa `from __future__ import annotations`. Es el mismo cambio que ya
tenía la copia de trabajo en `001/`.

## Comandos ejecutados para verificar (en esta máquina)

```bash
cd ~/source/uasd/cienciadedatos/tareas/Unidad_3/INF8239_U03_Recomendadores
uv sync && uv run pytest -q                       # 7 passed
uv run python scripts/download_data.py            # SHA-256 696d65a3dfceac7c45750ad32df2c259311949efec81f0f144fdfb91ebc9e436
uv run python scripts/audit_data.py               # + reports/audit_summary.json
uv run python scripts/lab08_content.py --title "Toy Story (1995)"      --out content_recommendations_toy_story.csv
uv run python scripts/lab08_content.py --title "Matrix, The (1999)"   --out content_recommendations_matrix.csv
uv run python scripts/lab08_content.py --title "Godfather, The (1972)" --out content_recommendations_godfather.csv
uv run python scripts/lab09_hybrid.py --factors 20 --epochs 12 --alpha 0.75
uv run python scripts/lab09_hybrid.py --factors 20 --epochs 12 --alpha 0.25
uv run python scripts/lab09_profiles.py
uv run python scripts/lab09_pareto.py
```

## Resultados obtenidos (para redactar las conclusiones)

LAB08 (MovieLens Latest Small, 100.836 valoraciones, 610 usuarios, 9.742 películas, densidad 1,70 %):

| Métrica | Valor |
|---|---|
| Ratings / movies / usuarios | 100.836 / 9.742 / 610 |
| Rango temporal | 828124615 – 1537799250 |
| Media de rating | 3,5016 (mín 0,5 · máx 5,0) |
| Top-10 popularidad (1º) | *The Shawshank Redemption* (1994), `weighted_score` 4,3952 |
| Similares a *Toy Story* (1995) | 10 películas con `content_score` 1,0 (empate por géneros idénticos) |

El empate de puntuaciones es real y debe explicarse en el cierre interpretativo: el modelo de
contenido usa TF-IDF de géneros, por lo que películas con el mismo conjunto de géneros (dibujos
animados, terror, drama…) empatan.

LAB09 (corte temporal leave-one-out, 20 factores, 12 épocas):

| α | RMSE | HitRate@10 | Cobertura | Tiempo | Tamaño |
|---|---|---|---|---|---|
| 0,75 | 1,0264 | 0,03748 | 7,75 % | 7,54 s | 1.883 KB |
| 0,25 | 1,0264 | 0,03237 | 10,65 % | 7,43 s | 1.883 KB |

Lectura: el RMSE no cambia porque depende solo de la factorización; al subir α (más peso
colaborativo) sube el acierto en el Top-10 y baja la cobertura del catálogo; con α bajo ocurre lo
contrario. Con tres semillas y tres tamaños de modelo (18 configuraciones) el HitRate@10 va de
0,02044 a 0,05111: la varianza entre semillas supera la diferencia entre valores de α. La frontera
de Pareto la ocupan **10 factores con α=0,75** (semillas 7 y 2024): menor tiempo, menor modelo y
mayor utilidad observada.
