"""Auditoría del corpus MovieLens.

Imprime el resumen y lo guarda en `reports/audit_summary.json` para que la documentación y el PDF
se apoyen en el artefacto y no en literales escritos a mano.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime

import pandas as pd

from inf8239_u03.config import MOVIELENS_DIR, ROOT
from inf8239_u03.data import load_movielens

ratings, movies = load_movielens(MOVIELENS_DIR)
possible = ratings["userId"].nunique() * movies["movieId"].nunique()
print("Ratings:", ratings.shape, "Movies:", movies.shape)
print("Usuarios:", ratings["userId"].nunique(), "Ítems valorados:", ratings["movieId"].nunique())
print("Rango temporal:", ratings["timestamp"].min(), ratings["timestamp"].max())
print("Densidad:", len(ratings) / possible)
print(ratings["rating"].describe())


def ahora_local() -> datetime:
    """Instante actual en la zona horaria local de la máquina."""
    return datetime.now(tz=UTC).astimezone()


def fecha_utc(timestamp: int) -> str:
    return datetime.fromtimestamp(int(timestamp), tz=UTC).strftime("%Y-%m-%d")


# --- Nulos ------------------------------------------------------------------------------------
nulos_ratings = int(ratings.isna().sum().sum())
nulos_movies = int(movies.isna().sum().sum())
nulos_por_columna = {f"ratings.{columna}": int(valor) for columna, valor in ratings.isna().sum().items()}
nulos_por_columna.update(
    {f"movies.{columna}": int(valor) for columna, valor in movies.isna().sum().items()}
)

# --- Duplicados -------------------------------------------------------------------------------
duplicados_titulo = int(movies["title"].duplicated().sum())
duplicados_titulo_distintos = int(movies.loc[movies["title"].duplicated(), "title"].nunique())
duplicados_usuario_pelicula = int(ratings.duplicated(subset=["userId", "movieId"]).sum())
duplicados_filas = int(ratings.duplicated().sum())

# --- Histórico por año (el corpus tiene una cola antigua de pocos años) -------------------------
anios = pd.to_datetime(ratings["timestamp"], unit="s", utc=True).dt.year
conteo_anios = anios.value_counts().sort_index()
usuarios_antes_2000 = int(ratings.loc[anios < 2000, "userId"].nunique())

# --- Distribución de valoraciones --------------------------------------------------------------
conteo = ratings["rating"].value_counts().sort_index()
modos = conteo[conteo == conteo.max()]
codigo_moda = float(modos.index[0])
valoraciones_moda = int(modos.max())
proporcion_moda = float(valoraciones_moda / len(ratings))

summary = {
    "generado_en": ahora_local().strftime("%Y-%m-%d"),
    "ratings_rows": int(ratings.shape[0]),
    "ratings_columns": list(ratings.columns),
    "movies_rows": int(movies.shape[0]),
    "movies_columns": list(movies.columns),
    "usuarios": int(ratings["userId"].nunique()),
    "items_valorados": int(ratings["movieId"].nunique()),
    "items_catalogo": int(movies["movieId"].nunique()),
    "items_sin_valoracion": int(movies["movieId"].nunique() - ratings["movieId"].nunique()),
    "valoraciones_por_anio": {str(int(anio)): int(valor) for anio, valor in conteo_anios.items()},
    "usuarios_con_valoracion_antes_2000": usuarios_antes_2000,
    "densidad": float(len(ratings) / possible),
    "timestamp_min": int(ratings["timestamp"].min()),
    "timestamp_max": int(ratings["timestamp"].max()),
    "fecha_min": fecha_utc(ratings["timestamp"].min()),
    "fecha_max": fecha_utc(ratings["timestamp"].max()),
    "rating_mean": float(ratings["rating"].mean()),
    "rating_std": float(ratings["rating"].std()),
    "rating_min": float(ratings["rating"].min()),
    "rating_max": float(ratings["rating"].max()),
    "rating_counts": {str(key): int(value) for key, value in conteo.items()},
    "rating_mode": codigo_moda,
    "rating_mode_count": valoraciones_moda,
    "rating_mode_share": proporcion_moda,
    "rating_distribution_unimodal": bool(len(modos) == 1),
    "nulos_ratings": nulos_ratings,
    "nulos_movies": nulos_movies,
    "nulos_total": nulos_ratings + nulos_movies,
    "nulos_por_columna": nulos_por_columna,
    "duplicados_titulo": duplicados_titulo,
    "duplicados_titulo_distintos": duplicados_titulo_distintos,
    "duplicados_usuario_pelicula": duplicados_usuario_pelicula,
    "duplicados_filas_ratings": duplicados_filas,
    "valoraciones_por_usuario_media": float(ratings.groupby("userId").size().mean()),
    "valoraciones_por_usuario_mediana": float(ratings.groupby("userId").size().median()),
}
reports = ROOT / "reports"
reports.mkdir(exist_ok=True)
(reports / "audit_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
print("Guardado:", reports / "audit_summary.json")
print(
    "Nulos:", nulos_ratings + nulos_movies,
    "| títulos duplicados:", duplicados_titulo,
    "| ítems sin valoración:", summary["items_sin_valoracion"],
    "| moda de valoración:", codigo_moda, f"({proporcion_moda:.1%})",
)
