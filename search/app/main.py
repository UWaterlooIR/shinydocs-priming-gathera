import os
from fastapi import FastAPI, HTTPException
from pyserini.search import SimpleSearcher
from timeit import default_timer as timer

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


@app.get("/search/")
def search(query: str, size: int = 10):
    start = timer()
    hits = searcher.search(query, k=size)
    end = timer()
    total_time = end - start
    return {
        "query": query,
        "total_matches": len(hits),
        "total_time": total_time,
        "hits":
            [{
                "rank": i + 1,
                "docno": hits[i].docid,
                "score": hits[i].score,
                "title": searcher.doc(hits[i].docid).contents()[:15],
                "snippet": searcher.doc(hits[i].docid).contents()[:50]
            } for i in range(len(hits))]
    }

@app.get("/docs/{docno}/content")
def get_content(docno: str):
    doc = searcher.doc(docno)
    if doc is None:
        raise HTTPException(status_code=404, detail="Doc not found")
    return {
        "docno": docno,
        "content": doc.contents()
    }

@app.get("/docs/{docno}/raw")
def get_content(docno: str):
    doc = searcher.doc(docno)
    if doc is None:
        raise HTTPException(status_code=404, detail="Doc not found")
    return {
        "docno": docno,
        "raw": doc.raw()
    }
