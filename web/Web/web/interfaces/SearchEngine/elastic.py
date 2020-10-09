import json

import requests
from config.settings.base import SEARCH_SERVER_IP
from config.settings.base import SEARCH_SERVER_PORT
from web.interfaces.SearchEngine.base import SearchInterface
from collections import OrderedDict


class Elastic(SearchInterface):
    headers = {'Accept': 'application/json', 'Content-type': 'application/json'}

    @staticmethod
    def search(query: str, size: int = 100):
        response = requests.get(
            f"http://{SEARCH_SERVER_IP}:{SEARCH_SERVER_PORT}/athome4/_search",
            data=json.dumps({
                "query": {
                    "match": {
                        "contents": query
                    }
                },
                "size": size,
            }),
            headers=Elastic.headers
        )

        response.raise_for_status()
        response_json = response.json()
        hits = [
            {
                "rank": i,
                "docno": hit["_id"],
                "score": hit["_score"],
                "title": hit["_source"]["contents"][:15],
                "snippet": hit["_source"]["contents"][:50],
            }
            for i, hit in enumerate(response_json["hits"]["hits"])
        ]
        return {
            "query": query,
            "total_matches": len(response_json["hits"]["hits"]),
            "size": size,
            "total_time": response_json["took"] / 1000,
            "hits": hits
        }

    @staticmethod
    def get_content(docno: str):
        response = requests.get(
            f"http://{SEARCH_SERVER_IP}:{SEARCH_SERVER_PORT}/athome4/_doc/{docno}/_source/",
            headers=Elastic.headers
        )
        response.raise_for_status()
        response_json = response.json()
        return {
            "docno": response_json["id"],
            "raw": response_json["contents"]
        }

    @staticmethod
    def get_raw(docno: str):
        response = requests.get(
            f"http://{SEARCH_SERVER_IP}:{SEARCH_SERVER_PORT}/athome4/_doc/{docno}/_source/",
            headers=Elastic.headers
        )
        response.raise_for_status()
        response_json = response.json()
        return {
            "docno": response_json["id"],
            "raw": response_json["raw"]
        }
