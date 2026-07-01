import requests
import html as html_lib
import json
import re
from datetime import datetime, date, timezone, timedelta
from collections import defaultdict
import settings

TAIWAN_TZ = timezone(timedelta(hours=8))
CWA_DATASET = 'F-D0047-073'
CWA_LOCATION = '西屯區'
WEEKDAY_NAMES = ['週一', '週二', '週三', '週四', '週五', '週六', '週日']

# (label, time_display, temp_hours, rain_start_hours)
TIME_SLOTS = [
    ('早上', '06–12', range(6, 12),  [6, 9]),
    ('下午', '12–18', range(12, 18), [12, 15]),
    ('晚上', '18–00', range(18, 24), [18, 21]),
]


def _day_label(d, today):
    delta = (d - today).days
    wd = WEEKDAY_NAMES[d.weekday()]
    if delta == 0:
        return '今天', wd
    if delta == 1:
        return '明天', wd
    return '後天', wd


def _parse_dt(s):
    try:
        return datetime.fromisoformat(s)
    except (ValueError, TypeError):
        return None


def _avg(values):
    return round(sum(values) / len(values)) if values else None


_DATE_RE = re.compile(r'^(\d{4}/\d{1,2}/\d{1,2}|\d{1,2}/\d{1,2}|\d{1,2}月[初中底])')


def _has_explicit_date(content):
    return bool(_DATE_RE.match(content.strip()))


_TIMING_DAY = {'初': 1, '中': 15, '底': 28}


def _parse_explicit_date(content, today):
    s = content.strip()
    m = re.match(r'^(\d{4})/(\d{1,2})/(\d{1,2})', s)
    if m:
        try:
            return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            return None
    m = re.match(r'^(\d{1,2})/(\d{1,2})', s)
    if m:
        try:
            mo, day = int(m.group(1)), int(m.group(2))
            return date(today.year, mo, day)
        except ValueError:
            return None
    m = re.match(r'^(\d{1,2})月([初中底])', s)
    if m:
        try:
            mo, day = int(m.group(1)), _TIMING_DAY[m.group(2)]
            return date(today.year, mo, day)
        except ValueError:
            return None
    return None


def _age_days(time_str, today):
    try:
        dt = datetime.strptime(time_str, '%Y/%m/%d %H:%M:%S')
        return (today - dt.date()).days
    except Exception:
        return None


def _memo_age_badge(days):
    if days is None or days < 30:
        return ''
    if days >= 365:
        cls, label = 'age-old', '已列待辦超過1年'
    elif days >= 183:
        cls, label = 'age-old', '已列待辦超過半年'
    elif days >= 90:
        cls, label = 'age-warn', '已列待辦超過90天'
    else:
        cls, label = 'age-recent', '已列待辦超過30天'
    return f'<span class="future-item-age {cls}">{label}</span>'


_MEMO_GROUPS = [
    ('expired',    '已過期',  'memo-group-expired'),
    ('soon',       '7天內',   'memo-group-soon'),
    ('future',     '7天後',   'memo-group-future'),
    ('far_future', '一個月後', 'memo-group-far-future'),
    ('other',      '其他項目', 'memo-group-other'),
]


def _build_memo_html(items, important_items, today):
    if not items and not important_items:
        return ''
    # Each entry: (sort_date, content, extra, is_important)
    # extra: badge HTML for regular items, date string for important items
    groups = {key: [] for key, _, _ in _MEMO_GROUPS}

    for item in items:
        content = item.get('content', '')
        if _has_explicit_date(content):
            d = _parse_explicit_date(content, today)
            if d is None:
                groups['other'].append((date.max, content, '', False))
            else:
                days_until = (d - today).days
                if days_until <= 0:
                    groups['expired'].append((d, content, '', False))
                elif days_until <= 7:
                    groups['soon'].append((d, content, '', False))
                elif days_until <= 30:
                    groups['future'].append((d, content, '', False))
                else:
                    groups['far_future'].append((d, content, '', False))
        else:
            badge = _memo_age_badge(_age_days(item.get('modifyTime', ''), today))
            groups['other'].append((date.max, content, badge, False))

    for item in important_items:
        name = item.get('name', '')
        date_str = item.get('date', '')
        if not name or not date_str:
            continue
        try:
            parts = date_str.split('/')
            d = date(int(parts[0]), int(parts[1]), int(parts[2]))
        except (ValueError, IndexError):
            continue
        days_until = (d - today).days
        if days_until < 0:
            continue
        date_label = f'{d.month}/{d.day}'
        if days_until <= 7:
            groups['soon'].append((d, name, date_label, True))
        elif days_until <= 30:
            groups['future'].append((d, name, date_label, True))
        else:
            groups['far_future'].append((d, name, date_label, True))

    for key in groups:
        groups[key].sort(key=lambda x: x[0])

    body = ''
    for key, label, cls in _MEMO_GROUPS:
        if not groups[key]:
            continue
        rows = ''
        for _, c, extra, is_important in groups[key]:
            if is_important:
                rows += (f'<div class="future-item future-item-important">'
                         f'<span class="important-date-badge">{html_lib.escape(extra)}</span>'
                         f'<span class="future-item-content">{html_lib.escape(c)}</span>'
                         f'</div>')
            else:
                rows += (f'<div class="future-item">'
                         f'<span class="future-item-content">{html_lib.escape(c)}</span>'
                         f'{extra}</div>')
        body += (f'<div class="memo-group-label {cls}">{label}</div>'
                 f'<div class="future-list-card">{rows}</div>')

    if not body:
        return ''
    return (f'<div class="section">'
            f'<div class="section-title">待辦事項</div>'
            f'{body}'
            f'</div>')


def _build_purchase_html(items):
    if not items:
        return ''
    rows = ''.join(
        f'<div class="future-item">'
        f'<span class="future-item-content">{html_lib.escape(item.get("name", ""))}</span>'
        f'</div>'
        for item in items
    )
    return (f'<div class="section">'
            f'<div class="section-title">待買清單</div>'
            f'<div class="future-list-card">{rows}</div>'
            f'</div>')


_ALL_SLOT_NAMES = ['早上', '下午', '晚上']


def _day_summary(slots_data):
    """slots_data: list of (slot_name, avg_temp, avg_rain)"""
    very_hot, hot, very_cold, cool, rainy = [], [], [], [], []
    for name, temp, rain in slots_data:
        if temp is not None:
            if temp >= 35:
                very_hot.append(name)
            elif temp >= 30:
                hot.append(name)
            if temp < 10:
                very_cold.append(name)
            elif temp < 20:
                cool.append(name)
        if rain is not None and rain > 50:
            rainy.append(name)

    def fmt(names):
        return '整天' if set(names) == set(_ALL_SLOT_NAMES) else '、'.join(names)

    messages = []
    if very_hot:
        messages.append(f'{fmt(very_hot)}非常熱，建議不要外出')
    if hot:
        messages.append(f'{fmt(hot)}氣溫偏高，注意補水')
    if very_cold:
        messages.append(f'{fmt(very_cold)}非常冷，建議不要外出')
    if cool:
        messages.append(f'{fmt(cool)}偏涼，注意保暖')
    if rainy:
        messages.append(f'{fmt(rainy)}可能會下雨，建議帶傘')

    if not messages:
        return ''
    items = ''.join(f'<div class="weather-summary-item">{m}</div>' for m in messages)
    return f'<div class="weather-summary">{items}</div>'


def generate_html():
    now = datetime.now(TAIWAN_TZ)
    today = now.date()
    target_dates = [today + timedelta(days=i) for i in range(3)]

    try:
        url = (f'https://opendata.cwa.gov.tw/api/v1/rest/datastore/{CWA_DATASET}'
               f'?Authorization={settings.CWA_API_KEY}')
        resp = requests.get(url, timeout=25)
        resp.raise_for_status()
        data = resp.json()

        all_locs = data['records']['Locations'][0]['Location']
        loc = next((l for l in all_locs if l['LocationName'] == CWA_LOCATION), None)
        if not loc:
            return '<div class="wip">找不到地點資料</div>'

        elements = {el['ElementName']: el for el in loc['WeatherElement']}

        # date → {hour: temp}
        temp_dh = defaultdict(dict)
        for slot in elements.get('溫度', {}).get('Time', []):
            dt_str = slot.get('DataTime', '')
            dt = _parse_dt(dt_str)
            if not dt:
                continue
            try:
                temp_dh[dt.date()][dt.hour] = int(slot['ElementValue'][0]['Temperature'])
            except (KeyError, ValueError, IndexError):
                pass

        # date → {start_hour: rain_pct}
        rain_dh = defaultdict(dict)
        for slot in elements.get('3小時降雨機率', {}).get('Time', []):
            dt_str = slot.get('StartTime', '')
            dt = _parse_dt(dt_str)
            if not dt:
                continue
            try:
                rain_dh[dt.date()][dt.hour] = int(slot['ElementValue'][0]['ProbabilityOfPrecipitation'])
            except (KeyError, ValueError, IndexError):
                pass

        cards_html = ''
        for d in target_dates:
            label, weekday = _day_label(d, today)
            date_str = f'{d.month}/{d.day}'
            today_cls = ' weather-card-today' if d == today else ''

            slots_html = ''
            slots_data = []
            for slot_name, slot_time, temp_hours, rain_hours in TIME_SLOTS:
                temps = [temp_dh[d][h] for h in temp_hours if h in temp_dh[d]]
                rains = [rain_dh[d][h] for h in rain_hours if h in rain_dh[d]]
                avg_temp = _avg(temps)
                avg_rain = _avg(rains)
                slots_data.append((slot_name, avg_temp, avg_rain))
                temp_display = f'{avg_temp}°' if avg_temp is not None else '--'
                rain_display = f'{avg_rain}%' if avg_rain is not None else '--'

                slots_html += f'''
        <div class="weather-slot">
          <div class="slot-period">{slot_name}</div>
          <div class="slot-time">{slot_time}</div>
          <div class="slot-temp">{temp_display}</div>
          <div class="slot-rain">💧 {rain_display}</div>
        </div>'''

            summary_html = _day_summary(slots_data)

            cards_html += f'''
    <div class="weather-card{today_cls}">
      <div class="weather-card-header">
        <span class="weather-day-main">{html_lib.escape(label)}</span>
        <span class="weather-day-sub">{weekday} · {date_str}</span>
      </div>
      <div class="weather-slots">{slots_html}
      </div>{summary_html}
    </div>'''

        update_time = now.strftime('%H:%M')
        weather_html = f'''<div class="section">
  <div class="section-title">台中市西屯區 天氣預報</div>
  <div class="weather-list">{cards_html}
  </div>
  <div class="update-time">資料來源：中央氣象署 · 今日 {update_time} 更新</div>
</div>'''
        try:
            r = requests.get(settings.URL_GAS_API,
                             params={'action': 'action_get_dashboard_future'}, timeout=25)
            future_data = json.loads(r.json().get('responseMsg', '{}'))
        except Exception:
            future_data = {}
        extra_html = (_build_memo_html(future_data.get('memo', []), future_data.get('importantSchedule', []), today) +
                      _build_purchase_html(future_data.get('purchase', [])))
        return weather_html + extra_html

    except Exception as e:
        return f'<div class="wip">天氣資料載入失敗：{html_lib.escape(str(e))}</div>'
