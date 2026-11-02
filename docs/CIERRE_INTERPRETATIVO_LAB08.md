# LAB08 · Cierre interpretativo

Proyecto: `INF8239_U03_Recomendadores` · Evidencia: `reports/` · Fecha: 2026-11-01

## Resultado principal

El corpus está **localizado, descargado, auditado y documentado**: MovieLens *Latest Small* (100.836
valoraciones, 610 usuarios, 9.742 películas, densidad 1,6968 %, periodo 2017-01-01 a 2018-09-24), con
SHA-256 `696d65a3…e436` registrado y reproducido por `scripts/download_data.py`. Sobre ese corpus
funcionan las dos políticas del laboratorio: el **baseline de popularidad suavizada** y el
**recomendador por contenido**.

## Evidencia utilizada

| Evidencia | Archivo | Qué muestra |
|---|---|---|
| Descarga con hash | salida de `scripts/download_data.py` | SHA-256 de los bytes obtenidos |
| Auditoría completa | `reports/audit_summary.json` | filas, usuarios, ítems, densidad, rango temporal, distribución de valoraciones |
| Baseline de popularidad | `reports/popular_top10.csv` | *The Shawshank Redemption* (4,3952), *The Godfather* (4,2427), *Fight Club* (4,2327) |
| Tres consultas por contenido | `reports/content_recommendations_toy_story.csv`, `..._matrix.csv`, `..._godfather.csv` | listas Top-10 con `content_score` y géneros |
| Pruebas | `uv run pytest tests/test_data.py tests/test_content.py -q` | 7 passed |
| Documentación | `docs/DATASET_CARD.md` | procedencia, licencia, diccionario, sesgos y usos prohibidos |

## Qué representa la similitud

La similitud del recomendador por contenido mide **coincidencia de conjuntos de géneros** (TF-IDF
sobre la columna `genres` y coseno), no afinidad de gusto. En las tres consultas el resultado es
ilustrativo: *Toy Story (1995)* devuelve diez películas con exactamente los mismos géneros
(`Adventure|Animation|Children|Comedy|Fantasy`), *Matrix, The (1999)* diez películas con
`Action|Sci-Fi|Thriller` y *Godfather, The (1972)* diez películas con `Crime|Drama`. El `content_score`
es 1,0 en los treinta casos: el modelo está reproducido el género, no la película. La película
consultada **no aparece** en su propio Top-10 (verificado en las tres consultas), tal como exige el
manual.

## Problema de cold start observado

En este laboratorio el cold start se observa por contraste: el modelo por contenido **sí** puede
responder para un usuario sin historial, porque solo necesita la película de referencia; el modelo
colaborativo, en cambio, no tiene nada que aprender de un usuario que nunca interactuó. La
consecuencia visible en LAB09 es que el usuario nuevo recibe la lista de popularidad, idéntica para
todos, y eso debe declararse en la interfaz y en las conclusiones.

## Riesgo de sobre-especialización

El riesgo está confirmado y es **estructural**, no accidental: al usar únicamente géneros, el
recomendador devuelve variations de la misma combinación temática. El efecto practical es una burbuja
de filtro: el usuario recibe más de lo mismo, con poca exploración de categorías distintas. Agravantes
medibles: la densidad del corpus es 1,7 % (la evidencia de genres es escasa) y el catálogo incluye
9.742 películas de las cuales solo 9.724 tienen alguna valoración.

## Decisión o siguiente experimento

**Decisión:** aceptar MovieLens *Latest Small* como corpus de LAB08/LAB09 por reproducibilidad
(descarga automatizada, hash, licencia clara, identificadores anónimos, sin datos personales),
documentando tres salvedades: es un conjunto de desarrollo que puede cambiar, no tiene demografía y
no admite afirmaciones por grupo poblacional.

**Siguiente experimento:** (1) ampliar la señal de contenido con el género como *texto* ponderado por
rareza (TF-IDF con `sublinear_tf`) para romper los empates de 1,0; (2) medir diversidad con
`novelty` y `diversificación intra-lista` además de cobertura, porque la cobertura de catálogo no
detecta la repetición temática; (3) en LAB09, contrastar el peso colaborativo con la señal de
géneros antes de fijar `alpha` en la configuración final.
