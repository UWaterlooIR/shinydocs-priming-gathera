from web.judgment.models import Judgment
from web.evaluate import helpers


def user_reported_rel__user_found_rel(session, qrel):
    data = []
    judgments = Judgment.objects.filter(
        session=session).filter(
        relevance__isnull=False).order_by('-created_at')

    topic_id = str(session.topic.number)
    total_relevant_count = helpers.get_total_qrel_relevant_count(qrel, topic_id)
    total_user_reported_rel_found_qrel_rel = 0
    total_user_reported_rel_count = float(len(judgments))
    for idx, j in enumerate(judgments, 1):
        is_doc_qrel_relevant = helpers.is_doc_qrel_relevant(qrel, topic_id, j.doc_id)
        total_user_reported_rel_found_qrel_rel += is_doc_qrel_relevant
        data.append({
            "x": idx,
            "x_percent": round(idx/total_user_reported_rel_count, 2) if total_user_reported_rel_count else 0,
            "y": total_user_reported_rel_found_qrel_rel,
            "y_percent": round(total_user_reported_rel_found_qrel_rel/total_relevant_count, 2) if total_relevant_count else 0.0
        })
    return data
