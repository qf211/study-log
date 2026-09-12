from datetime import datetime

def is_valid_minutes(m):
    return 1 <= m <= 600

def parse_date(s):
    try:
        datetime.strptime(s, '%Y-%m-%d')
        return s
    except(ValueError, TypeError):
        return None

def is_valid_topic(t):
    return isinstance(t, str) and 1 <= len(t.strip()) <= 200
