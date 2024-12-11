import random


SEED = 2025

treatments_base = [
    ['A', 'B', 'C', 'D', 'E'],
    ['B', 'C', 'D', 'E', 'A'],
    ['C', 'D', 'E', 'A', 'B'],
    ['D', 'E', 'A', 'B', 'C'],
    ['E', 'A', 'B', 'C', 'D'],
]

topics_base = [
    ['a', 'b', 'c', 'd', 'e'],
    ['c', 'd', 'e', 'a', 'b'],
    ['e', 'a', 'b', 'c', 'd'],
    ['b', 'c', 'd', 'e', 'a'],
    ['d', 'e', 'a', 'b', 'c'],
]

def print_latin_sq(sq):
    for i in sq:
        print(i)
    print('------------------------------')


def shuffle_rows(sq):
    random.seed(SEED)
    random.shuffle(sq)
    return sq


def shuffle_columns(latin_square):
    random.seed(SEED)
    # Get the number of columns (same as rows in a square matrix)
    n = len(latin_square)
    # Generate a list of column indices
    column_indices = list(range(n))
    # Shuffle the column indices
    random.shuffle(column_indices)
    # Create a new square matrix by reordering columns
    shuffled_square = []
    for row in latin_square:
        shuffled_row = [row[i] for i in column_indices]
        shuffled_square.append(shuffled_row)
    return shuffled_square

def shuffle_rows_and_columns(latin_square):
    random.seed(SEED)
    return shuffle_columns(shuffle_rows(latin_square))

def superimposed_latin_square(treatments, topics):
    random.seed(SEED)
    super_imposed_square = []
    for i in range(len(treatments)):
        super_imposed_square.append([])
        for j in range(len(topics)):
            super_imposed_square[i].append((treatments[i][j], topics[i][j]))
    print_latin_sq(super_imposed_square)
    return super_imposed_square


def test_latin_sq_correct(latin_sq):
    # Check that each row contains all the treatments
    for row in latin_sq:
        if len(set(row)) != len(row):
            return False
    # Check that each column contains all the topics
    for i in range(len(latin_sq)):
        column = [latin_sq[j][i] for j in range(len(latin_sq))]
        if len(set(column)) != len(column):
            return False
    return True




class Topic:
    def __init__(self, seed_query, description=None, narrative=None, label=None):
        self.seed_query = seed_query
        self.description = description
        self.narrative = narrative
        self.label = label

    def add_label(self, label):
        assert label in ['a', 'b', 'c', 'd', 'e']
        self.label = label

    def __str__(self):
        return f'{self.seed_query} - {self.label}'


class SessionType:
    def __init__(self, name, integrated_cal, nudge, search_disabled, label=None):
        self.name = name
        self.integrated_cal = integrated_cal
        self.nudge = nudge
        self.search_disabled = search_disabled
        self.label = label

    def add_label(self, label):
        assert label in ['A', 'B', 'C', 'D', 'E']
        self.label = label

    def __str__(self):
        return f'{self.name} - {self.label}'



SESSION_TYPES = [
        SessionType('integrated-cal', True, False, False),
        SessionType('cal-only', False, False, True),
        SessionType('integrated-cal-with-nudge', True, True, False),
        SessionType('cal-with-nudge', False, True, False),
        SessionType('base', False, False, False)
]

TOPICS = [
    Topic('apple',),
    Topic('banana'),
    Topic('cherry'),
    Topic('date'),
    Topic('elderberry')
]

def map_labels_to_treatments_and_topics(session_types, topics_list):
    session_mapping = {}
    for i in range(len(session_types)):
        session_mapping[session_types[i].label] = session_types[i]
    topic_mapping = {}
    for i in range(len(topics_list)):
        topic_mapping[topics_list[i].label] = topics_list[i]
    return session_mapping, topic_mapping



def assign_random_labels_to_topics_and_sessions(sessions, topics, ):
    random.seed(SEED)
    topics_choices = ['a', 'b', 'c', 'd', 'e']
    sessions_choices = ['A', 'B', 'C', 'D', 'E']
    for i in range(len(topics)):
        topics[i].add_label(random.choice(topics_choices))
        topics_choices.remove(topics[i].label)
    for i in range(len(sessions)):
        sessions[i].add_label(random.choice(sessions_choices))
        sessions_choices.remove(sessions[i].label)
    return sessions, topics

def add_topics_and_sessions_to_latin_square(session_mapping, topic_mapping, latin_square):
    for i in range(len(latin_square)):
        for j in range(len(latin_square[i])):
            latin_square[i][j] = (session_mapping[latin_square[i][j][0]], topic_mapping[latin_square[i][j][1]])
    return latin_square


def create_final_latin_square(treatments, topics, base_latin_treatments, base_latin_topics):
    latin_sq = superimposed_latin_square(base_latin_treatments, base_latin_topics)
    latin_sq = shuffle_rows_and_columns(latin_sq)
    assert test_latin_sq_correct(latin_sq)
    sessions, topics = assign_random_labels_to_topics_and_sessions(treatments, topics)
    session_mapping, topic_mapping = map_labels_to_treatments_and_topics(sessions, topics)
    final_latin_sq = add_topics_and_sessions_to_latin_square(session_mapping, topic_mapping, latin_sq)
    assert test_latin_sq_correct(final_latin_sq)
    return final_latin_sq

create_final_latin_square(SESSION_TYPES, TOPICS, treatments_base, topics_base)
