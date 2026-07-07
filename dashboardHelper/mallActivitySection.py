import html as html_lib
import json
from datetime import datetime, timezone, timedelta

import requests

TAIWAN_TZ = timezone(timedelta(hours=8))


def _parse_date(date_str):
    try:
        return datetime.strptime(str(date_str).strip(), '%Y/%m/%d').date()
    except (ValueError, TypeError):
        return None


def _format_date(d):
    return f'{d.month}/{d.day}'


def generate_html(gas_url):
    try:
        r = requests.get(gas_url, params={'action': 'action_get_mall_activities'}, timeout=25)
        activities = json.loads(r.json().get('responseMsg', '[]'))
    except Exception as e:
        return f'<div class="wip">商場活動資料載入失敗：{html_lib.escape(str(e))}</div>'

    today = datetime.now(TAIWAN_TZ).date()
    rows = []
    for item in activities:
        mall_name = str(item.get('mallName', '')).strip()
        activity_name = str(item.get('activityName', '')).strip()
        if not mall_name or not activity_name:
            continue
        start = _parse_date(item.get('startDate', ''))
        end = _parse_date(item.get('endDate', ''))
        if end and end < today:
            continue
        rows.append((start, mall_name, activity_name, end))

    if not rows:
        return (
            '<div class="section">'
            '<div class="section-title">商場活動</div>'
            '<div class="chart-card" style="text-align:center;padding:24px;'
            'color:#94A3B8;font-size:13px;">尚無活動資料</div>'
            '</div>'
        )

    rows.sort(key=lambda x: (x[0] is None, x[0]))

    items_html = ''
    for start, mall_name, activity_name, end in rows:
        if start and end:
            date_label = f'{_format_date(start)}~{_format_date(end)}'
        elif end:
            date_label = f'~{_format_date(end)}'
        elif start:
            date_label = f'{_format_date(start)}~'
        else:
            date_label = ''
        content = f'{mall_name} {date_label} {activity_name}'.strip()
        items_html += f'<div class="future-item"><span class="future-item-content">{html_lib.escape(content)}</span></div>'

    return (
        '<div class="section">'
        '<div class="section-title">商場活動</div>'
        f'<div class="future-list-card">{items_html}</div>'
        '</div>'
    )
