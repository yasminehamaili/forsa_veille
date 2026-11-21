"""Pipeline complet : collecte -> filtre -> classification -> indexation.
Lancer chaque jour :  python ingest.py   (cron / GitHub Actions)"""
from classifier import classify, is_relevant
from scraper import collect_all
from store import add_articles


def run() -> dict:
    raw = collect_all()
    kept = [a for a in raw if a["text"] and is_relevant(a)]
    for a in kept:
        a["categories"] = classify(a)
    n_chunks = add_articles(kept)
    stats = {"collectes": len(raw), "pertinents": len(kept), "chunks_indexes": n_chunks}
    print("[ingest]", stats)
    return stats


if __name__ == "__main__":
    run()
