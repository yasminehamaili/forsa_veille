"""Outils (function calling) que le LLM peut appeler."""
import json
from pathlib import Path

from config import CATEGORIES
from store import search

DATA = Path(__file__).parent / "data"
CATS = list(CATEGORIES.keys())

TOOLS = [
    {
        "name": "search_market_news",
        "description": ("Cherche dans la base de veille (actualités algériennes du secteur) des informations "
                        "sur le marché, les prix, les concurrents, la réglementation, l'approvisionnement, etc. "
                        "À utiliser pour expliquer les causes EXTERNES d'un phénomène."),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Requête en français (ex: 'prix du sucre importation')"},
                "category": {"type": "string", "enum": CATS, "description": "Axe de veille (optionnel)"},
                "days": {"type": "integer", "description": "Fenêtre en jours (défaut 90)"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_kpi",
        "description": "Retourne les KPIs actuels de l'entreprise pour un département.",
        "input_schema": {
            "type": "object",
            "properties": {"departement": {"type": "string",
                           "enum": ["ventes", "production", "stock", "approvisionnements", "finance"]}},
            "required": ["departement"],
        },
    },
    {
        "name": "get_forecast",
        "description": "Retourne les prévisions du modèle prédictif pour un département.",
        "input_schema": {
            "type": "object",
            "properties": {"departement": {"type": "string",
                           "enum": ["ventes", "stock", "approvisionnements"]}},
            "required": ["departement"],
        },
    },
    {
        "name": "get_competitor_info",
        "description": "Cherche les informations récentes sur un concurrent (prix, lancements, campagnes).",
        "input_schema": {
            "type": "object",
            "properties": {"nom": {"type": "string", "description": "Nom du concurrent (ex: Ifri, Hamoud)"}},
            "required": ["nom"],
        },
    },
]


def _load(name: str) -> dict:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def run_tool(name: str, args: dict):
    if name == "search_market_news":
        return search(args["query"], args.get("category"), args.get("days", 90))
    if name == "get_kpi":
        return _load("kpis.json").get(args["departement"], "département inconnu")
    if name == "get_forecast":
        return _load("forecasts.json").get(args["departement"], "pas de prévision disponible")
    if name == "get_competitor_info":
        return search(f"{args['nom']} prix lancement campagne", days=120, k=5)
    return {"erreur": f"outil inconnu: {name}"}
