"""Couche 2 : base vectorielle (RAG) avec ChromaDB + embeddings multilingues."""
import time

import chromadb
from sentence_transformers import SentenceTransformer

from config import CHROMA_DIR, EMBED_MODEL

_model = None
_client = chromadb.PersistentClient(path=CHROMA_DIR)
_col = _client.get_or_create_collection("veille_marche", embedding_function=None,
                                        metadata={"hnsw:space": "cosine"})


def _embedder():
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBED_MODEL)
    return _model


def chunk_text(text: str, size: int = 350, overlap: int = 50) -> list[str]:
    words = text.split()
    if not words:
        return []
    step = size - overlap
    return [" ".join(words[i:i + size]) for i in range(0, len(words), step)]


def add_articles(articles: list[dict]) -> int:
    ids, docs, metas = [], [], []
    for a in articles:
        for i, ch in enumerate(chunk_text(a["text"])):
            ids.append(f"{a['id']}_{i}")
            docs.append(ch)
            metas.append({"title": a["title"], "url": a["url"], "source": a["source"], "ts": a["ts"],
                          "category": a["categories"][0], "categories": ",".join(a["categories"])})
    if not docs:
        return 0
    emb = _embedder().encode([f"passage: {d}" for d in docs], normalize_embeddings=True).tolist()
    _col.upsert(ids=ids, documents=docs, metadatas=metas, embeddings=emb)
    return len(docs)


def search(query: str, category: str | None = None, days: int = 90, k: int = 5) -> list[dict]:
    q = _embedder().encode([f"query: {query}"], normalize_embeddings=True).tolist()
    filters = [{"ts": {"$gte": int(time.time()) - days * 86400}}]
    if category:
        filters.append({"category": category})
    where = filters[0] if len(filters) == 1 else {"$and": filters}
    res = _col.query(query_embeddings=q, n_results=k, where=where)
    hits = []
    for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
        hits.append({"extrait": doc[:700], "titre": meta["title"], "source": meta["source"],
                     "url": meta["url"], "categorie": meta["category"],
                     "date": time.strftime("%Y-%m-%d", time.localtime(meta["ts"])),
                     "pertinence": round(1 - dist, 3)})
    return hits
