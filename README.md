# Forsa TIC – Chatbot expert avec veille marché (RAG + outils)

## Architecture
```
Sources (RSS/HTML) -> scraper.py -> classifier.py (secteur + 7 axes) -> store.py (ChromaDB, embeddings FR/AR)
                                                                             |
Employé -> /chat (api.py) -> agent.py (Claude + tool calling) -> tools.py: search_market_news
                                                                          get_kpi / get_forecast
                                                                          get_competitor_info
```

## Installation
```bash
python -m venv venv && source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                  # puis mets ta clé ANTHROPIC_API_KEY
```

## Utilisation
```bash
python test_search.py          # 1) tester le RAG (sans clé API)
python ingest.py               # 2) collecter + indexer les actualités (à planifier 1x/jour)
uvicorn api:app --reload       # 3) lancer l'API
```
Test :
```bash
curl -X POST http://127.0.0.1:8000/chat -H "Content-Type: application/json" \
  -d '{"message":"Pourquoi nos ventes baissent ?","departement":"ventes"}'
```

## À faire ensuite
1. Vérifier/ajuster `SOURCES` dans `config.py` (URLs RSS, sélecteurs HTML) et ajouter les sites de concurrents.
2. Remplacer `data/kpis.json` et `forecasts.json` par les vraies sorties du pipeline ML.
3. Brancher `/chat` sur le panneau chatbot du front, et afficher `sources` sous chaque réponse.
4. Planifier `ingest.py` (cron ou GitHub Actions).
5. Tester la qualité sur des textes arabes ; passer à `bge-m3` si besoin.

## Remarques légales
Respecter robots.txt et conditions des sites ; privilégier RSS ; toujours citer la source.
