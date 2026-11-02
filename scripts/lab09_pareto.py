"""Tres semillas y tabla de Pareto para el recomendador híbrido (LAB09).

Compara alfa, factores y semillas; registra utilidad (HitRate@10), cobertura,
costo (tiempo de ajuste y tamaño del modelo) y la frontera de Pareto.

Salidas: reports/pareto_results.csv, reports/pareto.png
"""

from __future__ import annotations

import pickle
import sys
from time import perf_counter

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from inf8239_u03.config import MOVIELENS_DIR, ROOT
from inf8239_u03.data import load_movielens
from inf8239_u03.hybrid import build_genre_features, evaluate_hybrid
from inf8239_u03.recommenders import MatrixFactorization, temporal_leave_one_out

SEEDS = [42, 7, 2024]
FACTORS = [10, 20, 40]
ALPHAS = [0.25, 0.75]
EPOCHS = 12
REPETITIONS = 3  # el tiempo de ajuste se mide varias veces y se reporta la mediana

ratings, movies = load_movielens(MOVIELENS_DIR)
train, test = temporal_leave_one_out(ratings)
genre_matrix, movie_row = build_genre_features(movies)

reports = ROOT / "reports"
reports.mkdir(exist_ok=True)
cache = reports / "pareto_results.csv"

rows = []
if "--reutilizar" in sys.argv and cache.exists():
    results = pd.read_csv(cache)
    print("Reutilizando", cache)
else:
    for seed in SEEDS:
        for factors in FACTORS:
            durations = []
            model = None
            for _ in range(REPETITIONS):
                start = perf_counter()
                model = MatrixFactorization(factors=factors, seed=seed).fit(train, epochs=EPOCHS)
                durations.append(perf_counter() - start)
            train_seconds = float(np.median(durations))
            model_size_kb = len(pickle.dumps(model)) / 1024
            for alpha in ALPHAS:
                evaluation = evaluate_hybrid(model, train, test, genre_matrix, movie_row, alpha)
                rows.append({
                    "seed": seed, "factors": factors, "epochs": EPOCHS, "alpha": alpha,
                    "rmse": evaluation["rmse"], "hit_rate_at_10": evaluation["hit_rate_at_10"],
                    "catalog_coverage": evaluation["catalog_coverage"],
                    "train_seconds": train_seconds, "train_seconds_min": min(durations),
                    "train_seconds_max": max(durations), "repeticiones": REPETITIONS,
                    "model_size_kb": model_size_kb,
                })
                print(f"seed={seed} factors={factors} alpha={alpha} "
                      f"hit@10={evaluation['hit_rate_at_10']:.5f} "
                      f"cobertura={evaluation['catalog_coverage']:.4f} "
                      f"tiempo mediana={train_seconds:.2f}s (min {min(durations):.2f} · max {max(durations):.2f})")
    results = pd.DataFrame(rows)


def pareto_flags(frame: pd.DataFrame, utility: str = "hit_rate_at_10", cost: str = "train_seconds") -> pd.Series:
    """Una configuración está dominada si otra iguala o mejora utilidad con igual o menor costo."""
    flags = []
    for _, row in frame.iterrows():
        dominated = ((frame[utility] >= row[utility]) & (frame[cost] <= row[cost]) &
                     ((frame[utility] > row[utility]) | (frame[cost] < row[cost]))).any()
        flags.append(not bool(dominated))
    return pd.Series(flags, index=frame.index)


results["is_pareto"] = pareto_flags(results)
reports = ROOT / "reports"
reports.mkdir(exist_ok=True)
results.to_csv(reports / "pareto_results.csv", index=False)

figure, axes = plt.subplots(1, 2, figsize=(13.5, 5.5))
colors = {0.25: "#0f7c7b", 0.75: "#b45309"}
markers = {42: "o", 7: "s", 2024: "^"}
sizes = {10: 55, 20: 95, 40: 135}
for alpha, group in results.groupby("alpha"):
    for seed, seed_group in group.groupby("seed"):
        axes[0].scatter(seed_group["train_seconds"], seed_group["hit_rate_at_10"], label=f"alpha={alpha}",
                        color=colors[alpha], marker=markers[seed], s=90, alpha=0.85, edgecolor="white", linewidth=0.6)
        axes[1].scatter(seed_group["train_seconds"], seed_group["catalog_coverage"], label=f"alpha={alpha}",
                        color=colors[alpha], marker=markers[seed], s=90, alpha=0.85, edgecolor="white", linewidth=0.6)
frontier = results[results["is_pareto"]].sort_values("train_seconds")
axes[0].plot(frontier["train_seconds"], frontier["hit_rate_at_10"], "--", color="#334155", linewidth=1.2,
             label="frontera de Pareto (utilidad)")
axes[1].scatter(frontier["train_seconds"], frontier["catalog_coverage"], marker="*", s=240,
                color="#111827", zorder=5, label="configuración en la frontera")
for _, row in frontier.iterrows():
    axes[0].annotate(f"s{row['seed']}·f{row['factors']}·a{row['alpha']}",
                     (row["train_seconds"], row["hit_rate_at_10"]),
                     textcoords="offset points", xytext=(8, -14), fontsize=8, color="#111827")
    axes[1].annotate(f"s{row['seed']}·f{row['factors']}·a{row['alpha']}",
                     (row["train_seconds"], row["catalog_coverage"]),
                     textcoords="offset points", xytext=(8, -14), fontsize=8, color="#111827")
axes[0].set(xlabel="Tiempo de ajuste (s)", ylabel="HitRate@10", title="Utilidad frente a costo computacional")
axes[1].set(xlabel="Tiempo de ajuste (s)", ylabel="Cobertura del catálogo", title="Cobertura frente a costo computacional")
alpha_handles = [Patch(facecolor=colors[alpha], label=f"alpha={alpha}") for alpha in ALPHAS]
seed_handles = [Line2D([], [], color="#475569", marker=markers[seed], linestyle="", markersize=8,
                        label=f"semilla {seed}") for seed in sorted(markers)]
factor_handles = [Line2D([], [], color="#475569", marker="o", linestyle="", markersize=6,
                          label=f"{factors} factores") for factors in sorted(sizes)]
figure.legend(handles=alpha_handles + seed_handles + factor_handles, loc="lower center", ncol=7, fontsize=8,
              bbox_to_anchor=(0.5, -0.07), frameon=False)
for axis in axes:
    axis.grid(alpha=0.25)
figure.tight_layout()
figure.savefig(reports / "pareto.png", dpi=160, bbox_inches="tight")

print("\nResultados completos:")
print(results.to_string(index=False))
print("\nFrontera de Pareto:")
print(results[results["is_pareto"]].to_string(index=False))
