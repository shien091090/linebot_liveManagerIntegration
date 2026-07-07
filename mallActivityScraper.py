import html
import json
import re
from datetime import datetime, timezone, timedelta

import requests

import settings

TAIWAN_TZ = timezone(timedelta(hours=8))
USER_AGENT = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
              '(KHTML, like Gecko) Chrome/124.0 Safari/537.36')

_SOGO_ITEM_RE = re.compile(
    r'<div class="in_n_items">.*?<span>\s*([^<]+?)\s*</span>\s*<div class="in_h3">\s*<h3>\s*([^<]+?)\s*</h3>',
    re.S
)
_SOGO_FULL_RANGE_RE = re.compile(
    r'(\d{4})/(\d{1,2})/(\d{1,2})\([^)]*\)\s*~\s*(?:(\d{4})/)?(\d{1,2})/(\d{1,2})\([^)]*\)'
)
_SOGO_START_ONLY_RE = re.compile(r'(\d{4})/(\d{1,2})/(\d{1,2})\([^)]*\)\s*~')

_LIHPAO_ITEM_RE = re.compile(
    r'<div class="item-wrap[^"]*">.*?<img[^>]*alt="([^"]*)"[^>]*>.*?'
    r'<div class="item-title">([^<]*)</div>\s*<div class="item-text">(.*?)</div>',
    re.S
)
_LIHPAO_DATE_PATTERNS = [
    re.compile(r'(\d{4})[/.](\d{1,2})[/.](\d{1,2})\s*[-~]\s*(\d{4})[/.](\d{1,2})[/.](\d{1,2})'),
    re.compile(r'(\d{4})[/.](\d{1,2})[/.](\d{1,2})\s*[-~]\s*(\d{1,2})[/.](\d{1,2})'),
    re.compile(r'(\d{1,2})[/.](\d{1,2})\s*[-~]\s*(\d{1,2})[/.](\d{1,2})'),
]


def _fmt_date(y, m, d):
    return f'{int(y):04d}/{int(m):02d}/{int(d):02d}'


def _clean_text(s):
    s = html.unescape(s)
    return re.sub(r'\s+', ' ', s).strip()


def _truncate(text, max_len=24):
    text = text.strip()
    return text if len(text) <= max_len else text[:max_len] + '…'


def _is_expired(end_date_str, today):
    if not end_date_str:
        return False
    try:
        return datetime.strptime(end_date_str, '%Y/%m/%d').date() < today
    except ValueError:
        return False


def _parse_sogo(page_html):
    results = []
    for date_text, title in _SOGO_ITEM_RE.findall(page_html):
        date_text = _clean_text(date_text)
        title = _clean_text(title)
        if not title:
            continue

        m = _SOGO_FULL_RANGE_RE.search(date_text)
        if m:
            sy, sm, sd, ey, em, ed = m.groups()
            results.append((title, _fmt_date(sy, sm, sd), _fmt_date(ey or sy, em, ed)))
            continue

        m = _SOGO_START_ONLY_RE.search(date_text)
        if m:
            sy, sm, sd = m.groups()
            results.append((title, _fmt_date(sy, sm, sd), ''))
    return results


def _resolve_lihpao_date(match, today):
    g = match.groups()
    if len(g) == 6:
        sy, sm, sd, ey, em, ed = g
        return _fmt_date(sy, sm, sd), _fmt_date(ey, em, ed)
    if len(g) == 5:
        sy, sm, sd, em, ed = g
        return _fmt_date(sy, sm, sd), _fmt_date(sy, em, ed)
    # len(g) == 4: "M/d - M/d" with no year given, infer from today's date
    sm, sd, em, ed = g
    year = today.year
    try:
        start = datetime(year, int(sm), int(sd)).date()
    except ValueError:
        return None
    if (today - start).days > 60:
        year += 1
    return _fmt_date(year, sm, sd), _fmt_date(year, em, ed)


def _extract_lihpao_date_range(text, today):
    for pattern in _LIHPAO_DATE_PATTERNS:
        m = pattern.search(text)
        if m:
            resolved = _resolve_lihpao_date(m, today)
            if resolved:
                return resolved
    return None


def _parse_lihpao(page_html, today):
    results = []
    for alt_text, title, body_text in _LIHPAO_ITEM_RE.findall(page_html):
        title = _clean_text(title)
        if not title:
            continue
        combined_text = f'{_clean_text(alt_text)} {_clean_text(body_text)} {title}'
        date_range = _extract_lihpao_date_range(combined_text, today)
        if not date_range:
            continue
        start, end = date_range
        results.append((title, start, end))
    return results


_PARSERS = {'sogo': _parse_sogo, 'lihpao': lambda page_html: _parse_lihpao(page_html, _today())}


def _today():
    return datetime.now(TAIWAN_TZ).date()


def fetch_activities():
    with open('mallActivitySources.json', encoding='utf-8') as f:
        sources = json.load(f)

    today = _today()
    activities = []

    for source in sources:
        mall_name = source['mallName']
        parser_name = source.get('parser')
        parser = _PARSERS.get(parser_name)
        if not parser:
            print(f'[{mall_name}] unknown parser "{parser_name}", skipped')
            continue

        try:
            resp = requests.get(source['url'], headers={'User-Agent': USER_AGENT}, timeout=25)
            resp.raise_for_status()
        except Exception as e:
            print(f'[{mall_name}] fetch failed: {e}')
            continue

        parsed = parser(resp.text)
        kept = 0
        for title, start, end in parsed:
            if _is_expired(end, today):
                continue
            activities.append({
                'mallName': mall_name,
                'activityName': _truncate(title),
                'startDate': start,
                'endDate': end,
            })
            kept += 1
        print(f'[{mall_name}] parsed {len(parsed)} items, kept {kept} after expiry filter')

    return activities


def main():
    activities = fetch_activities()
    payload = json.dumps(activities, ensure_ascii=False)
    print(f'Writing {len(activities)} activities to GAS...')

    r = requests.post(
        f'{settings.URL_GAS_API}?action=action_set_mall_activities',
        headers={'Content-Type': 'application/json'},
        data=payload.encode('utf-8'),
        timeout=30
    )
    print(f'POST status: {r.status_code}')

    verify = requests.get(f'{settings.URL_GAS_API}?action=action_get_mall_activities', timeout=25)
    print('Verify response:', verify.text[:800])


if __name__ == '__main__':
    main()
