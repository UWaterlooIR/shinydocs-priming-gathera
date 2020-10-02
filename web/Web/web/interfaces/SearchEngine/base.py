from abc import ABC, abstractmethod


class Search(ABC):

    def __init__(self, host, port):
        self.host = host
        self.port = port
        super().__init__()

    @abstractmethod
    def search(self, query: str, number_of_results: int) -> list:
        """Returns a list of search results for a given query.
        E.g.
        [
            {
                "rank": 1
                "docid": "92302",
                "score": "34239",
                "title": "Title of document",
                "snippet": "A short highlight of the document based on the query"
            },
            ...
        ]
        """
        pass

    @abstractmethod
    def get_content(self, docid: str) -> str:
        """Returns the indexed content of the document

        """
        pass

    @abstractmethod
    def get_raw(self, docid: str) -> str:
        """Returns the raw document content

        """
        pass
