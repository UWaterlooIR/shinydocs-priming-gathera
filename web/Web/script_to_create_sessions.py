from web.core.models import Session
from web.users.models import User
from web.topic.models import Topic
import random
import string
class SessionType:
    def __init__(self, name, integrated_cal, nudge, search_disabled):
        self.name = name
        self.integrated_cal = integrated_cal
        self.nudge = nudge
        self.search_disabled = search_disabled


SESSION_TYPES = [
        SessionType('integrated-cal', True, False, False),
        SessionType('cal-only', False, False, True),
        SessionType('integrated-cal-with-nudge', True, True, False),
        SessionType('cal-with-nudge', False, True, False),
        SessionType('base', False, False, False)
    ]

queries = [
    'apple',
    'banana',
    'cherry',
    'date',
    'elderberry'
]

order = [1,4,5,2,3]

def create_5_sessions_for_user(q):
    random_username = f'experiment_user_{random.randint(1000, 9999)}'
    random_password = (f'{random.randint(1000, 9999)}_'
                       f'{random.choice(string.ascii_lowercase)}_{random.choice(string.ascii_uppercase)}')
    random_user = User.objects.create_user(random_username,
                                                 '{}@crazymail.com'.format(random_username),
                                                 random_password)
    random_user.save()
    print(random_username,  random_password)
    for i, session_to_create in enumerate(SESSION_TYPES):
        topic = Topic(
            title=f'{random_user.username}-{session_to_create.name}',
            seed_query=f'{q[i]}',
        )
        topic.save()
        session = Session.objects.create(
            username=random_user,
            integrated_cal=session_to_create.integrated_cal,
            nudge_to_cal=session_to_create.nudge,
            disable_search=session_to_create.search_disabled,
            topic=topic,
            session_order=order[i],
            max_number_of_judgments=0,
            show_full_document_content=False,
            strategy='doc',
            show_debugging_content=0,
            is_shared=False,
        )
        session.save()
    random_user.current_session = Session.objects.filter(username=random_user).order_by('session_order').first()
    random_user.save()
