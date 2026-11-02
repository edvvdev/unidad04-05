import json

from inf8239_u03.config import MOVIELENS_DIR, ROOT
from inf8239_u03.data import load_movielens

ratings, movies = load_movielens(MOVIELENS_DIR)
possible = ratings["userId"].nunique() * movies["movieId"].nunique()
print("Ratings:", ratings.shape, "Movies:", movies.shape)
print("Usuarios:", ratings["userId"].nunique(), "Ítems valorados:", ratings["movieId"].nunique())
print("Rango temporal:", ratings["timestamp"].min(), ratings["timestamp"].max())
print("Densidad:", len(ratings) / possible)
print(ratings["rating"].describe())

summary = {
    "ratings_rows": int(ratings.shape[0]),
    "ratings_columns": list(ratings.columns),
    "movies_rows": int(movies.shape[0]),
    "movies_columns": list(movies.columns),
    "usuarios": int(ratings["userId"].nunique()),
    "items_valorados": int(ratings["movieId"].nunique()),
    "items_catalogo": int(movies["movieId"].nunique()),
    "densidad": float(len(ratings) / possible),
    "timestamp_min": int(ratings["timestamp"].min()),
    "timestamp_max": int(ratings["timestamp"].max()),
    "rating_mean": float(ratings["rating"].mean()),
    "rating_std": float(ratings["rating"].std()),
    "rating_min": float(ratings["rating"].min()),
    "rating_max": float(ratings["rating"].max()),
    "rating_counts": {str(key): int(value) for key, value in ratings["rating"].value_counts().sort_index().items()},
    "valoraciones_por_usuario_media": float(ratings.groupby("userId").size().mean()),
    "valoraciones_por_usuario_mediana": float(ratings.groupby("userId").size().median()),
}
reports = ROOT / "reports"
reports.mkdir(exist_ok=True)
(reports / "audit_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
print("Guardado:", reports / "audit_summary.json")
