import requests
from config.settings.base import SEARCH_SERVER_IP
from config.settings.base import SEARCH_SERVER_PORT
from web.interfaces.SearchEngine.base import SearchInterface
from collections import OrderedDict


class Anserini(SearchInterface):

    @staticmethod
    def search(query: str, size: int):
        response = requests.get(
            f"http://{SEARCH_SERVER_IP}:{SEARCH_SERVER_PORT}/search",
            params={
                "query": query,
                "size": size
            }
        )
        response.raise_for_status()
        response_json = response.json()
        return response_json

    @staticmethod
    def get_content(docno: str):
        response = requests.get(
            f"http://{SEARCH_SERVER_IP}:{SEARCH_SERVER_PORT}/docs/{docno}/content",
        )
        response.raise_for_status()
        response_json = response.json()
        return response_json

    @staticmethod
    def get_raw(docno: str):
        response = requests.get(
            f"http://{SEARCH_SERVER_IP}:{SEARCH_SERVER_PORT}/docs/{docno}/raw",
        )
        response.raise_for_status()
        response_json = response.json()
        return response_json
