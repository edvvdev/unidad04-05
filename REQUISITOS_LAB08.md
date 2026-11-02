# LAB08 · Requisitos y evidencia (Unidad 03 · Manual de laboratorios guiados)

Fuente: `~/Downloads/Unidad 03. Manual laboratorios guiados_.pdf` (sección `U03.LAB08`, págs. 5–8).
Proyecto base oficial: **INF8239_U03_Recomendadores_Proyecto_Base_uv.zip** (proyecto compartido con LAB09).

## Producto del laboratorio
Dataset MovieLens documentado; baseline de popularidad suavizada; recomendador por contenido; pruebas; aplicación local y explicación de cold start, cobertura y sobre-especialización.

## Pasos y requisitos
1. **Entorno**: `uv --version`, `uv python install 3.12`, `uv sync`, `uv run pytest -q` (las pruebas usan datos pequeños incluidos solo para verificar la arquitectura).
2. **Arquitectura**: `data/raw/` (MovieLens, no se edita), `docs/` (Dataset Card y System Card), `models/`, `reports/`, `src/inf8239_u03/`, `scripts/`, `tests/`, `app/`.
3. **Fuente y licencia** a documentar: GroupLens Research, University of Minnesota · valoración de 0.5–5 estrellas con marca temporal · identificadores anónimos sin demografía · limitación: los usuariosaskarían al menos 20 películas · uso académico bajo las condiciones del README oficial · referencia Harper y Konstan (2015), DOI 10.1145/2827872 (el dataset es de desarrollo y puede cambiar: registrar fecha, URL y hash).
4. **Descargar y auditar**: `uv run python scripts/download_data.py` y `uv run python scripts/audit_data.py`. Debe imprimirse el hash SHA-256, usuarios, películas y valoraciones; comprobar columnas, claves foráneas, rango de ratings y marcas temporales.
5. **Baseline de popularidad**: `uv run python scripts/lab08_content.py`. El promedio suavizado combina media de la película y media global (una película con una sola valoración alta no debe dominar). Comparar `mean`, `count` y `weighted_score`.
6. **Contenido**: el proyecto representa géneros con TF-IDF y similitud coseno. En `reports/content_recommendations.csv`: comprobar que la película consultada no aparece en su propio Top-10 · identificar qué géneros explican las primeras posiciones · explicar los empates de puntuación · describir un caso de sobre-especialización.
   Interpretación: la recomendación significa «comparte características registradas», no «le gustará al usuario».
7. **Aplicación local**: `uv run streamlit run app/streamlit_app.py`. Probar tres películas de géneros distintos; la interfaz debe mostrar fuente, método y limitación, no solo títulos.
8. **Publicación**: `uv export --format requirements.txt --output-file requirements-cloud.txt`; dataset por script o caché controlada (nunca ruta personal); sin `.venv`, credenciales ni temporales; rutas relativas; la plataforma debe permitir descargar ~1 MB de GroupLens; README con comando de inicio y restricciones del dataset.
9. **Pruebas y Git**: `uv run pytest tests/test_data.py tests/test_content.py -q`; commits `chore: initialize reproducible recommender project` y `feat: add popularity and content recommenders`.

## Cierre interpretativo (redacción obligatoria)
Resultado principal · Evidencia utilizada · Qué representa la similitud · Problema de cold start observado · Riesgo de sobre-especialización · Decisión o siguiente experimento.

## Evidencia para entregar
Dataset Card, hash, auditoría, Top-10 de popularidad, tres consultas por contenido, pruebas, README y conclusión. El **Ejercicio 05** contiene la rúbrica oficial.
