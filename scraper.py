"""Couche 1 : collecte des actualités (RSS en priorité, HTML en secours)."""
import hashlib
import time
from datetime import datetime, timezone
from urllib.parse import urljoin

import feedparser
import requests
from bs4 import BeautifulSoup

from config import SOURCES

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ForsaTicBot/1.0; projet etudiant)"}


def _id(url: str) -> str:
    return hashlib.sha1(url.encode()).hexdigest()


def _clean(text: str) -> str:
    return " ".join(text.split())


def extract_text(url: str) -> str:
    """Télécharge une page et récupère le texte des paragraphes."""
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()
    paras = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
    return _clean(" ".join(p for p in paras if len(p) > 40))


def fetch_rss(source: dict) -> list[dict]:
    feed = feedparser.parse(source["url"], request_headers=HEADERS)
    articles = []
    for e in feed.entries[:40]:
        url = e.get("link")
        if not url:
            continue
        ts = time.mktime(e.published_parsed) if e.get("published_parsed") else time.time()
        text = BeautifulSoup(e.get("summary", ""), "html.parser").get_text(" ", strip=True)
        if len(text) < 300:  # résumé trop court -> on va chercher l'article complet
            try:
                text = extract_text(url) or text
            except Exception:
                pass
        articles.append({"id": _id(url), "title": _clean(e.get("title", "")), "url": url,
                         "ts": int(ts), "source": source["name"], "text": text})
    return articles


def fetch_html(source: dict) -> list[dict]:
    r = requests.get(source["url"], headers=HEADERS, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    links, seen = [], set()
    for a in soup.select(source["link_selector"])[:30]:
        href = urljoin(source["url"], a.get("href", ""))
        if href not in seen:
            seen.add(href)
            links.append((href, _clean(a.get_text())))
    articles = []
    for href, title in links:
        try:
            text = extract_text(href)
        except Exception:
            continue
        articles.append({"id": _id(href), "title": title, "url": href,
                         "ts": int(datetime.now(timezone.utc).timestamp()),
                         "source": source["name"], "text": text})
        time.sleep(1)  # politesse envers les serveurs
    return articles


def collect_all() -> list[dict]:
    out = []
    for s in SOURCES:
        try:
            batch = fetch_rss(s) if s["type"] == "rss" else fetch_html(s)
            print(f"[scraper] {s['name']}: {len(batch)} articles")
            out.extend(batch)
        except Exception as ex:
            print(f"[scraper] ERREUR {s['name']}: {ex}")
    return out
