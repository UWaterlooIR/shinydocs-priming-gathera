import os

from fastapi import FastAPI, HTTPException
from pyserini.search import SimpleSearcher
#from pyserini import index
from timeit import default_timer as timer


#INDEX_PATH = os.environ['ANSERINI_INDEX_PATH']
SEARCH_INDEX_PATH = os.environ['ANSERINI_SMALL_INDEX_PATH']
print(SEARCH_INDEX_PATH)
# Initialize pyserini searcher
searcher = SimpleSearcher(SEARCH_INDEX_PATH)
#index_reader = index.IndexReader(INDEX_PATH)

# Configure BM25 parameters
searcher.set_bm25(0.9, 0.4)
#searcher.set_rm3(10, 10, 0.5)
import logging

app = FastAPI()


@app.get("/")
def read_root():
    return {"index_path": INDEX_PATH}


@app.get("/search/")
def search(query: str, size: int = 50):
    start = timer()
    hits = searcher.search(query, k=size)
    end = timer()
    total_time = end - start
    hits_clean = []
    for i in range(len(hits)):
        # content = "test speed"
        #content = hits[i].contents #index_reader.doc_contents(hits[i].docid)
        #content = get_wet_content(hits[i].docid)
        #title, url, content = parse_content(content)
        h = {
            "rank": i + 1,
            "docno": hits[i].docid,#.replace("<urn:uuid:", "").replace(">", ""),
            "score": hits[i].score,
            "title": hits[i].contents[:100],
            "snippet": hits[i].contents[:350]
        }
        hits_clean.append(h)

    return {
        "query": query,
        "total_matches": len(hits),
        "size": size,
        "total_time": total_time,
        "hits": hits_clean
    }


@app.get("/docs/{docno}/content")
def get_content(docno: str):
    content = ""# index_reader.doc_contents(docno)
    if content is None:
        raise HTTPException(status_code=404, detail="Doc not found")
    return {
        "docno": docno,
        "content": content
    }


@app.get("/docs/{docno}/raw")
def get_content(docno: str):
    raw = ""#index_reader.doc_raw(docno)
    if raw is None:
        raise HTTPException(status_code=404, detail="Doc not found")
    return {
        "docno": docno,
        "raw": raw
    }
