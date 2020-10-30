from config.settings.base import DOCUMENTS_URL
from config.settings.base import PARA_URL
from django.core.cache import cache
from web.core.models import CCNewsRecord
import os
import subprocess

import httplib2

try:
    # For c speedups
    from simplejson import loads
except ImportError:
    from json import loads


def get_date(content):
    for line in content.split('\n'):
        if line.strip()[:4] == "Sent":
            try:
                return line.split(':', 1)[1].strip()
            except:
                pass
    return ""


def get_subject(content):
    for line in content.split('\n'):
        if line.strip()[:7] == "Subject":
            return line.split(':', 1)[1].strip()
    return ""


def get_wet_content(record_id):
    try:
        row = CCNewsRecord.objects.get(record_id="{}".format(record_id))
    except:
        return ""

    if row:
        wet_path = "/cc/wet/{}/{}/{}".format(row.year, row.month, row.filename)

        opts = ["-s", row.offset]
        my_cmd = ["/zpipe/zchunk"] + opts
        result = ""
        with open(wet_path, "r") as infile:
            result = subprocess.run(my_cmd, stdin=infile, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.decode('utf-8')


def parse_content(content):
    # Get url
    start_url = content.index("WARC-Target-URI: ") + 17
    url = content[start_url:content.index("\n", start_url)]
    
    # Get to the actual document content
    content = content[content.index("\n", content.index("Content-Length:")):]
    lines = content.splitlines()
    
    def clean(line):
        words = line.split()
        # Remove lines with less than 5 words
        if len(words) <= 5:
            return False
        # Remove lines that contain a word with >= 50 chars
        if any(len(y) >= 50 for y in words):
            return False

        return True

    lines = list(filter(None, lines))
    title = lines[0][:100]

    # Clean content
    lines  = list(filter(lambda line: clean(line), lines))

    # Create paragraphs
    paragraphs = "".join("<p>{}</p>".format(line) for line in lines[1:])

    return title, url, paragraphs


def get_documents(doc_ids, query=None, top_terms=None, orig_para_id=None):
    """
    :param query:
    :param doc_ids: the ids of documents to return
    :return: documents content
    """

    result = []
    for idx, doc_id in enumerate(doc_ids):
        if not doc_id.startswith("<urn:uuid:"):
            doc_id = "<urn:uuid:{}>".format(doc_id)
    
        title = ""
        content = ""
        url = ""

        if cache.get(doc_id):
            title, url, content = cache.get(doc_id)
        else:
            content = get_wet_content(doc_id)
            if content:
                title, url, content = parse_content(content)
                cache.set(doc_id, [title, url, content], 60*30)

        if len(content) == 0:
            if len(title) == 0:
                title = '<i class="text-warning">The document title is empty</i>'
            content = '<i class="text-warning">The document content is empty. Possibly could not fetch content</i>'
        else:
            if len(title) == 0:
                title = content[:32]

        document = {
            'doc_id': doc_id.replace("<urn:uuid:", "").replace(">", ""),
            'title': title,
            'content': content.replace("\n", "<br/>"),
            'date': url,
            'top_terms': {}
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
