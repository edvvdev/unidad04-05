# Dataset Card · MovieLens (LAB08 y LAB09)

Proyecto: `INF8239_U03_Recomendadores` · Curso: INF-8239 Ciencia de Datos II · Unidad 03

## Fuente, fecha, versión y hash

| Campo | Valor |
|---|---|
| Fuente | GroupLens Research, University of Minnesota — MovieLens *Latest Small* |
| URL de descarga | `https://files.grouplens.org/datasets/movielens/ml-latest-small.zip` |
| URL de la ficha | `https://grouplens.org/datasets/movielens/latest/` |
| Script de descarga | `scripts/download_data.py` (usa `src/inf8239_u03/data.py`) |
| Fecha de descarga | 2026-11-05 (ejecución en esta máquina) |
| SHA-256 de los bytes descargados | `696d65a3dfceac7c45750ad32df2c259311949efec81f0f144fdfb91ebc9e436` |
| Versión | *Latest Small* (conjunto de desarrollo, **puede cambiar**; no es una versión archivada) |
| Ruta local | `data/raw/ml-latest-small/` (no se versiona; se regenera con el script) |

El hash permite verificar que otra persona obtiene exactamente los mismos bytes; si cambia, cambió la
fuente y las métricas deben recalcularse.

## Licencia y cita

- Uso: académico e investigativo según el README oficial de MovieLens (no hay licencia de código
  abierto; se debe citar la fuente).
- Cita: Harper, F. M., & Konstan, J. A. (2015). *The MovieLens datasets: Movie data for recommender
  system research*. ACM Transactions on Office Information Systems, 29(4), 19. https://doi.org/10.1145/2827872
- El manual de la Unidad 03 reproduce esta referencia y su DOI.

## Archivos y diccionario

| Archivo | Filas | Columnas | Descripción |
|---|---|---|---|
| `ratings.csv` | 100.836 | `userId`, `movieId`, `rating`, `timestamp` | Valoración explícita de 0,5 a 5 estrellas con marca temporal en segundos Unix |
| `movies.csv` | 9.742 | `movieId`, `title`, `genres` | Catálogo de películas con Géneros separados por `|` (sin género = `(no genres listed)`) |

| Columna | Tipo | Significado | Unidad / categorías |
|---|---|---|---|
| `userId` | entero | Identificador anónimo del usuario | 1–610 |
| `movieId` | entero | Identificador de la película | 1–9.742 |
| `rating` | flotante | Valoración del usuario | 0,5–5,0 en pasos de 0,5 |
| `timestamp` | entero | Momento de la valoración | Segundos Unix (828.124.615–1.537.799.250) |
| `title` | texto | Título de la película | Texto libre |
| `genres` | texto | Géneros de la película | Conjunto de 0–3 géneros de una taxonomía de 20 |

Estadísticas de auditoría (`reports/audit_summary.json`, generado por `scripts/audit_data.py`):

| Indicador | Valor |
|---|---|
| Filas de valoración / usuarios | 100.836 / 610 |
| Ítems valorados / ítems del catálogo | 9.724 / 9.742 |
| Densidad de la matriz usuario–ítem | 1,6968 % |
| Rango temporal | 828.124.615 – 1.537.799.250 (1996-03-29 – 2018-09-24) |
| Media ± desviación de la valoración | 3,5016 ± 1,0425 (mín 0,5 · máx 5,0) |
| Valoraciones por usuario | media 165,3 · mediana 70,5 |
| Nulos (`ratings.csv` + `movies.csv`) | 0 (0 + 0) |
| Duplicados | 5 títulos repetidos en el catálogo · 0 pares usuario–película repetidos · 0 filas repetidas |
| Ítems sin ninguna valoración | 18 (9.742 − 9.724) |
| Distribución de valoraciones | 0,5: 1.370 · 1,0: 2.811 · 1,5: 1.791 · 2,0: 7.551 · 2,5: 5.550 · 3,0: 20.047 · 3,5: 13.136 · 4,0: 26.818 · 4,5: 8.551 · 5,0: 13.211 |
| Forma de la distribución | **unimodal**: moda 4,0 con 26.818 valoraciones (26,6 %); no es balanceada |

## Procedimiento de descarga

```bash
uv sync
uv run python scripts/download_data.py     # imprime destino y SHA-256
uv run python scripts/audit_data.py        # imprime auditoría y guarda reports/audit_summary.json
```

El script valida que no haya rutas inseguras en el ZIP antes de extraerlo. No hay rutas absolutas ni
credenciales en el código; el destino es relativo a la raíz del proyecto.

## Población observada y exclusiones

- **Población observada:** usuarios registrados en MovieLens que valoraron al menos 20 películas; sin
  demografía, sin edad, sin género, sin ubicación. Los identificadores son anónimos y no permiten
  reconstruir a una persona.
- **Período observado:** del 29 de marzo de 1996 al 24 de septiembre de 2018 (rango completo de las
  marcas temporales del corpus). El histórico no es uniforme: la cola antigua es pequeña
  (1996: 6.040 · 1997: 1.916 · 1998: 507 · 1999: 2.439 valoraciones), mientras que el grueso del corpus es de 2017–2018; el desglose por año está en
  `reports/audit_summary.json` (`valoraciones_por_anio`) y 159 de los
  610 usuarios tienen alguna valoración anterior a 2000.
- **Exclusiones aplicadas en el laboratorio:** ninguna columna del dataset se elimina; la separación
  entre entrenamiento y prueba se hace por **corte temporal** (la última valoración de cada usuario
  queda como prueba), no por muestreo aleatorio, para no usar interacciones futuras.
- **Ítems sin valoración:** 18 películas del catálogo
  (9.742 − 9.724) nunca fueron valoradas y
  quedan fuera de la evaluación, aunque siguen siendo recommendation candidates.

## Calidad, sesgos y usos prohibidos

- **Calidad:** la auditoría (`reports/audit_summary.json`) no detecta **ningún nulo** en `ratings.csv`
  ni en `movies.csv`; los rangos de valoración y las claves foráneas se validan en
  `validate_movielens`. Hay 5 títulos de película repetidos en el
  catálogo (títulos distintos con la misma etiqueta, no filas repetidas) y ningún par
  usuario–película repetido. Las marcas temporales permiten simular evaluación temporal, pero
  **no** permiten saber qué recomendación se hizo en el momento real.
- **Sesgo de autoselección:** solo se observan consumos ya realizados; la densidad baja
  (1,70 %) significa que la mayoría de las combinaciones usuario–película
  no tiene valoración, no que el usuario rechazara la película.
- **Sin demografía:** no se pueden atribuir preferencias a grupos poblacionales.
- **Uso no permitido:** no usar estos datos para afirmar preferencias de grupos, ni publicar
  identificadores personales, ni tratar *Latest Small* como archivo congelado para resultados
  científicos comparables (advertencia explícita de GroupLens).
- **Uso permitido:** investigación académica con cita de la fuente y registro de la fecha y el hash.
