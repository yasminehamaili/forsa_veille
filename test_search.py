"""Test rapide SANS clé API : vérifie que la recherche RAG fonctionne."""
from classifier import classify
from store import add_articles, search

demo = [{"id": "demo1", "title": "Hausse du prix du sucre importé", "url": "https://exemple.dz/1",
         "ts": 1790000000, "source": "Démo",
         "text": "Le prix du sucre importé a augmenté de 12% ce mois, pénalisant les producteurs de boissons "
                 "et de jus. Les fournisseurs signalent une pénurie à venir et des retards au port d'Alger."}]
for a in demo:
    a["categories"] = classify(a)
print("Catégories:", demo[0]["categories"])
print("Chunks:", add_articles(demo))
import time
demo[0]["ts"] = int(time.time())
add_articles(demo)
for h in search("pénurie de sucre prix", days=365):
    print(h["pertinence"], h["titre"], h["categorie"])
