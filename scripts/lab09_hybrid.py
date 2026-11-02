from __future__ import annotations

import argparse
import json
import pickle
from time import perf_counter

from inf8239_u03.config import MOVIELENS_DIR, ROOT
from inf8239_u03.data import load_movielens
from inf8239_u03.hybrid import build_genre_features, evaluate_hybrid
from inf8239_u03.recommenders import MatrixFactorization, temporal_leave_one_out

parser = argparse.ArgumentParser()
parser.add_argument("--factors", type=int, default=20)
parser.add_argument("--epochs", type=int, default=12)
parser.add_argument("--alpha", type=float, default=0.75)
parser.add_argument("--seed", type=int, default=42)
parser.add_argument("--save-model", action="store_true", help="guarda el modelo de factorización en models/")
args = parser.parse_args()

ratings, movies = load_movielens(MOVIELENS_DIR)
train, test = temporal_leave_one_out(ratings)
start = perf_counter()
model = MatrixFactorization(factors=args.factors, seed=args.seed).fit(train, epochs=args.epochs)
train_seconds = perf_counter() - start
genre_matrix, movie_row = build_genre_features(movies)
evaluation = evaluate_hybrid(model, train, test, genre_matrix, movie_row, args.alpha)
model_size_kb = len(pickle.dumps(model)) / 1024
popular = train.groupby("movieId")["rating"].agg(["mean", "count"]).sort_values(["count", "mean"], ascending=False)
popular_items = popular.index.tolist()
metrics = {
    "rmse": evaluation["rmse"],
    "hit_rate_at_10": evaluation["hit_rate_at_10"],
    "catalog_coverage": evaluation["catalog_coverage"],
    "train_seconds": train_seconds,
    "factors": args.factors,
    "epochs": args.epochs,
    "alpha": args.alpha,
    "seed": args.seed,
    "model_size_kb": model_size_kb,
    "cold_start_policy": "popularidad por cantidad y media; no personalizada",
}
(ROOT / "reports").mkdir(exist_ok=True)
(ROOT / "reports/hybrid_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
cold_start_items = popular_items[:10]
movies[movies["movieId"].isin(cold_start_items)].set_index("movieId").loc[cold_start_items].reset_index().to_csv(
    ROOT / "reports/cold_start_fallback.csv", index=False
)
if args.save_model:
    models = ROOT / "models"
    models.mkdir(exist_ok=True)
    model_path = models / f"mf_factors{args.factors}_epochs{args.epochs}_alpha{args.alpha}_seed{args.seed}.joblib"
    model_path.write_bytes(pickle.dumps(model))
    metrics["model_path"] = str(model_path.relative_to(ROOT))
    (ROOT / "reports/hybrid_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(json.dumps(metrics, indent=2))
