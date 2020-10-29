import json

import requests
from config.settings.base import DEFAULT_NUM_DISPLAY
from config.settings.base import INDEX_NAME
from config.settings.base import SEARCH_SERVER_IP
from config.settings.base import SEARCH_SERVER_PORT
from config.settings.base import SEARCH_API_KEY
from web.interfaces.SearchEngine.base import SearchInterface


class Elastic(SearchInterface):
    headers = {
        'Accept': 'application/json',
        'Content-type': 'application/json',
        'Authorization': 'Apikey ' + SEARCH_API_KEY
    }
    url = f"{SEARCH_SERVER_IP}:{SEARCH_SERVER_PORT}/{INDEX_NAME}"

    @staticmethod
    def search(query: str, size: int = DEFAULT_NUM_DISPLAY, offset: int = 0):
        response = requests.get(
            f"{Elastic.url}/_search",
            headers=Elastic.headers,
            verify=False,
            data=json.dumps({
                "query": {
                    "match": {
                        "contents": query
                    }
                },
                "size": size,
                "from": offset,
                "highlight": {
                    "number_of_fragments": 3,
                    "fields": {
                        "contents": {}
                    }
                }
            })
        )

        response.raise_for_status()
        response_json = response.json()
        hits = []
        for i, hit in enumerate(response_json["hits"]["hits"]):
            content = hit["_source"]["contents"]
            title = content[:content[1:].index("\n")]

            hits.append({
                "rank": i,
                "docno": hit["_id"].replace("<urn:uuid:", "").replace(">", ""),
                "score": hit["_score"],
                "title": title,
                "snippet": '... '.join(hit["highlight"]["contents"]) + '... '
            })
        
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
            f"{Elastic.url}/_doc/{docno}/_source/",
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
            f"{Elastic.url}/_doc/{docno}/_source/",
            headers=Elastic.headers
        )
        response.raise_for_status()
        response_json = response.json()
        return {
            "docno": response_json["id"],
            "raw": response_json["raw"]
        }
