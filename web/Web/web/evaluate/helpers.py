
def is_doc_qrel_relevant(qrels, topic_id, doc_id):
    if topic_id in qrels and doc_id in qrels[topic_id]:
        return qrels[topic_id][doc_id] > 0
    return False


def get_total_qrel_relevant_count(qrels, topic_id):

    count = 0
    if topic_id in qrels:
        for d in qrels[topic_id]:
            count += (qrels[topic_id][d] > 0)
    return count
