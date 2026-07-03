import json
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

import requests

import settings
from dashboardHelper.futureSection import (
    CWA_DATASET, CWA_LOCATION, TIME_SLOTS, TAIWAN_TZ,
    _day_label, _parse_dt, _avg, _day_summary_messages,
    _has_explicit_date, _parse_explicit_date,
)

_WEEKDAY_NAMES = ['一', '二', '三', '四', '五', '六', '日']
_TODO_LOOKAHEAD_DAYS = 2  # 今天、明天、後天 = 0~2 天後
_BUDGET_CATEGORIES_TO_ANNOUNCE = ['外食餐費', '生鮮&調味料', '生活用品', '利卡', '璇璇', '娛樂', '醫療保健']
_BUDGET_ALERT_THRESHOLD_PCT = 60


def _fetch_weather_lines():
    try:
        now = datetime.now(TAIWAN_TZ)
        today = now.date()
        target_dates = [today + timedelta(days=i) for i in range(_TODO_LOOKAHEAD_DAYS + 1)]

        url = (f'https://opendata.cwa.gov.tw/api/v1/rest/datastore/{CWA_DATASET}'
               f'?Authorization={settings.CWA_API_KEY}')
        resp = requests.get(url, timeout=25)
        resp.raise_for_status()
        data = resp.json()

        all_locs = data['records']['Locations'][0]['Location']
        loc = next((l for l in all_locs if l['LocationName'] == CWA_LOCATION), None)
        if not loc:
            return ['天氣資料暫時無法取得。']

        elements = {el['ElementName']: el for el in loc['WeatherElement']}

        temp_dh = defaultdict(dict)
        for slot in elements.get('溫度', {}).get('Time', []):
            dt = _parse_dt(slot.get('DataTime', ''))
            if not dt:
                continue
            try:
                temp_dh[dt.date()][dt.hour] = int(slot['ElementValue'][0]['Temperature'])
            except (KeyError, ValueError, IndexError):
                pass

        rain_dh = defaultdict(dict)
        for slot in elements.get('3小時降雨機率', {}).get('Time', []):
            dt = _parse_dt(slot.get('StartTime', ''))
            if not dt:
                continue
            try:
                rain_dh[dt.date()][dt.hour] = int(slot['ElementValue'][0]['ProbabilityOfPrecipitation'])
            except (KeyError, ValueError, IndexError):
                pass

        lines = []
        for d in target_dates:
            label, _ = _day_label(d, today)
            slots_data = []
            for slot_name, _slot_time, temp_hours, rain_hours in TIME_SLOTS:
                temps = [temp_dh[d][h] for h in temp_hours if h in temp_dh[d]]
                rains = [rain_dh[d][h] for h in rain_hours if h in rain_dh[d]]
                slots_data.append((slot_name, _avg(temps), _avg(rains)))
            messages = _day_summary_messages(slots_data)
            if messages:
                lines.append(f'{label}{"，".join(messages)}')
        return lines
    except Exception:
        return ['天氣資料暫時無法取得。']


def _fetch_upcoming_todo_and_purchase():
    try:
        r = requests.get(settings.URL_GAS_API, params={'action': 'action_get_dashboard_future'}, timeout=25)
        future_data = json.loads(r.json().get('responseMsg', '{}'))
    except Exception:
        return None, None

    today = datetime.now(TAIWAN_TZ).date()
    todo_lines = []
    for item in future_data.get('memo', []):
        content = item.get('content', '').strip()
        if not content or not _has_explicit_date(content):
            continue
        d = _parse_explicit_date(content, today)
        if d is None:
            continue
        days_until = (d - today).days
        if 0 <= days_until <= _TODO_LOOKAHEAD_DAYS:
            todo_lines.append(content)

    purchase_lines = [item.get('name', '').strip() for item in future_data.get('purchase', [])
                       if item.get('name', '').strip()]
    return todo_lines, purchase_lines


def _fetch_budget_lines():
    try:
        r = requests.get(settings.URL_GAS_API, params={'action': 'action_get_budget_status'}, timeout=25)
        budget = json.loads(r.json().get('responseMsg', '{}'))
    except Exception:
        return None

    lines = []
    for cat in budget.get('categories', []):
        if cat.get('name') not in _BUDGET_CATEGORIES_TO_ANNOUNCE:
            continue
        effective_budget = cat.get('effectiveBudget', 0)
        if effective_budget <= 0:
            continue
        pct = int(cat.get('spent', 0) / effective_budget * 100)
        if pct < _BUDGET_ALERT_THRESHOLD_PCT:
            continue
        if cat.get('isOverBudget'):
            lines.append(f'{cat["name"]}已經超支{cat.get("overspent", 0)}元，沒有剩餘預算')
        else:
            remaining = effective_budget - cat.get('spent', 0)
            lines.append(f'{cat["name"]}已使用{pct}%，剩餘{remaining}元可以使用')
    return lines


def generate_text():
    with ThreadPoolExecutor(max_workers=3) as ex:
        weather_f = ex.submit(_fetch_weather_lines)
        todo_f = ex.submit(_fetch_upcoming_todo_and_purchase)
        budget_f = ex.submit(_fetch_budget_lines)
        weather_lines = weather_f.result()
        todo_lines, purchase_lines = todo_f.result()
        budget_lines = budget_f.result()

    now = datetime.now(TAIWAN_TZ)
    parts = [f'今天是{now.month}月{now.day}日星期{_WEEKDAY_NAMES[now.weekday()]}。']

    if weather_lines:
        parts.append('天氣方面，' + '；'.join(weather_lines) + '。')
    else:
        parts.append('接下來三天天氣穩定，沒有特別提醒。')

    if todo_lines is None:
        parts.append('待辦事項資料暫時無法取得。')
    elif todo_lines:
        parts.append('接下來三天的待辦事項：' + '；'.join(todo_lines) + '。')
    else:
        parts.append('接下來三天沒有待辦事項。')

    if purchase_lines is None:
        parts.append('待買清單資料暫時無法取得。')
    elif purchase_lines:
        parts.append(f'待買清單目前有{len(purchase_lines)}項，分別是' + '、'.join(purchase_lines) + '。')
    else:
        parts.append('待買清單目前是空的。')

    if budget_lines is None:
        parts.append('預算資料暫時無法取得。')
    elif budget_lines:
        parts.append('預算方面，' + '；'.join(budget_lines) + '。')
    else:
        parts.append('預算控制得宜，沒有分類超過六十%。')

    return '\n\n'.join(parts)
