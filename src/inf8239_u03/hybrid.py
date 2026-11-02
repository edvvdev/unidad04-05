"""Lógica compartida del recomendador híbrido (LAB09).

Se extrajo del script `scripts/lab09_hybrid.py` del proyecto base para poder
reutilizar exactamente el mismo cálculo en los experimentos de perfiles y de
Pareto, sin duplicar ni alterar la lógica original.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import root_mean_squared_error
from sklearn.metrics.pairwise import cosine_similarity

from inf8239_u03.metrics import catalog_coverage, hit_rate_at_k
from inf8239_u03.recommenders import MatrixFactorization


def build_genre_features(movies: pd.DataFrame) -> tuple[object, dict[int, int]]:
    """Devuelve la matriz TF-IDF de géneros y el índice película -> fila."""
    movie_table = movies.reset_index(drop=True).copy()
    movie_table["genres_text"] = movie_table["genres"].str.replace("|", " ", regex=False)
    genre_matrix = TfidfVectorizer().fit_transform(movie_table["genres_text"])
    movie_row = {int(movie_id): index for index, movie_id in enumerate(movie_table["movieId"])}
    return genre_matrix, movie_row


def genre_profile(
    history: pd.DataFrame,
    genre_matrix,
    movie_row: dict[int, int],
) -> np.ndarray:
    """Perfil de géneros ponderado por la nota del usuario (base + 2.5)."""
    history_rows = [movie_row[int(item)] for item in history["movieId"]]
    weights = np.clip(history["rating"].to_numpy() - 2.5, 0.1, None)
    profile = np.asarray(genre_matrix[history_rows].multiply(weights[:, None]).sum(axis=0)) / weights.sum()
    return profile


def hybrid_top_n(
    model: MatrixFactorization,
    train: pd.DataFrame,
    genre_matrix,
    movie_row: dict[int, int],
    user_id: int,
    alpha: float,
    k: int = 10,
    candidates: int = 100,
) -> pd.DataFrame:
    """Top-k híbrido (colaborativo + contenido) para un usuario."""
    seen = set(train.loc[train["userId"].eq(user_id), "movieId"])
    collaborative = model.top_n(user_id, seen, candidates)
    span = max(collaborative["collaborative_score"].max() - collaborative["collaborative_score"].min(), 1e-9)
    collaborative["normalized"] = (collaborative["collaborative_score"] - collaborative["collaborative_score"].min()) / span
    history = train.loc[train["userId"].eq(user_id) & train["movieId"].isin(movie_row), ["movieId", "rating"]]
    profile = genre_profile(history, genre_matrix, movie_row)
    candidate_rows = [movie_row[int(item)] for item in collaborative["movieId"]]
    content_scores = cosine_similarity(profile, genre_matrix[candidate_rows]).ravel()
    content_span = max(content_scores.max() - content_scores.min(), 1e-9)
    collaborative["content_score"] = (content_scores - content_scores.min()) / content_span
    collaborative["hybrid_score"] = alpha * collaborative["normalized"] + (1 - alpha) * collaborative["content_score"]
    return collaborative.nlargest(k, "hybrid_score")


def evaluate_hybrid(
    model: MatrixFactorization,
    train: pd.DataFrame,
    test: pd.DataFrame,
    genre_matrix,
    movie_row: dict[int, int],
    alpha: float,
    k: int = 10,
) -> dict:
    """RMSE, HitRate@K, cobertura y recomendaciones del sistema híbrido."""
    evaluable = test[test["userId"].isin(model.user_index) & test["movieId"].isin(model.item_index)]
    predictions = [model.predict(row.userId, row.movieId) for row in evaluable.itertuples()]
    rmse = root_mean_squared_error(evaluable["rating"], predictions)
    recommendations: dict[int, list[int]] = {}
    for user_id in evaluable["userId"].unique():
        top = hybrid_top_n(model, train, genre_matrix, movie_row, int(user_id), alpha, k)
        recommendations[int(user_id)] = top["movieId"].astype(int).tolist()
    return {
        "rmse": float(rmse),
        "hit_rate_at_10": hit_rate_at_k(recommendations, evaluable, k),
        "catalog_coverage": catalog_coverage(recommendations, len(model.items)),
        "evaluable_users": len(recommendations),
        "recommendations": recommendations,
    }
