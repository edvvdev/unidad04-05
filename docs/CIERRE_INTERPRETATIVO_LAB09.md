# LAB09 · Cierre interpretativo

Proyecto: `INF8239_U03_Recomendadores` · Evidencia: `reports/` · Fecha: 2026-11-01

## Resultado de ratings

La factorización de matriz (20 factores, 12 épocas, SGD, semilla 42) alcanza **RMSE 1,0264** sobre la
valoración retenida por el corte temporal (última valoración de cada usuario). Al subir a 40 factores
el RMSE mejora marginalmente (1,0211 con semilla 42; 1,0168 con semilla 2024) mientras el tamaño del
modelo se multiplica por 3,2 (1.077 MB → 3.494 MB). Mejor aproximación de ratings **no** significa
mejor recomendación: lo demuestra el hecho de que el RMSE es idéntico para `alpha` 0,25 y 0,75,
porque la combinación híbrida no participa en el ajuste.

## Resultado de ranking

Con la configuración principal (`alpha=0.75`, 20 factores, 12 épocas, semilla 42) el **HitRate@10 es
0,03748**: menos de 4 de cada 100 usuarios con valoración retenida encontraron esa película en las
primeras 10 posiciones. Al bajar a `alpha=0.25` el acierto cae a 0,03237 y la cobertura sube de 7,75 %
a 10,65 %. Con tres semillas y tres tamaños de modelo (18 configuraciones en
`reports/pareto_results.csv`) el HitRate@10 va de 0,02044 a 0,05111: **la varianza entre semillas es
mayor que la diferencia entre valores de `alpha`**, por lo que una sola ejecución no sostiene
conclusiones sobre `alpha`.

## Cobertura del catálogo

La cobertura baja con `alpha` alto (7,75 % con 0,75 frente a 10,65 % con 0,25) y sube con más
factores (12,4 %–12,6 % con 40 factores). En el mejor caso medido, solo 1 de cada 10 películas del
catálogo aparece alguna vez en las listas: el sistema concentra las recomendaciones. Es el indicador
de burbuja de filtro que exige el manual, y obliga a reportar cobertura junto al HitRate y nunca por
separado.

## Comportamiento del usuario frío

`reports/profile_recommendations.csv` documenta los tres perfiles:

| Perfil | Usuario | Valoraciones en entrenamiento | Comportamiento observado |
|---|---|---|---|
| Historial amplio | 414 | 2.697 | Lista del híbrido con señal colaborativa dominante (dramas y clásicos con muchas valoraciones) |
| Historial pequeño | 53 | 19 | Señal de contenido con más peso; lista más estable y genérica (*The Godfather*, *Annie Hall*, *Apocalypse Now*) |
| Usuario nuevo | 999999 | 0 | **Fallback de popularidad**: *Forrest Gump*, *The Shawshank Redemption*, *Pulp Fiction*…; la lista existe pero **no es personalizada** |

## Configuración seleccionada y evidencia

Se elige **`alpha=0.75` con 20 factores, 12 épocas y semilla 42**, por evidencia y no por preferencia:
(1) es la configuración del manual; (2) con las tres semillas, `alpha=0.75` domina en HitRate@10 en
6 de 9 comparaciones por semilla; (3) el RMSE no depende de `alpha`; (4) su costo es intermedio. La
**frontera de Pareto** (utilidad HitRate@10 frente a costo) la ocupan tres configuraciones:

| Semilla | Factores | α | HitRate@10 | Cobertura | Tiempo (mediana) | Modelo |
|---|---|---|---|---|---|---|
| 7 | 10 | 0,75 | 0,04089 | 5,46 % | 7,48 s | 1,077 MB |
| 2024 | 10 | 0,75 | 0,05111 | 5,79 % | 7,56 s | 1,077 MB |
| 2024 | 20 | 0,75 | 0,03578 | 7,49 % | 7,42 s | 1,883 MB |

Ninguna otra configuración las domina. La lectura honesta es que **el tamaño del modelo y la
utilidad son los ejes que discriminan**, no el tiempo: las tres configuraciones frontera tienen el
mayor HitRate@10 y el menor tamaño (10 factores) o un tamaño intermedio con más cobertura. Con
`alpha=0.25` ninguna configuración llega a la frontera: baja el acierto en el Top-10 y sube la
cobertura, es decir, cambia *qué* se recomienda, no *cuántas* películas distintas aparecen.

## Costo computacional

| Configuración | Tiempo de ajuste (mediana de 3) | Rango observado | Tamaño del modelo | RMSE |
|---|---|---|---|---|
| 10 factores | 7,48–7,56 s | 7,397–7,567 s | 1,077 MB | 1,0265–1,0337 |
| 20 factores | 7,42–7,60 s | 7,393–7,741 s | 1,883 MB | 1,0259–1,0266 |
| 40 factores | 7,51–7,55 s | 7,454–7,729 s | 3,494 MB | 1,0168–1,0244 |

El tiempo de ajuste es **prácticamente constante** (±0,1 s) porque lo domina el número de
observaciones × épocas del SGD, no el número de factores; el costo que sí crece de forma clara es el
**tamaño del modelo** (1,08 → 1,88 → 3,49 MB, ×3,2). Al repetir la medición, la frontera de Pareto
cambió entre ejecuciones (con una sola corrida por configuración entraba una de 40 factores): la
diferencia entre configuraciones es menor que el ruido de medición, por lo que **no se puede
afirmar que una configuración sea más rápida que otra**. Medición en CPU de escritorio, sin GPU.

## Riesgo principal y mitigación

**Riesgo principal: burbuja de filtro por concentración**, agravada por el desbalance de las señales
(la cobertura no supera el 13 % en ninguna configuración). **Mitigación aplicada:** documentar la
cobertura y el HitRate juntos, declarar el fallback de popularidad como no personalizado, comparar
explícitamente `alpha` alto y bajo, y reportar la frontera de Pareto en lugar de elegir el modelo más
grande. Riesgos secundarios: sesgo de selección (solo consumos ya realizados), ausencia de demografía
(no se afirman resultados por grupo) y retroalimentación (todo se evalúa offline con corte temporal,
sin usar interacciones futuras).
