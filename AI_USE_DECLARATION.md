# Declaración de uso de inteligencia artificial · Ejercicio 05

Proyecto: `INF8239_U03_Recomendadores` (Ejercicio 05 · consolidación de LAB08 y LAB09) · Curso:
INF-8239 Ciencia de Datos II · Unidad 04 · Fecha: 2026-11-05

Esta declaración describe **únicamente este ejercicio**. No contiene material de otros proyectos
(logística, Naive Bayes, modelos generativos) ni referencias a archivos que no existen en este
repositorio.

## Herramienta

Asistente de IA en modo CLI (Kilo, modelo MiniMax-M3) conversando con el estudiante, con acceso a
esta máquina y al repositorio del curso. No se usó ninguna otra herramienta de IA en este
ejercicio.

## Finalidad

1. **Ejecutar el flujo completo del laboratorio** y dejar la entrega reproducible: descarga con
   SHA-256, auditoría, recomendación por contenido, factorización con corte temporal, híbrido con
   dos valores de α, perfiles de usuario, frontera de Pareto, notebook ejecutado y PDF de entrega.
2. **Corregir incompatibilidades técnicas** del proyecto base (NumPy 2 y `numpy.matrix`) y extraer
   la lógica del híbrido a un módulo reutilizable sin alterar ninguna fórmula.
3. **Auditar la entrega contra la rúbrica** antes de publicarla: comprobar que cada cifra citada en
   el README, las cards, los cierres y el PDF sale de `reports/`, que el flujo documentado regenera
   todos los artefactos y que las pruebas y el linter pasan.
4. **Redactar** la documentación del ejercicio (README, Dataset Card, System Card, cierres
   interpretativos, PDF y esta declaración).

## Prompts relevantes que guiaron el trabajo

1. «Consolida en un único producto ejecutable las evidencias de LAB08 y LAB09: descarga y auditoría
   con SHA-256, baseline de popularidad, recomendación por contenido con tres consultas, corte
   temporal leave-one-out, factorización, híbrido con dos α, tres perfiles de usuario y una frontera
   de Pareto; el notebook debe quedar ejecutado de principio a fin y con figuras legibles.»
2. «Extrae la lógica del híbrido a un módulo reutilizable sin cambiar una sola fórmula y verifica
   que reproduce las métricas originales.»
3. «No redistribuyas MovieLens: el dataset se descarga por script y `data/raw/` queda fuera del
   repositorio.»
4. «Corrige los defectos de la entrega contra la rúbrica: la tabla de Pareto de 18 configuraciones
   no existe en ningún CSV versionado, el runner no ejecuta los scripts del LAB08/LAB09, el PDF tiene
   la fecha fija y cifras sin respaldo, y el lint falla.»
5. «Ninguna cifra del README, las cards, los cierres o el PDF puede estar escrita a mano: todo tiene
   que salir de `reports/`.»

## Verificaciones ejecutadas (comando y salida)

| Verificación | Comando | Salida observada |
|---|---|---|
| Pruebas | `uv run pytest -q` | `7 passed` |
| Linter | `uv run ruff check .` | `All checks passed!` |
| Descarga con hash | `uv run python scripts/download_data.py` | `SHA-256: 696d65a3dfceac7c45750ad32df2c259311949efec81f0f144fdfb91ebc9e436` |
| Auditoría | `uv run python scripts/audit_data.py` | 0 nulos · 5 títulos duplicados · 18 ítems sin valoración · moda 4,0 (26,6 %) · rango 1996-03-29 – 2018-09-24 |
| Contenido (3 consultas) | `uv run python scripts/lab08_content.py --title "Toy Story (1995)" --out content_recommendations_toy_story.csv` (y las otras dos) | 10 películas con `content_score` 1,0 en cada consulta |
| Híbrido α=0,75 | `uv run python scripts/lab09_hybrid.py --factors 20 --epochs 12 --alpha 0.75 --out hybrid_metrics.json` | RMSE 1,0264 · HitRate@10 0,03748 · cobertura 7,75 % · 1.883 KB |
| Híbrido α=0,25 | `uv run python scripts/lab09_hybrid.py --factors 20 --epochs 12 --alpha 0.25 --out hybrid_metrics_alpha025.json` | RMSE 1,0264 · HitRate@10 0,03237 · cobertura 10,65 % |
| Perfiles | `uv run python scripts/lab09_profiles.py` | historial amplio (414, 2.697 valoraciones) · historial pequeño (53, 19) · usuario nuevo (999999, fallback de popularidad) |
| Pareto multistamillas | `uv run python scripts/lab09_pareto.py` | 18 configuraciones en `reports/pareto_multiseed.csv` · HitRate@10 de 0,02044 a 0,05111 · frontera: 2 |
| Flujo completo | `bash scripts/run_all.sh` | termina sin errores y regenera los artefactos de `reports/` |
| Notebook | `uv run python -m jupyter nbconvert --to notebook --execute --inplace ...` | 21 celdas, 0 celdas en error, con salidas |
| PDF | `pdftotext -layout docs/EJERCICIO_05_PDF_BRIEF.pdf -` | 4 páginas con el nombre, la URL del repositorio y el rango temporal 1996-03-29 – 2018-09-24 |

## Correcciones realizadas durante la ejecución

| Corrección | Causa | Verificación |
|---|---|---|
| `np.asarray(...)` en el perfil de géneros de `lab09_hybrid.py` | `scipy` devuelve `numpy.matrix` en `.sum(axis=0)` y scikit-learn ya no lo acepta con NumPy 2 | El script volvió a ejecutarse y produjo las métricas del manual |
| Lógica del híbrido extraída a `src/inf8239_u03/hybrid.py` | El base la tenía embebida en el script y no se podía reutilizar | Métricas idénticas: RMSE 1,0264, HitRate@10 0,03748, cobertura 0,0775 |
| `reports/pareto_results.csv` (tabla consolidada de una semilla) y `reports/pareto_multiseed.csv` (18 configuraciones) son archivos distintos | Ambos se llamaban igual y el script pisaba la tabla que citan el README y el PDF | `bash scripts/run_all.sh` regenera los dos: 8 filas y 18 filas |
| El notebook lee `reports/pareto_multiseed.csv` y no lo sobrescribe | La frontera de 18 configuraciones solo quedaba trazable en un PNG | El notebook imprime la frontera y la copia en `reports/ejercicio05_resumen.json` |
| `scripts/run_all.sh` y `scripts/run_all.ps1` ejecutan LAB08 y LAB09 antes del notebook | El flujo documentado no regeneraba `hybrid_metrics*.json`, `profile_summary.csv`, `cold_start_fallback.csv` ni el Pareto | La corrida completa termina con `scripts/resumen_ejecutable.py` |
| Fecha de ejecución del PDF calculada en tiempo de ejecución | Estaba fija en `2026-11-02` | `scripts/audit_data.py` escribe `generado_en` en `reports/audit_summary.json` y el PDF lo usa |
| `scripts/audit_data.py` calcula nulos, duplicados, distribución de valoraciones e ítems sin valoración | El PDF afirmaba «0 nulos, 18 duplicados de texto, clases balanceadas» sin artefacto que lo respaldara | `reports/audit_summary.json` contiene las cifras y el PDF las lee de ahí |
| Rango temporal corregido a 1996-03-29 – 2018-09-24 | El mínimo real (`timestamp_min` 828.124.615) es de 1996-03-29, no de 2017-01-01 | `fecha_min` y `fecha_max` se derivan de los timestamps en el JSON de auditoría |
| Referencia de la corrida α=0,75 corregida a `reports/hybrid_metrics_alpha075.json` | `reports/hybrid_metrics.json` contenía la corrida α=0,25 y el tiempo «7,54 s» no correspondía a ningún artefacto | Los dos JSON existen con su propio campo `alpha` |
| `pytest tests/test_data.py tests/test_content.py -q` documentado como 4 passed (7 es el total) | Cifra incorrecta en el cierre de LAB08 | `uv run pytest -q` → 7 passed; el subconjunto → 4 passed |
| Marcadores distintos en la leyenda de `reports/pareto.png` | 10, 20 y 40 factores usaban el mismo marcador | La figura se regenera con `scripts/lab09_pareto.py` |
| `uv run ruff check .` en verde | Quedaban 4 hallazgos (3 en el notebook y 1 en el builder del PDF) | `All checks passed!` |

## Límites y responsabilidades del estudiante

- El asistente **no decide** qué dataset usar ni redacta las conclusiones finales sin que el
  estudiante las revise: el estudiante es responsable de los datos, del código, de las referencias y
  de las conclusiones de este ejercicio.
- El asistente **no ejecutó** el código en el portátil del estudiante: todas las cifras de este
  repositorio provienen de ejecuciones en esta máquina Linux (CPU, 2026-11-05) y deben reconfirmarse en
  su entorno (Windows, VS Code, PowerShell) antes de entregar.
- Los tiempos de ajuste dependen de la máquina y cambian entre corridas; por eso la cifra vigente de
  cada métrica está en el JSON o CSV de `reports/` y no en el texto.
- La afirmación de que una recomendación «le gustará a alguien» es **incorrecta**: el sistema mide
  coincidencia de géneros o patrones de interacción, y así queda escrito en las cards, en el PDF y en
  la interfaz.
- No se usaron datos personales: MovieLens solo contiene identificadores anónimos, y el dataset no se
  redistribuye (se descarga por script y `data/raw/` queda fuera de Git).
