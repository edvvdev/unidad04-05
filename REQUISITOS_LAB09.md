# LAB09 · Requisitos y evidencia (Unidad 03 · Manual de laboratorios guiados)

Fuente: `~/Downloads/Unidad 03. Manual laboratorios guiados_.pdf` (sección `U03.LAB09`, págs. 9–11).
Proyecto base: **INF8239_U03_Recomendadores_Proyecto_Base_uv.zip** — **se continúa aquí después del LAB08**, sin crear un segundo entorno ni descargar otra copia de MovieLens.

## Producto del laboratorio
Modelo colaborativo por factorización, corte temporal, evaluación de ratings y ranking, combinación híbrida, análisis de cold start y comparación de desempeño frente a costo.

## Pasos y requisitos
1. **Verificar el estado del proyecto**: `uv sync`, `uv run pytest -q`, `uv run python scripts/audit_data.py`.
2. **Corte temporal** (obligatorio): el script reserva la última valoración de cada usuario elegible. La separación aleatoria dejaría que el modelo aprenda de interacciones posteriores.
   `uv run python scripts/lab09_hybrid.py --factors 20 --epochs 12 --alpha 0.75`
   Resultado esperado: RMSE, HitRate@10, cobertura, duración y tamaño aproximado; recomendaciones de ejemplo y archivo de métricas.
3. **Interpretar la factorización** (lectura prudente): RMSE disminuye (mejor aproximación, revisar ranking) · HitRate sube y cobertura baja (concentra recomendaciones) · más factores sin mejora (complejidad sin evidencia) · usuario fuera del entrenamiento (no hay señal colaborativa; hace falta fallback).
4. **Híbrido**: `alpha` controla el peso colaborativo; usuarios fríos usan fallback documentado de popularidad/contenido.
   Comparación controlada: `--alpha 0.25` y `--alpha 0.75` manteniendo **iguales** semilla, corte, factores y épocas; comparar HitRate@10, cobertura y títulos recomendados; explicar qué señal domina; elegir `alpha` con evidencia, no con preferencia personal.
5. **Evaluar tres perfiles**: usuario con historial amplio (excluye ítems vistos, usa señal colaborativa) · usuario con historial pequeño (estabilidad y dependencia del contenido) · usuario nuevo (el fallback debe producir lista y declarar que **no** es personalizada).
6. **Costo y utilidad (Green AI)**: ejecutar **tres semillas**, registrar tiempo, métricas y tamaño del modelo, y construir tabla de Pareto (una configuración está dominada si otra obtiene igual o mejor utilidad con igual o menor costo). No seleccionar automáticamente el modelo más grande; justificar la mejora marginal frente a factores, épocas, tiempo y tamaño.
7. **Riesgos a revisar**: popularidad dominante · burbuja de filtro · sesgo de selección · ausencia de demografía (no se pueden afirmar resultados por grupos) · retroalimentación (las recomendaciones futuras cambian las interacciones que luego entrenan el modelo).
8. **Pruebas y Git**: `uv run pytest tests/test_matrix_factorization.py tests/test_metrics.py -q`; commit `feat: evaluate collaborative and hybrid recommenders`.

## Cierre interpretativo (redacción obligatoria)
Resultado de ratings · Resultado de ranking · Cobertura del catálogo · Comportamiento del usuario frío · Configuración seleccionada y evidencia · Costo computacional · Riesgo principal y mitigación.

## Evidencia para entregar (Ejercicio 05)
Comparación de popularidad, contenido, colaborativo e híbrido · métricas adecuadas · tres perfiles · tres semillas · pruebas · tabla de Pareto · System Card · conclusión.
