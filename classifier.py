"""Filtre sectoriel + classification dans les 7 axes de veille (par mots-clés)."""
from config import CATEGORIES, SECTOR_KEYWORDS


def is_relevant(article: dict) -> bool:
    blob = (article["title"] + " " + article["text"]).lower()
    return any(k in blob for k in SECTOR_KEYWORDS)


def classify(article: dict) -> list[str]:
    """Retourne les catégories triées par score (une 'principale' + secondaires)."""
    blob = (article["title"] + " " + article["text"]).lower()
    scores = {cat: sum(blob.count(k) for k in kws) for cat, kws in CATEGORIES.items()}
    ranked = [c for c, s in sorted(scores.items(), key=lambda x: -x[1]) if s > 0]
    return ranked[:2] or ["economique"]
