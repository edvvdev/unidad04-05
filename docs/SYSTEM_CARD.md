# System Card · Recomendador híbrido (LAB08 y LAB09)

Proyecto: `INF8239_U03_Recomendadores` · Unidad 03 · Fecha de la evaluación: 2026-11-05

## Usuarios y propósito

Sistema de recomendación académica para MovieLens *Latest Small*, construido para **estudiar** cómo se
comportan la popularidad, el contenido, la factorización y su combinación híbrida. El propósito es
pedagógico: mostrar qué mide cada métrica y qué límites tiene cada señal. **No** es un producto
orientado a producción ni a decidir qué película ve una persona real.

El sistema **no** predice la reacción de un usuario: ordena candidatos a partir de datos observados,
una función de puntuación y una política explícita.

## Catálogo y candidatos

| Aspecto | Detalle |
|---|---|
| Catálogo | 9.742 películas de `movies.csv` |
| Candidatos por usuario | Items del catálogo que el usuario **no** ha valorado en entrenamiento (`model.top_n`) |
| Filtro de vistos | Se excluye explícitamente el historial del usuario |
| Ítems nunca valorados | 18 películas del catálogo (9.742 − 9.724) no aparecen en las métricas |

## Señales utilizadas

| Señal | Implementación | Qué significa |
|---|---|---|
| Popularidad suavizada | `weighted_popularity`: media de la película combinada con la media global, ponderada por el número de valoraciones | «Lo que ve mucha gente con nota alta» |
| Contenido | TF-IDF de los géneros + similitud coseno (`ContentRecommender`) | «Comparte los géneros registrados» |
| Colaborativa | Factorización de matriz con 20 factores, 12 épocas, SGD (`MatrixFactorization`) | «Se parece a lo que valoraron usuarios parecidos» |
| Híbrida | `alpha` pondera la señal colaborativa y `1 - alpha` la de contenido (`src/inf8239_u03/hybrid.py`) | Combinación explícita de ambas señales |

## Modelos y fallback

| Componente | Configuración evaluada |
|---|---|
| Baseline (LAB08) | Popularidad suavizada, `quantile=0.80` |
| Contenido (LAB08) | TF-IDF de géneros + coseno, k=10 |
| Colaborativo (LAB09) | `MatrixFactorization(factors=20, epochs=12, seed=42)` |
| Híbrido (LAB09) | `alpha=0.75` (principal) y `alpha=0.25` (comparación controlada) |
| **Fallback (usuario frío)** | Popularidad por cantidad y media. **No es personalizada** y así se declara en `reports/hybrid_metrics.json` (`cold_start_policy`) y en la interfaz |

## Métricas offline

| Métrica | Definición | Limitación |
|---|---|---|
| RMSE | Error de predicción de ratings | Mide aproximación, **no** utilidad de la lista |
| HitRate@10 | Proporción de usuarios cuyo ítem retenido aparece en el Top-10 | Depende del corte temporal y del Top-10 |
| Cobertura del catálogo | Proporción de ítems distintos recomendados | Indica concentración, no diversidad percibida |
| Frontera de Pareto | 18 configuraciones (3 semillas × 3 tamaños × 2 α) en `reports/pareto_multiseed.csv` | El tiempo de ajuste es la mediana de 3 repeticiones: el ruido de medición es comparable a las diferencias entre configuraciones |

Resultados de referencia (semilla 42, 20 factores, 12 épocas; `reports/hybrid_metrics_alpha075.json` y
`reports/hybrid_metrics_alpha025.json`):

| α | RMSE | HitRate@10 | Cobertura | Tiempo de ajuste | Tamaño del modelo |
|---|---|---|---|---|---|
| 0,75 | 1,0264 | 0,03748 | 7,75 % | 7,75 s | 1.883 KB |
| 0,25 | 1,0264 | 0,03237 | 10,65 % | 7,57 s | 1.883 KB |

El RMSE **no cambia** con `alpha` porque depende solo de la factorización: es la evidencia de que
predecir ratings y ordenar ítems son tareas distintas.

## Cold start, cobertura y diversidad

- **Usuario nuevo (id 999999):** sin señal colaborativa → fallback de popularidad. La lista existe,
  pero no es personalizada (`reports/profile_recommendations.csv`).
- **Usuario con historial amplio (id 414, 2.697 valoraciones):** la señal colaborativa domina; las
  recomendaciones reflejan películas muy valoradas por usuarios parecidos.
- **Usuario con historial pequeño (id 53, 19 valoraciones):** la señal de contenido pesa más y las
  recomendaciones se concentran en géneros amplios; la lista es más estable pero menos específica.
- **Sobre-especialización:** el recomendador por contenido devuelve películas con **el mismo conjunto de
  géneros** (score 1,0 en las tres consultas), por lo que repite categorías ya conocidas y ofrece
  poca variedad. Es una limitación estructural del modelo por contenido, no un error de ejecución.

## Riesgos y monitoreo

| Riesgo | Descripción | Mitigación aplicada |
|---|---|---|
| Popularidad dominante | Los mismos títulos encabezan las listas de casi todos los usuarios | Comparar contenido y híbrido, y declarar el fallback como no personalizado |
| Burbuja de filtro | Exposición reiterada a un subconjunto estrecho de opciones | Medir cobertura del catálogo y reportarla junto al HitRate |
| Sesgo de selección | Solo se observan valoraciones de ítems ya consumidos | Declararlo en el Dataset Card; no permite inferir causalidad |
| Ausencia de demografía | No se pueden afirmar resultados por grupos poblacionales | No se reportan resultados por grupo |
| Retroalimentación | Las recomendaciones futuras cambian las interacciones que luego entrenan el modelo | Todo se evalúa offline sobre corte temporal |
| Similitud ≠ preferencia | El contenido solo mide coincidencia de géneros | La interfaz y este documento lo declaran de forma explícita |
| Datos mutables | *Latest Small* es un conjunto de desarrollo que puede cambiar | Se registra fecha, URL y SHA-256 |
