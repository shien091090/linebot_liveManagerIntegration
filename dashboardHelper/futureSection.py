import requests
import html as html_lib
from datetime import datetime, timezone, timedelta
from collections import defaultdict
import settings

TAIWAN_TZ = timezone(timedelta(hours=8))
CWA_DATASET = 'F-D0047-073'
CWA_LOCATION = '西屯區'
WEEKDAY_NAMES = ['週一', '週二', '週三', '週四', '週五', '週六', '週日']

_CODE_EMOJI = {1: '☀️', 2: '🌤️', 3: '🌤️', 4: '⛅', 5: '⛅', 6: '☁️', 7: '☁️'}


def _emoji(code):
    try:
        c = int(code)
    except (TypeError, ValueError):
        return '🌡️'
    if c in _CODE_EMOJI:
        return _CODE_EMOJI[c]
    return '🌧️' if c <= 17 else '⛈️'


def _day_label(d, today):
    delta = (d - today).days
    wd = WEEKDAY_NAMES[d.weekday()]
    if delta == 0:
        return '今天', wd
    if delta == 1:
        return '明天', wd
    if delta == 2:
        return '後天', wd
    return f'{d.month}/{d.day}', wd


def _parse_dt(s):
    try:
        return datetime.fromisoformat(s)
    except (ValueError, TypeError):
        return None


def generate_html():
    now = datetime.now(TAIWAN_TZ)
    today = now.date()

    try:
        url = (f'https://opendata.cwa.gov.tw/api/v1/rest/datastore/{CWA_DATASET}'
               f'?Authorization={settings.CWA_API_KEY}')
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        all_locs = data['records']['Locations'][0]['Location']
        loc = next((l for l in all_locs if l['LocationName'] == CWA_LOCATION), None)
        if not loc:
            return '<div class="wip">找不到地點資料</div>'

        elements = {el['ElementName']: el for el in loc['WeatherElement']}

        # Hourly temp: DataTime → temperature int
        temp_by_dt = {}
        for slot in elements.get('溫度', {}).get('Time', []):
            dt_str = slot.get('DataTime', '')
            if dt_str:
                try:
                    temp_by_dt[dt_str] = int(slot['ElementValue'][0]['Temperature'])
                except (KeyError, ValueError, IndexError):
                    pass

        # 3-hour rain probability: StartTime → int
        rain_map = {}
        for slot in elements.get('3小時降雨機率', {}).get('Time', []):
            dt_str = slot.get('StartTime', '')
            if dt_str:
                try:
                    rain_map[dt_str] = int(slot['ElementValue'][0]['ProbabilityOfPrecipitation'])
                except (KeyError, ValueError, IndexError):
                    pass

        # 3-hour weather phenomenon
        slots_3h = []
        for slot in elements.get('天氣現象', {}).get('Time', []):
            dt_str = slot.get('StartTime', '')
            if not dt_str:
                continue
            dt = _parse_dt(dt_str)
            if not dt:
                continue
            try:
                ev = slot['ElementValue'][0]
                slots_3h.append({
                    'dt': dt,
                    'weather': ev.get('Weather', ''),
                    'code': ev.get('WeatherCode', ''),
                    'rain': rain_map.get(dt_str, 0),
                })
            except (KeyError, IndexError):
                pass

        # Aggregate by calendar date
        days = defaultdict(lambda: {'temps': [], 'day_slots': [], 'all_slots': []})
        for dt_str, temp in temp_by_dt.items():
            dt = _parse_dt(dt_str)
            if dt:
                days[dt.date()]['temps'].append(temp)
        for slot in slots_3h:
            d = slot['dt'].date()
            days[d]['all_slots'].append(slot)
            if 6 <= slot['dt'].hour < 21:
                days[d]['day_slots'].append(slot)

        cards_html = ''
        for d in sorted(days.keys()):
            info = days[d]
            temps = info['temps']
            min_t = min(temps) if temps else '--'
            max_t = max(temps) if temps else '--'

            active = info['day_slots'] or info['all_slots']
            max_rain = max((s['rain'] for s in active), default=0)

            if active:
                dominant = max(active,
                               key=lambda s: int(s['code']) if s['code'].isdigit() else 0)
                dominant_weather = dominant['weather']
                dominant_code = dominant['code']
            else:
                dominant_weather, dominant_code = '無資料', '01'

            emoji = _emoji(dominant_code)
            label, weekday = _day_label(d, today)
            rain_display = f'{max_rain}%' if max_rain > 0 else '—'
            today_cls = ' weather-card-today' if d == today else ''

            cards_html += f'''
      <div class="weather-card{today_cls}">
        <div class="weather-day">
          <span class="weather-day-main">{html_lib.escape(label)}</span>
          <span class="weather-day-sub">{weekday}</span>
        </div>
        <div class="weather-icon">{emoji}</div>
        <div class="weather-detail">
          <div class="weather-temp">{min_t}° <span class="temp-sep">/</span> {max_t}°</div>
          <div class="weather-desc">{html_lib.escape(dominant_weather)}</div>
        </div>
        <div class="weather-rain">
          <span class="rain-icon">💧</span>
          <span class="rain-pct">{rain_display}</span>
        </div>
      </div>'''

        update_time = now.strftime('%H:%M')

        return f'''<div class="section">
  <div class="section-title">台中市西屯區 天氣預報</div>
  <div class="weather-list">{cards_html}
  </div>
  <div class="update-time">資料來源：中央氣象署 · 今日 {update_time} 更新</div>
</div>'''

    except Exception as e:
        return f'<div class="wip">天氣資料載入失敗：{html_lib.escape(str(e))}</div>'
