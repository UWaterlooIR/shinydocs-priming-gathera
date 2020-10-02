import os

from fastapi import FastAPI
from pyserini.search import SimpleSearcher


INDEX_PATH = os.environ['ANSERINI_INDEXI_PATH']

# Initialize pyserini searcher
searcher = SimpleSearcher(INDEX_PATH)

# Configure BM25 parameters and use RM3 query expansion
searcher.set_bm25(0.9, 0.4)
searcher.set_rm3(10, 10, 0.5)

app = FastAPI()


@app.get("/")
def read_root():
    return {"index_path": INDEX_PATH}


@app.get("/search/{query}")
def read_item(query: str = None):
    hits = searcher.search(query, k=100)
    return {
        "query": query,
        "hits": [
            {
                "rank": i + 1,
                "docid": hits[i].docid,
                "score": hits[i].score,
                "title": searcher.doc(hits[i].docid).contents()[:15],
                "snippet": searcher.doc(hits[i].docid).contents()[:50]
            }
            for i in range(len(hits))
        ]
    }
