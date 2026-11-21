"""Configuration centrale : sources de veille, catégories, mots-clés."""
import os

CHROMA_DIR = os.getenv("CHROMA_DIR", "./chroma_db")
EMBED_MODEL = "intfloat/multilingual-e5-small"  # FR + AR, léger (changer pour bge-m3 si GPU)
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-5-5")

# ⚠️ À VÉRIFIER / AJUSTER : les URLs et sélecteurs peuvent changer.
# type "rss"  -> flux RSS (le plus stable, à privilégier)
# type "html" -> page de liste d'articles + sélecteur CSS des liens
SOURCES = [
    {"name": "APS Économie", "type": "rss", "url": "https://www.aps.dz/economie?format=feed&type=rss"},
    {"name": "El Watan Économie", "type": "rss", "url": "https://elwatan-dz.com/category/economie/feed"},
    {"name": "Liberté Économie", "type": "rss", "url": "https://www.liberte-algerie.com/economie/feed"},
    {"name": "Le Quotidien d'Oran", "type": "html",
     "url": "https://www.lequotidien-oran.com/", "link_selector": "a[href*='news=']"},
    # Ajoute ici : sites de concurrents (boissons), ministères, Journal Officiel...
]

# Les 7 axes de la veille globale
CATEGORIES = {
    "technologique": ["machine", "automatisation", "technologie", "emballage", "procédé", "usine", "digital",
                      "تكنولوجيا", "آلة"],
    "economique": ["inflation", "dinar", "taux de change", "croissance", "importation", "exportation",
                   "douane", "pib", "économie", "تضخم", "دينار", "استيراد", "تصدير"],
    "financiere": ["crédit", "banque", "fiscal", "impôt", "subvention", "financement", "investissement",
                   "loi de finances", "قرض", "بنك", "ضريبة"],
    "commerciale": ["prix", "vente", "marché", "concurrent", "part de marché", "promotion", "consommation",
                    "سعر", "سوق", "منافس"],
    "approvisionnement": ["matière première", "sucre", "huile", "blé", "pénurie", "stock", "logistique",
                          "port", "fournisseur", "approvisionnement", "ندرة", "مواد أولية", "سكر"],
    "marketing": ["publicité", "campagne", "marque", "lancement", "tendance", "consommateur", "sponsor",
                  "إشهار", "علامة"],
    "distribution": ["distribution", "grande surface", "grossiste", "détaillant", "export", "circuit",
                     "transport", "توزيع", "جملة"],
}

# Filtre sectoriel : on ne garde que les articles liés au secteur choisi
SECTOR_KEYWORDS = [
    "boisson", "jus", "soda", "eau minérale", "limonade", "agroalimentaire", "sucre", "emballage",
    "conserve", "lait", "ifri", "hamoud", "coca", "cevital", "soummam", "rouiba", "نيو", "مشروبات", "عصير",
    "الصناعات الغذائية",
]
