from config.settings.base import ANSERINI_INDEX_PATH
from config.settings.base import DOCUMENTS_URL
from config.settings.base import PARA_URL
import json

import httplib2
from pyserini import index

index_reader = index.IndexReader(ANSERINI_INDEX_PATH)


def get_documents(doc_ids, query=None, top_terms=None, orig_para_id=None):
    """
    :param orig_para_id:
    :param top_terms:
    :param query:
    :param doc_ids: the ids of documents to return
    :return: documents content
    """
    result = []
    for idx, doc_id in enumerate(doc_ids):

        raw = index_reader.doc(doc_id).raw()
        content = json.loads(raw)
        url = content["url"]
        content = content["text"].split("\n")
        title = content[0]
        content = "\n".join(content[1:])

        if len(content) == 0:
            if len(title) == 0:
                title = '<i class="text-warning">The document title is empty</i>'
            content = '<i class="text-warning">The document content is empty</i>'
        else:
            if len(title) == 0:
                title = content[:32]

        document = {
            'doc_id': doc_id,
            'title': title,
            'content': content.replace("\n", "<br/>"),
            'date': url,
            'top_terms': top_terms.get(doc_id if orig_para_id is None else "{}.{}".format(doc_id, orig_para_id[idx]), None) if top_terms else None,
            'ok': True if content else False
        }
        result.append(document)

    return result


def get_documents_with_snippet(doc_ids, query=None, top_terms=None):
    h = httplib2.Http()
    url = "{}/{}"
    doc_ids_unique = []
    doc_ids_set = set()
    for doc_id in doc_ids:
        if doc_id['doc_id'] not in doc_ids_set:
            doc_ids_set.add(doc_id['doc_id'])
            doc_ids_unique.append(doc_id)

    doc_ids = doc_ids_unique

    result = get_documents([doc['doc_id'] for doc in doc_ids], query, top_terms, [doc['para_id'] for doc in doc_ids if 'para_id' in doc])
    for doc_para_id, doc in zip(doc_ids, result):
        if 'para_id' not in doc_para_id:
            doc['snippet'] = u''
            continue
        try:
            para_id = doc_para_id['doc_id'] + '.' + doc_para_id['para_id']
            resp, content = h.request(url.format(PARA_URL, para_id),
                                      method="GET")
            doc['snippet'] = content.decode('utf-8', 'ignore').replace("\n", "<br />")
        except:
            doc['snippet'] = u''
    return result
