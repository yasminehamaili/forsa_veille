"""Couche 3 : le LLM expert (Claude) avec boucle d'appel d'outils."""
import json
import os

import anthropic
from dotenv import load_dotenv

from config import CLAUDE_MODEL
from tools import TOOLS, run_tool

load_dotenv()
client = anthropic.Anthropic()  # lit ANTHROPIC_API_KEY

SYSTEM_PROMPT = """Tu es un analyste expert du secteur agroalimentaire / boissons en Algérie, intégré à une
plateforme de reporting d'entreprise. Tu aides les employés à comprendre leurs rapports et à décider.

MÉTHODE (obligatoire) :
1. Commence par les données internes : appelle get_kpi (et get_forecast si pertinent).
2. Cherche ensuite les causes EXTERNES avec search_market_news. Balaye les axes pertinents parmi :
   technologique, economique, financiere, commerciale, approvisionnement, marketing, distribution.
   Fais plusieurs recherches si besoin (une par axe).
3. Distingue clairement causes internes (opérations, données) et causes externes (marché).
4. Propose des stratégies concrètes, priorisées, avec l'impact attendu.

RÈGLES :
- Base chaque affirmation externe sur une source retournée par les outils ; cite [Source, date].
- Ne jamais inventer de chiffres. Si l'info manque, dis-le.
- Parle de "cause probable", jamais de cause certaine (corrélation ≠ causalité).
- Réponds dans la langue de l'utilisateur (français par défaut), ton clair et professionnel.

FORMAT DE RÉPONSE :
**Constat** · **Causes internes** · **Causes externes (veille marché)** · **Risques à venir** · **Recommandations**
(Pour une question simple, réponds brièvement sans tout le format.)"""


def ask(message: str, departement: str | None = None, history: list | None = None, max_steps: int = 8) -> dict:
    ctx = f"[Département affiché : {departement}]\n" if departement else ""
    messages = (history or []) + [{"role": "user", "content": ctx + message}]
    sources: dict[str, dict] = {}

    for _ in range(max_steps):
        resp = client.messages.create(model=CLAUDE_MODEL, max_tokens=1500, system=SYSTEM_PROMPT,
                                      tools=TOOLS, messages=messages)
        if resp.stop_reason != "tool_use":
            answer = "".join(b.text for b in resp.content if b.type == "text")
            return {"answer": answer, "sources": list(sources.values())}

        messages.append({"role": "assistant", "content": resp.content})
        results = []
        for block in resp.content:
            if block.type == "tool_use":
                out = run_tool(block.name, block.input)
                if isinstance(out, list):
                    for h in out:
                        if isinstance(h, dict) and "url" in h:
                            sources[h["url"]] = {"titre": h["titre"], "source": h["source"],
                                                 "date": h["date"], "url": h["url"]}
                results.append({"type": "tool_result", "tool_use_id": block.id,
                                "content": json.dumps(out, ensure_ascii=False)})
        messages.append({"role": "user", "content": results})

    return {"answer": "Je n'ai pas pu conclure (trop d'étapes). Reformule ta question.", "sources": []}
