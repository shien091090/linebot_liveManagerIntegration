import json
import requests
from collections import defaultdict
from datetime import datetime, timedelta

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib.font_manager import FontProperties
import matplotlib.dates as mdates

import settings

_COLOR_MORNING = "#3B82F6"
_COLOR_EVENING = "#F59E0B"
_COLOR_SLEEP   = "#8B5CF6"
_COLOR_XUAN    = "#EC4899"
_COLOR_BATH    = "#10B981"
_COLOR_BUSY    = "#EF4444"

_FONT_PATH = "fonts/Cubic_11_1.010_R.ttf"
_FONT_PROP = FontProperties(fname=_FONT_PATH)

SLEEP_EVENT      = "準備睡覺"
WAKE_EVENT       = "起床"
BATH_EVENT       = "準備洗澡"
MORNING_LEAVE    = "準備出門上班"
MORNING_ARRIVE   = "上班到達公司座位"
EVENING_LEAVE    = "準備下班離開座位"
EVENING_ARRIVE   = "下班到家"
XUAN_SLEEP_START = "璇璇準備入睡"
XUAN_SLEEP_END   = "璇璇睡著"

CHART_NAMES = ['通勤', '睡覺', '璇璇睡覺', '時間點', '忙碌']


def _fetch_data():
    resp = requests.get(
        settings.URL_GAS_API,
        params={"action": "action_get_dashboard_status"},
        timeout=30
    )
    data = resp.json()
    return json.loads(data["responseMsg"])


def _parse_records(raw_records):
    by_date = defaultdict(list)
    for r in raw_records:
        date_str   = r.get("date", "").strip()
        time_str   = r.get("time", "").strip()
        event_type = r.get("eventType", "").strip()
        if not (date_str and time_str and event_type):
            continue
        try:
            dt = datetime.strptime(f"{date_str} {time_str}", "%Y/%m/%d %H:%M:%S")
            by_date[date_str].append({"dt": dt, "eventType": event_type})
        except ValueError:
            continue
    for d in by_date:
        by_date[d].sort(key=lambda x: x["dt"])
    return by_date


def _first_event(events, event_type):
    for e in events:
        if e["eventType"] == event_type:
            return e["dt"]
    return None


def _last_event(events, event_type):
    result = None
    for e in events:
        if e["eventType"] == event_type:
            result = e["dt"]
    return result


def _calc_commute(by_date):
    morning, evening = [], []
    for date_str in sorted(by_date):
        events = by_date[date_str]
        date   = datetime.strptime(date_str, "%Y/%m/%d")
        leave  = _first_event(events, MORNING_LEAVE)
        arrive = _first_event(events, MORNING_ARRIVE)
        if leave and arrive:
            diff = (arrive - leave).total_seconds() / 60
            if 5 <= diff <= 180:
                morning.append((date, diff))
        leave2  = _first_event(events, EVENING_LEAVE)
        arrive2 = _first_event(events, EVENING_ARRIVE)
        if leave2 and arrive2:
            diff = (arrive2 - leave2).total_seconds() / 60
            if 5 <= diff <= 180:
                evening.append((date, diff))
    return morning, evening


def _calc_my_sleep(by_date):
    results = []
    for date_str in sorted(by_date):
        events   = by_date[date_str]
        sleep_dt = _last_event(events, SLEEP_EVENT)
        if not sleep_dt:
            continue
        hour = sleep_dt.hour
        if 18 <= hour <= 23:
            wake_date_str = (datetime.strptime(date_str, "%Y/%m/%d") + timedelta(days=1)).strftime("%Y/%m/%d")
            plot_date = datetime.strptime(date_str, "%Y/%m/%d")
        elif 0 <= hour < 4:
            wake_date_str = date_str
            plot_date = datetime.strptime(date_str, "%Y/%m/%d") - timedelta(days=1)
        else:
            continue
        if wake_date_str not in by_date:
            continue
        wake_events = [e for e in by_date[wake_date_str]
                       if e["eventType"] == WAKE_EVENT and 4 <= e["dt"].hour < 12]
        if not wake_events:
            continue
        wake_dt  = wake_events[-1]["dt"]
        diff_min = (wake_dt - sleep_dt).total_seconds() / 60
        if 180 <= diff_min <= 720:
            results.append((plot_date, diff_min / 60))
    return results


def _calc_xuan_sleep(by_date):
    results = []
    for date_str in sorted(by_date):
        events = by_date[date_str]
        start  = _first_event(events, XUAN_SLEEP_START)
        end    = _first_event(events, XUAN_SLEEP_END)
        if start and end:
            diff = (end - start).total_seconds() / 60
            if 1 <= diff <= 120:
                results.append((datetime.strptime(date_str, "%Y/%m/%d"), diff))
    return results


def _wrap_late_night_hour(dt):
    h = dt.hour + dt.minute / 60
    if h < 4:
        h += 24
    return h


def _calc_time_points(by_date):
    my_sleep, xuan_sleep, bath = [], [], []
    for date_str in sorted(by_date):
        events = by_date[date_str]
        date   = datetime.strptime(date_str, "%Y/%m/%d")
        dt = _last_event(events, SLEEP_EVENT)
        if dt:
            h = _wrap_late_night_hour(dt)
            if h >= 18:
                my_sleep.append((date, h))
        dt = _last_event(events, XUAN_SLEEP_END)
        if dt:
            xuan_sleep.append((date, _wrap_late_night_hour(dt)))
        dt = _last_event(events, BATH_EVENT)
        if dt:
            bath.append((date, _wrap_late_night_hour(dt)))
    return my_sleep, xuan_sleep, bath


def _parse_memo_history(raw_history):
    blocks = []
    current_block = []
    for r in raw_history:
        content = str(r.get("content", "")).strip()
        modify_time_str = str(r.get("modifyTime", "")).strip()
        total_count = r.get("totalCount")
        if not content or not modify_time_str or total_count in ("", None):
            continue
        try:
            number = int(r.get("number"))
            total_count = int(total_count)
            modify_time = datetime.strptime(modify_time_str, "%Y/%m/%d %H:%M:%S")
        except (ValueError, TypeError):
            continue
        row = {"number": number, "modifyTime": modify_time, "totalCount": total_count}
        if number == 1 and current_block:
            blocks.append(current_block)
            current_block = []
        current_block.append(row)
    if current_block:
        blocks.append(current_block)
    return blocks


def _calc_busy_score(blocks):
    daily_counts = defaultdict(int)
    if len(blocks) < 2:
        return daily_counts

    prev_size = len(blocks[0])
    pending_removals = 0
    for block in blocks[1:]:
        size = len(block)
        if size > prev_size:
            add_date = max(row["modifyTime"] for row in block).date()
            daily_counts[add_date] += (size - prev_size)
            if pending_removals:
                daily_counts[add_date] += pending_removals
                pending_removals = 0
        elif size < prev_size:
            pending_removals += (prev_size - size)
        prev_size = size

    if pending_removals:
        last_known_date = max(row["modifyTime"] for row in blocks[-1]).date()
        daily_counts[last_known_date] += pending_removals

    return daily_counts


def _densify_daily_counts(daily_counts):
    if not daily_counts:
        return []
    dates = sorted(daily_counts)
    start, end = dates[0], dates[-1]
    result = []
    d = start
    while d <= end:
        result.append((datetime(d.year, d.month, d.day), daily_counts.get(d, 0)))
        d += timedelta(days=1)
    return result


def _rolling_avg(data, window=30, warmup=0):
    if len(data) < 2:
        return []
    dates  = [d for d, _ in data]
    values = [v for _, v in data]
    first_date = dates[0]
    result = []
    for i, d in enumerate(dates):
        if (d - first_date).days < warmup:
            continue
        w = [values[j] for j in range(len(data)) if 0 <= (d - dates[j]).days <= window]
        if w:
            result.append((d, sum(w) / len(w)))
    return result


def _fmt_hour_label(h):
    h = h % 24
    hh = int(h)
    mm = int(round((h - hh) * 60))
    if mm == 60:
        hh = (hh + 1) % 24
        mm = 0
    return f'{hh:02d}:{mm:02d}'


def _new_axes():
    fig, ax = plt.subplots(figsize=(10, 6), dpi=120)
    return fig, ax


def _plot_series(ax, data, color, label):
    dates = [d for d, _ in data]
    values = [v for _, v in data]
    ax.plot(dates, values, marker='o', markersize=4, color=color, label=label)


def _finalize_and_save(fig, ax, title, ylabel, file_name):
    ax.set_title(title, fontproperties=_FONT_PROP, fontsize=18)
    ax.set_ylabel(ylabel, fontproperties=_FONT_PROP, fontsize=12)
    ax.legend(prop=_FONT_PROP)
    ax.grid(True, linestyle='--', alpha=0.4)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(file_name)
    plt.close(fig)


def generate_chart_image(chart_name):
    """回傳 (file_name, error_message)，成功時 error_message 為 None"""
    try:
        status = _fetch_data()
    except Exception as e:
        return None, f'資料載入失敗：{e}'

    raw          = status.get("dailyTimeRecords", [])
    memo_history = status.get("memoHistory", [])
    by_date = _parse_records(raw)

    file_name = 'recent_status_chart.jpg'

    if chart_name == '通勤':
        morning, evening = _calc_commute(by_date)
        if not morning and not evening:
            return None, '尚無足夠資料'
        fig, ax = _new_axes()
        if morning:
            _plot_series(ax, morning, _COLOR_MORNING, '上班通勤')
        if evening:
            _plot_series(ax, evening, _COLOR_EVENING, '下班通勤')
        _finalize_and_save(fig, ax, '上下班耗時', '分鐘', file_name)
        return file_name, None

    if chart_name == '睡覺':
        my_sleep = _calc_my_sleep(by_date)
        if not my_sleep:
            return None, '尚無足夠資料'
        fig, ax = _new_axes()
        _plot_series(ax, my_sleep, _COLOR_SLEEP, '睡眠時長')
        _finalize_and_save(fig, ax, '我的睡眠時長', '小時', file_name)
        return file_name, None

    if chart_name == '璇璇睡覺':
        xuan_sleep = _calc_xuan_sleep(by_date)
        if not xuan_sleep:
            return None, '尚無足夠資料'
        fig, ax = _new_axes()
        _plot_series(ax, xuan_sleep, _COLOR_XUAN, '入睡耗時')
        _finalize_and_save(fig, ax, '璇璇入睡耗時', '分鐘', file_name)
        return file_name, None

    if chart_name == '時間點':
        my_sleep_t, xuan_t, bath_t = _calc_time_points(by_date)
        if not my_sleep_t and not xuan_t and not bath_t:
            return None, '尚無足夠資料'
        fig, ax = _new_axes()
        if my_sleep_t:
            _plot_series(ax, my_sleep_t, _COLOR_SLEEP, '我的入睡')
        if xuan_t:
            _plot_series(ax, xuan_t, _COLOR_XUAN, '璇璇睡著')
        if bath_t:
            _plot_series(ax, bath_t, _COLOR_BATH, '洗澡')
        ax.set_ylim(21, 27)
        ax.set_yticks(range(21, 28))
        ax.set_yticklabels([_fmt_hour_label(h) for h in range(21, 28)])
        _finalize_and_save(fig, ax, '時間點趨勢', '時間', file_name)
        return file_name, None

    if chart_name == '忙碌':
        memo_blocks = _parse_memo_history(memo_history)
        busy_daily  = _calc_busy_score(memo_blocks)
        busy_series = _densify_daily_counts(busy_daily)
        if not busy_series:
            return None, '尚無足夠資料'
        avg = _rolling_avg(busy_series, warmup=30)
        if not avg:
            return None, '尚無足夠資料（累積天數未滿30天）'
        fig, ax = _new_axes()
        raw_dates = [d for d, _ in busy_series]
        raw_values = [v for _, v in busy_series]
        ax.scatter(raw_dates, raw_values, color=_COLOR_BUSY, alpha=0.25, s=12)
        avg_dates = [d for d, _ in avg]
        avg_values = [v for _, v in avg]
        ax.plot(avg_dates, avg_values, color=_COLOR_BUSY, label='忙碌指數（30天滾動平均）')
        _finalize_and_save(fig, ax, '忙碌程度', '件', file_name)
        return file_name, None

    return None, f'未知的圖表名稱：{chart_name}'
