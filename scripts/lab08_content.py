import argparse

from inf8239_u03.config import MOVIELENS_DIR, ROOT
from inf8239_u03.data import load_movielens
from inf8239_u03.recommenders import ContentRecommender, weighted_popularity

parser = argparse.ArgumentParser()
parser.add_argument("--title", default="Toy Story (1995)", help="película de referencia para la consulta por contenido")
parser.add_argument("--out", default="content_recommendations.csv", help="archivo CSV de salida dentro de reports/")
args = parser.parse_args()

ratings, movies = load_movielens(MOVIELENS_DIR)
reports = ROOT / "reports"
reports.mkdir(exist_ok=True)
popular = weighted_popularity(ratings, movies).head(10)
popular[["title", "count", "mean", "weighted_score"]].to_csv(reports / "popular_top10.csv", index=False)
recommendations = ContentRecommender().fit(movies).recommend(args.title, 10)
recommendations.to_csv(reports / args.out, index=False)
print("Popularidad:\n", popular[["title", "count", "mean", "weighted_score"]])
print(f"\nSimilares a {args.title}:\n", recommendations)
print(f"\nGuardado: {reports / args.out}")
