"""Evalúa tres perfiles de usuario: historial amplio, historial pequeño y usuario nuevo (LAB09).

Salida: reports/profile_recommendations.csv
"""

from __future__ import annotations

from inf8239_u03.config import MOVIELENS_DIR, ROOT
from inf8239_u03.data import load_movielens
from inf8239_u03.hybrid import build_genre_features, hybrid_top_n
from inf8239_u03.recommenders import MatrixFactorization, temporal_leave_one_out

ratings, movies = load_movielens(MOVIELENS_DIR)
train, test = temporal_leave_one_out(ratings)
model = MatrixFactorization(factors=20, seed=42).fit(train, epochs=12)
genre_matrix, movie_row = build_genre_features(movies)
title_by_id = movies.set_index("movieId")["title"]

history_size = train.groupby("userId").size()
wide_user = int(history_size.idxmax())
small_user = int(history_size.idxmin())
new_user = 999_999

popular = train.groupby("movieId")["rating"].agg(["mean", "count"]).sort_values(["count", "mean"], ascending=False)
popular_items = popular.index.tolist()[:10]

rows = []
for profile, user_id in [("historial amplio", wide_user), ("historial pequeño", small_user), ("usuario nuevo", new_user)]:
    if user_id in model.user_index:
        top = hybrid_top_n(model, train, genre_matrix, movie_row, user_id, alpha=0.75, k=10)
        method = "híbrido (colaborativo + contenido)"
        for rank, item in enumerate(top.itertuples(), start=1):
            rows.append({"perfil": profile, "userId": user_id, "rank": rank, "movieId": int(item.movieId),
                         "title": title_by_id[int(item.movieId)], "metodo": method,
                         "collaborative_score": float(item.collaborative_score),
                         "content_score": float(item.content_score),
                         "hybrid_score": float(item.hybrid_score)})
    else:
        method = "fallback de popularidad (no personalizado)"
        for rank, movie_id in enumerate(popular_items, start=1):
            rows.append({"perfil": profile, "userId": user_id, "rank": rank, "movieId": int(movie_id),
                         "title": title_by_id[int(movie_id)], "metodo": method,
                         "collaborative_score": None, "content_score": None, "hybrid_score": None})

summary = []
for profile, user_id in [("historial amplio", wide_user), ("historial pequeño", small_user), ("usuario nuevo", new_user)]:
    summary.append({"perfil": profile, "userId": user_id,
                    "valoraciones_en_entrenamiento": int(history_size.get(user_id, 0)),
                    "en_entrenamiento": user_id in model.user_index,
                    "metodo": "híbrido (colaborativo + contenido)" if user_id in model.user_index
                              else "fallback de popularidad (no personalizado)"})

reports = ROOT / "reports"
reports.mkdir(exist_ok=True)
import pandas as pd

pd.DataFrame(rows).to_csv(reports / "profile_recommendations.csv", index=False)
pd.DataFrame(summary).to_csv(reports / "profile_summary.csv", index=False)
print(pd.DataFrame(summary).to_string(index=False))
print("\nRecomendaciones por perfil:")
print(pd.DataFrame(rows)[["perfil", "rank", "title", "metodo"]].to_string(index=False, max_colwidth=45))
