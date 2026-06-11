import re
from datetime import date, timedelta

COLOR_DEFAULT = '#5e637e'
COLOR_PAST = '#CC0000'
COLOR_UPCOMING = '#E5A800'


def _parse_date_from_text(text, current_year):
    m = re.search(r'(\d{4})/(\d{1,2})/(\d{1,2})', text)
    if m:
        try:
            return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            pass

    m = re.search(r'(?<!\d)(\d{1,2})/(\d{1,2})(?!\d)', text)
    if m:
        try:
            return date(current_year, int(m.group(1)), int(m.group(2)))
        except ValueError:
            pass

    return None


def get_memo_item_color(text, today):
    parsed = _parse_date_from_text(text, today.year)
    if parsed is None:
        return COLOR_DEFAULT
    if parsed <= today:
        return COLOR_PAST
    if parsed <= today + timedelta(days=7):
        return COLOR_UPCOMING
    return COLOR_DEFAULT


def build_colored_memo_items(response_msg, today):
    lines = [line for line in response_msg.split('\n') if line.strip()]
    return [(line, get_memo_item_color(line, today)) for line in lines]
