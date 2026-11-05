"""Resumen final del Ejercicio 05: lee `reports/` y muestra las cifras clave de la corrida.

Se invoca al final de `scripts/run_all.sh` y `scripts/run_all.ps1` para que el flujo documentado
termine con los números que efectivamente se generaron.
"""

from __future__ import annotations

import json

import pandas as pd

from inf8239_u03.config import ROOT

REPORTS = ROOT / "reports"


def leer_json(nombre: str) -> dict:
    ruta = REPORTS / nombre
    if not ruta.exists():
        return {}
    return json.loads(ruta.read_text(encoding="utf-8"))


def leer_csv(nombre: str) -> pd.DataFrame:
    ruta = REPORTS / nombre
    if not ruta.exists():
        return pd.DataFrame()
    return pd.read_csv(ruta)


def numero(valor: float, decimales: int = 5) -> str:
    return f"{valor:.{decimales}f}"


auditoria = leer_json("audit_summary.json")
alfa075 = leer_json("hybrid_metrics_alpha075.json")
alfa025 = leer_json("hybrid_metrics_alpha025.json")
consolidado = leer_csv("pareto_results.csv")
multiseed = leer_csv("pareto_multiseed.csv")
popularidad = leer_csv("popular_top10.csv")
perfiles = leer_csv("profile_summary.csv")

print("=" * 78)
print("RESUMEN DE LA CORRIDA · Ejercicio 05")
print("=" * 78)
if auditoria:
    print(f"Dataset          : {auditoria['ratings_rows']:,} valoraciones · "
          f"{auditoria['usuarios']} usuarios · {auditoria['items_catalogo']:,} películas · "
          f"densidad {auditoria['densidad']:.2%}".replace(",", "."))
    print(f"Rango temporal   : {auditoria['fecha_min']} – {auditoria['fecha_max']} "
          f"(ts {auditoria['timestamp_min']} – {auditoria['timestamp_max']})")
    print(f"Calidad          : {auditoria['nulos_total']} nulos · "
          f"{auditoria['duplicados_titulo']} títulos duplicados · "
          f"{auditoria['items_sin_valoracion']} ítems sin valoración")
    print(f"Valoraciones     : unimodal={auditoria['rating_distribution_unimodal']} · "
          f"moda {auditoria['rating_mode']} ({auditoria['rating_mode_share']:.1%})")
if not popularidad.empty:
    print(f"Popularidad (1º) : {popularidad.iloc[0]['title']} "
          f"({numero(float(popularidad.iloc[0]['weighted_score']), 4)})")
for nombre, metricas in (("híbrido α=0,75", alfa075), ("híbrido α=0,25", alfa025)):
    if metricas:
        print(f"{nombre:<17}: RMSE {numero(metricas['rmse'], 4)} · "
              f"HitRate@10 {numero(metricas['hit_rate_at_10'])} · "
              f"cobertura {metricas['catalog_coverage']:.2%} · "
              f"tiempo {metricas['train_seconds']:.2f} s · "
              f"modelo {metricas['model_size_kb']:.0f} KB")
if not consolidado.empty:
    print(f"Pareto 1 semilla : {len(consolidado)} configuraciones en reports/pareto_results.csv "
          f"(HitRate@10 {numero(consolidado['hit_rate_at_10'].min())} – "
          f"{numero(consolidado['hit_rate_at_10'].max())})")
if not multiseed.empty:
    frontera = multiseed[multiseed["is_pareto"]]
    print(f"Pareto multistam.: {len(multiseed)} configuraciones en reports/pareto_multiseed.csv "
          f"(HitRate@10 {numero(multiseed['hit_rate_at_10'].min())} – "
          f"{numero(multiseed['hit_rate_at_10'].max())}; frontera: {len(frontera)})")
    for _, fila in frontera.iterrows():
        print(f"    frontera  semilla {int(fila['seed'])} · {int(fila['factors'])} factores · "
              f"α={fila['alpha']} · HitRate@10 {numero(fila['hit_rate_at_10'])} · "
              f"cobertura {fila['catalog_coverage']:.2%}")
if not perfiles.empty:
    for _, fila in perfiles.iterrows():
        print(f"Perfil           : {fila['perfil']} (usuario {int(fila['userId'])}, "
              f"{int(fila['valoraciones_en_entrenamiento'])} valoraciones) · {fila['metodo']}")
print("=" * 78)
