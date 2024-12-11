from web.core.models import Session
from web.judgment.models import Judgment
from web.search.models import Query


def extract_session_judgments(session_id):
    """
    Extracts list of judgments for a given session
    """
    session = Session.objects.get(id=session_id)
    judgments_for_session = Judgment.objects.filter(session=session).order_by('created_at')
    judgments = []
    for judgment in judgments_for_session:
        judgments.append((judgment.doc_id, judgment.relevance))
    return judgments

def get_all_search_queries_for_session(session_id):
    """
    Extracts all search queries for a given session
    """
    session = Session.objects.get(id=session_id)
    search_queries = Query.objects.filter(session=session).order_by('created_at')
    queries = []
    for search_query in search_queries:
        queries.append(search_query.query)
    return queries

def get_session_stats(session_id, should_print=True):
    """
    Extracts session statistics
    """
    session = Session.objects.get(id=session_id)
    judgments_for_session = Judgment.objects.filter(session=session)
    total_judgments = judgments_for_session.count()
    relevant_judgments = judgments_for_session.filter(relevance__in=[1,2]).count()
    non_relevant_judgments = judgments_for_session.filter(relevance=0).count()
    total_search_queries = Query.objects.filter(session=session).count()
    timespent_in_minutes_and_seconds = session.timespent // 60, session.timespent % 60
    if should_print:
        print(
            f'Total Judgments: {total_judgments}\n'
            f'Relevant Judgments: {relevant_judgments}\n'
            f'Non-Relevant Judgments: {non_relevant_judgments}\n'
            f'Total Search Queries: {total_search_queries}\n'
            f'Time Spent: {timespent_in_minutes_and_seconds[0]} minutes'
            f' {timespent_in_minutes_and_seconds[1]} seconds'
        )
    return (total_judgments, relevant_judgments, non_relevant_judgments, total_search_queries,
            session.timespent)

def get_session_stats_for_all_sessions_for_a_user(user_id):
    """
    Extracts session statistics for all sessions for a user
    """
    sessions = Session.objects.filter(username=user_id,)
    total_sessions = sessions.count()
    total_timespent_on_all_sessions = 0
    total_rel_judgments = 0
    total_non_rel_judgments = 0
    total_judgments = 0
    total_search_queries = 0
    session_with_most_spent_time = None
    print(
        f'User ID: {user_id}\n'
        f'Total Sessions: {total_sessions}\n'
    )
    for session in sessions:
        session_with_most_spent_time = session if not session_with_most_spent_time or \
            session_with_most_spent_time.timespent < session.timespent else session_with_most_spent_time
        total_timespent_on_all_sessions += session.timespent
        print(f'Session ID: {session.id}')
        stats = get_session_stats(session.id, should_print=False)
        total_judgments += stats[0]
        total_rel_judgments += stats[1]
        total_non_rel_judgments += stats[2]
        total_search_queries += stats[3]
        print('\n')
    total_timespent_in_minutes_and_seconds = total_timespent_on_all_sessions // 60, total_timespent_on_all_sessions % 60
    print(
        f'Total Sessions: {total_sessions}\n'
        f'Total Time Spent on all Sessions: {total_timespent_in_minutes_and_seconds[0]} minutes'
        f' {total_timespent_in_minutes_and_seconds[1]} seconds\n'
        f'Total Judgments: {total_judgments}\n'
        f'Total Relevant Judgments: {total_rel_judgments}\n'
        f'Total Non-Relevant Judgments: {total_non_rel_judgments}\n'
        f'Total Search Queries: {total_search_queries}\n'
        f'Session with Most Time Spent: {session_with_most_spent_time.id}'
    )


def mean_user_reported_rel_docs_by_session_type():
    integrated_cal_sessions = Session.objects.filter(integrated_cal=True, nudge_to_cal=False)
    cal_only_sessions = Session.objects.filter(integrated_cal=False, nudge_to_cal=False,
                                               disable_search=True)
    integrated_cal_with_nudge_sessions = Session.objects.filter(integrated_cal=True, nudge_to_cal=True)
    cal_with_nudge_sessions = Session.objects.filter(integrated_cal=False, nudge_to_cal=True)
    base_sessions = Session.objects.filter(integrated_cal=False, nudge_to_cal=False, disable_search=False)
    session_types = [
        (integrated_cal_sessions, 'integrated_cal'), (cal_only_sessions, 'cal_only'),
        (integrated_cal_with_nudge_sessions, 'integrated_cal_with_nudge'), (cal_with_nudge_sessions, 'cal_with_nudge'),
        (base_sessions, 'base')
    ]
    for session in session_types:
        print(f'Session Type: {session[1]}')
        (mean_judgments, mean_rel_judgments, mean_non_rel_judgments, mean_search_queries,
         mean_timespent_on_all_sessions) = get_mean_stats(session[0])


def get_mean_stats(sessions):
    total_rel_judgments = 0
    total_non_rel_judgments = 0
    total_judgments = 0
    total_search_queries = 0
    total_timespent_on_all_sessions = 0
    for session in sessions:
        stats = get_session_stats(session.id, should_print=False)
        total_judgments += stats[0]
        total_rel_judgments += stats[1]
        total_non_rel_judgments += stats[2]
        total_search_queries += stats[3]
        total_timespent_on_all_sessions += stats[4]
    mean_rel_judgments = total_rel_judgments / sessions.count()
    mean_non_rel_judgments = total_non_rel_judgments / sessions.count()
    mean_judgments = total_judgments / sessions.count()
    mean_search_queries = total_search_queries / sessions.count()
    mean_timespent_on_all_sessions = total_timespent_on_all_sessions / sessions.count()
    print(
        f'Total Sessions: {sessions.count()}\n'
        f'Mean Time Spent on all Sessions: {mean_timespent_on_all_sessions}\n'
        f'Mean Judgments: {mean_judgments}\n'
        f'Mean Relevant Judgments: {mean_rel_judgments}\n'
        f'Mean Non-Relevant Judgments: {mean_non_rel_judgments}\n'
        f'Mean Search Queries: {mean_search_queries}\n\n'
    )
    return (mean_judgments, mean_rel_judgments, mean_non_rel_judgments, mean_search_queries,
            mean_timespent_on_all_sessions)
