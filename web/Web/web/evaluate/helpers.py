import random


def is_doc_qrel_relevant(qrels, topic_id, doc_id):
    return bool(random.getrandbits(1))


def get_total_qrel_relevant_count(qrels, topic_id):
    return 100
