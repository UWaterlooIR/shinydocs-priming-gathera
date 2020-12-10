import httplib2
import requests

from config.settings.base import DOCUMENTS_URL
from config.settings.base import PARA_URL
from django.core.cache import cache
from web.core.models import CCNewsRecord
import os
import subprocess

import httplib2

def get_wet_content(record_id):
    try:
        row = CCNewsRecord.objects.get(record_id="{}".format(record_id))
    except CCNewsRecord.DoesNotExist:
        raise CCNewsRecord.DoesNotExist(f'{record_id} not found in CCNewsRecord database.')

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
    url = url.strip()

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
        found = True

        if cache.get(doc_id):
            title, url, content = cache.get(doc_id)
        else:
            try:
                content = get_wet_content(doc_id)
            except CCNewsRecord.DoesNotExist:
                title = '<i class="text-danger">The document is not found in the database record.</i>'
                content = '<i class="text-danger">The document is not found in the database record. Could not fetch it\'s content.</i>'
                found = False
            except Exception:
                title = '<i class="text-danger">Error occured while fetching document.</i>'
                content = '<i class="text-danger">An error occured while fetching document content.</i>'
                found = False
            else:
                if content:
                    title, url, content = parse_content(content)
                    cache.set(doc_id, [title, url, content], 60*30)

        if len(content) == 0:
            if len(title) == 0:
                title = '<i class="text-warning">The document title is empty</i>'
            content = '<i class="text-warning">The document content is empty. Possibly could not fetch content.</i>'
        else:
            if len(title) == 0:
                title = content[:32]

        document = {
            'doc_id': doc_id.replace("<urn:uuid:", "").replace(">", ""),
            'title': title,
            'content': content.replace("\n", "<br/>"),
            'date': url,
            'top_terms': {},
            'ok': found == True
        }
        result.append(document)

    return result



def get_documents_with_snippet(doc_ids, query=None, top_terms=None):
    raise NotImplementedError 
