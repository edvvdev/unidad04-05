# Declaración de uso de inteligencia artificial · LAB08 y LAB09

Proyecto: `INF8239_U03_Recomendadores` (Unidad 03) · Curso: INF-8239 Ciencia de Datos II
Fecha: 2026-11-01

## Herramienta

Asistente de IA en modo CLI (Kilo, modelo MiniMax-M3) conversando con el estudiante, con acceso a
esta máquina y al repositorio del curso.

## En qué ayudó

- **Lectura del manual de la Unidad 03** y extracción de la lista de requisitos y evidencia de LAB08 y
  LAB09 a `REQUISITOS_LAB08.md` y `REQUISITOS_LAB09.md`.
- **Corrección de un error del proyecto base**: `scripts/lab09_hybrid.py` fallaba con
  `TypeError: np.matrix is not supported` (NumPy 2 + scikit-learn). Se aplicó una única línea
  (`np.asarray(...)`) que no altera la lógica del modelo; el cambio está documentado en
  `CAMBIOS_AL_BASE.md`.
- **Extensiones mínimas sobre el base**, todas justificadas porque el manual exige evidencia que el
  proyecto original no producía:
  - `scripts/audit_data.py` ahora guarda `reports/audit_summary.json`.
  - `scripts/lab08_content.py` acepta `--title` y `--out` para documentar tres consultas.
  - `src/inf8239_u03/hybrid.py` (módulo nuevo) extrae la lógica del híbrido del script base para poder
    reutilizarla sin duplicarla; `scripts/lab09_hybrid.py` la usa y reproduce **exactamente** las
    mismas métricas que el script original (RMSE 1,0264183126391635, HitRate@10 0,03747870528109029,
    cobertura 0,07751778167199258).
  - `scripts/lab09_hybrid.py` añade `--seed`, guardado opcional del modelo y `model_size_kb`.
  - `scripts/lab09_profiles.py` y `scripts/lab09_pareto.py` (nuevos) producen la evaluación de los tres
    perfiles y la tabla de Pareto con tres semillas, que el manual exige.
  - `scripts/train_ae_vae.py` del proyecto generativo: curvas, MSE de reconstrucción y panel de 16
    ejemplos con semilla fija (documentado en `CAMBIOS_AL_BASE.md` de ese proyecto).
- **Redacción** de `docs/DATASET_CARD.md`, `docs/SYSTEM_CARD.md`, los cierres interpretativos de LAB08 y
  LAB09, este documento y la actualización del README.
- **Revisión de las figuras** (`reports/pareto.png`): se corrigió una leyenda ilegible y se eliminaron
  textos encimados.

## Qué ejecutó y verificó el estudiante

El estudiante debe confirmar, **en su propia máquina y con su propia cuenta**, antes de entregar:

- [ ] `uv sync` y `uv run pytest -q` en verde (aquí: 7 passed).
- [ ] `uv run python scripts/download_data.py` y comprobar que el SHA-256 coincide con el de la Dataset Card.
- [ ] `uv run python scripts/audit_data.py` y contrastar las cifras con `reports/audit_summary.json`.
- [ ] `uv run python scripts/lab08_content.py --title "..." --out ...` para las tres consultas.
- [ ] `uv run python scripts/lab09_hybrid.py --factors 20 --epochs 12 --alpha 0.75` y `--alpha 0.25`.
- [ ] `uv run python scripts/lab09_profiles.py` y `uv run python scripts/lab09_pareto.py` (tres semillas).
- [ ] `uv run streamlit run app/streamlit_app.py` con tres películas de géneros distintos.
- [ ] Tomar las capturas de pantalla (con `cls` antes de cada una) y comprobar que las cifras del
      informe coinciden con los JSON/CSV de `reports/`.

## Límites y decisiones del estudiante

- El asistente **no decide** qué dataset usar en los laboratorios donde el manual exige aprobación del
  docente, ni redacta las conclusiones finales sin que el estudiante las revise.
- El asistente **no ejecutó** el código en el portátil del estudiante: todas las cifras de este
  repositorio provienen de ejecuciones en esta máquina Linux y deben reconfirmarse en el entorno del
  estudiante (Windows, VS Code, PowerShell) antes de entregarlas.
- La declaración de que una recomendación "le gustará a alguien" es **incorrecta**: el sistema mide
  coincidencia de géneros o patrones de interacción, y así queda escrito en las cards y en la interfaz.
- No se usaron datos personales: MovieLens solo contiene identificadores anónimos.


## Ejercicio 05 (consolidación) · prompts, verificaciones y correcciones

**Prompts relevantes que guiaron el trabajo**

1. «Consolida en un único producto ejecutable las evidencias de LAB08 y LAB09: descarga y auditoría
   con SHA-256, baseline de popularidad, recomendación por contenido con tres consultas, corte
   temporal leave-one-out, factorización, híbrido con dos α, tres perfiles de usuario y una frontera
   de Pareto; el notebook debe quedar ejecutado de principio a fin y con figuras legibles.»
2. «El script base fija el modelo logístico aunque el Naive Bayes gane por F1 macro: guarda y analiza
   el mejor por la métrica del manual y deja la comparación en CSV.»
3. «Extrae la lógica del híbrido a un módulo reutilizable sin cambiar una sola fórmula y verifica
   que reproduce las métricas originales.»
4. «Elige una palabra del corpus para los vecinos de los embeddings y explica qué significa cada
   medida de centralidad sin afirmar que una persona es "la más influyente".»
5. «No redistribuyas MovieLens: el dataset se descarga por script y `data/raw/` queda fuera del
   repositorio.»

**Verificaciones que el estudiante debe repetir (casillas para marcar)**

- [ ] `uv sync` y `uv run pytest -q` → 7 passed.
- [ ] `uv run python scripts/download_data.py` → el SHA-256 coincide con el de `docs/DATASET_CARD.md`.
- [ ] `uv run python scripts/audit_data.py` → cifras iguales a `reports/audit_summary.json`.
- [ ] `uv run python scripts/lab09_hybrid.py --factors 20 --epochs 12 --alpha 0.75` y `--alpha 0.25`
      → HitRate@10 0,03748 y 0,03237, cobertura 7,75 % y 10,65 %.
- [ ] `uv run python scripts/lab09_profiles.py` → el usuario nuevo recibe el fallback y la interfaz lo
      declara como no personalizado.
- [ ] `uv run python scripts/lab09_pareto.py` → 18 configuraciones; el tiempo es la mediana de 3
      repeticiones.
- [ ] Ejecutar el notebook del Ejercicio 05 de principio a fin y revisar las tres figuras.
- [ ] Regenerar `docs/EJERCICIO_05_PDF_BRIEF.pdf` y completar nombre, matrícula y enlace.

**Correcciones realizadas durante la ejecución**

| Corrección | Causa | Verificación |
|---|---|---|
| `np.asarray(...)` en el perfil de géneros de `lab09_hybrid.py` | `scipy` devuelve `numpy.matrix` en `.sum(axis=0)` y scikit-learn ya no lo acepta con NumPy 2 | El script volvió a ejecutarse y produjo las métricas del manual |
| Lógica del híbrido extraída a `src/inf8239_u03/hybrid.py` | El base la tenía embebida en el script y no se podía reutilizar | Métricas idénticas: RMSE 1,0264183126391635, HitRate@10 0,03747870528109029, cobertura 0,07751778167199258 |
| Se guarda el **mejor** modelo por F1 macro | El base guardaba siempre el logístico (0,78954) aunque el Naive Bayes ganara (0,81903) | `reports/text_metrics.csv` marca `es_elegido` |
| `reports/*` dejó de ignorarse en `.gitignore` | El base excluía las figuras y el CSV de métricas, es decir, la evidencia que exige el mandato | `git check-ignore` confirma que los JSON/CSV/PNG sí se versionan |
| `requirements.txt` y `requirements-dev.txt` generados con `uv export` | El mandato los exige y el base solo traía `requirements-colab.txt` | `uv export` regenera ambos de forma reproducible |
