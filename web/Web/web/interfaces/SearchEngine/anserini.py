import requests
from config.settings.base import SEARCH_SERVER_IP
from config.settings.base import SEARCH_SERVER_PORT
from web.interfaces.SearchEngine.base import Search


class Anserini(Search):

    def search(self, query: str, number_of_results: int) -> list:
        r = requests.get("{}:{}/search/{}".format(SEARCH_SERVER_IP,
                                                  SEARCH_SERVER_PORT,
                                                  query))
        # Todo: check status code
        results = r.json()
        return []

    def get_content(self, docid: str) -> str:
        return ""

    def get_raw(self, docid: str) -> str:
        raise NotImplementedError
