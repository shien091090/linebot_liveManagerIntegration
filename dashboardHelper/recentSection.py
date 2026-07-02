import io
import base64
import json
import requests
from collections import defaultdict
from datetime import datetime, timedelta

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker

import settings

_COLOR_MORNING = "#3B82F6"
_COLOR_EVENING = "#F59E0B"
_COLOR_SLEEP   = "#8B5CF6"
_COLOR_XUAN    = "#EC4899"
_COLOR_BATH    = "#10B981"

_CHART_CSS = """
.chart-subtitle { font-size: 12px; color: #64748B; margin-bottom: 8px; margin-top: 2px; }
.chart-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.07), 0 0 0 1px rgba(0,0,0,0.04);
  padding: 10px 8px 4px;
}
.chart-legend {
  display: flex; flex-wrap: wrap; gap: 10px;
  font-size: 11px; color: #64748B;
  padding: 6px 4px 2px;
}
.chart-legend-item { display: flex; align-items: center; gap: 4px; }
.legend-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
"""

SLEEP_EVENT      = "準備睡覺"
WAKE_EVENT       = "起床"
BATH_EVENT       = "準備洗澡"
MORNING_LEAVE    = "準備出門上班"
MORNING_ARRIVE   = "上班到達公司座位"
EVENING_LEAVE    = "準備下班離開座位"
EVENING_ARRIVE   = "下班到家"
XUAN_SLEEP_START = "璇璇準備入睡"
XUAN_SLEEP_END   = "璇璇睡著"


def _fetch_data():
    resp = requests.get(
        settings.URL_GAS_API,
        params={"action": "action_get_dashboard_status"},
        timeout=30
    )
    data = resp.json()
    status = json.loads(data["responseMsg"])
    return status.get("dailyTimeRecords", [])


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


def _calc_time_points(by_date):
    my_sleep, xuan_sleep, bath = [], [], []
    for date_str in sorted(by_date):
        events = by_date[date_str]
        date   = datetime.strptime(date_str, "%Y/%m/%d")
        dt = _last_event(events, SLEEP_EVENT)
        if dt:
            h = dt.hour + dt.minute / 60
            if h < 4:
                h += 24
            if h >= 18:
                my_sleep.append((date, h))
        dt = _last_event(events, XUAN_SLEEP_END)
        if dt:
            xuan_sleep.append((date, dt.hour + dt.minute / 60))
        dt = _last_event(events, BATH_EVENT)
        if dt:
            bath.append((date, dt.hour + dt.minute / 60))
    return my_sleep, xuan_sleep, bath


def _rolling_avg(data, window=30):
    if len(data) < 2:
        return []
    dates  = [d for d, _ in data]
    values = [v for _, v in data]
    result = []
    for i, d in enumerate(dates):
        w = [values[j] for j in range(len(data)) if 0 <= (d - dates[j]).days <= window]
        if w:
            result.append((d, sum(w) / len(w)))
    return result


def _to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=130, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    buf.seek(0)
    enc = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return enc


def _setup_ax(ax):
    ax.set_facecolor("#F8FAFC")
    ax.grid(True, alpha=0.25, linestyle="--", linewidth=0.7)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color("#CBD5E1")
    ax.spines["bottom"].set_color("#CBD5E1")
    ax.tick_params(colors="#64748B", labelsize=8)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%y/%m"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha="right", fontsize=8)


def _chart_duration(series_list, colors):
    fig, ax = plt.subplots(figsize=(8, 2.6))
    fig.patch.set_facecolor("white")
    _setup_ax(ax)
    all_dates = [d for s in series_list for d, _ in s]
    for data, color in zip(series_list, colors):
        if not data:
            continue
        dates, vals = zip(*data)
        ax.scatter(dates, vals, color=color, alpha=0.2, s=7, zorder=2)
        rolling = _rolling_avg(data)
        if rolling:
            rd, rv = zip(*rolling)
            ax.plot(rd, rv, color=color, linewidth=1.8, zorder=3)
    if all_dates:
        ax.set_xlim(left=min(all_dates))
    fig.tight_layout(pad=0.5)
    return _to_base64(fig)


def _chart_timepoints(series_list, colors):
    fig, ax = plt.subplots(figsize=(8, 2.6))
    fig.patch.set_facecolor("white")
    _setup_ax(ax)
    all_dates = [d for s in series_list for d, _ in s]
    all_vals  = [v for s in series_list for _, v in s]
    for data, color in zip(series_list, colors):
        if not data:
            continue
        dates, vals = zip(*data)
        ax.scatter(dates, vals, color=color, alpha=0.2, s=7, zorder=2)
        rolling = _rolling_avg(data)
        if rolling:
            rd, rv = zip(*rolling)
            ax.plot(rd, rv, color=color, linewidth=1.8, zorder=3)

    def time_fmt(x, _):
        h = int(x) % 24
        m = int(round((x % 1) * 60))
        if m == 60:
            h, m = (h + 1) % 24, 0
        return f"{h:02d}:{m:02d}"

    ax.yaxis.set_major_formatter(ticker.FuncFormatter(time_fmt))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(1))
    if all_dates:
        ax.set_xlim(left=min(all_dates))
    if all_vals:
        ax.set_ylim(min(all_vals) - 0.5, max(all_vals) + 0.5)
    fig.tight_layout(pad=0.5)
    return _to_base64(fig)


def _legend_html(items):
    dots = "".join(
        f'<span class="chart-legend-item">'
        f'<span class="legend-dot" style="background:{color}"></span>{label}</span>'
        for label, color in items
    )
    return f'<div class="chart-legend">{dots}</div>'


def _section_html(title, subtitle, img_b64, legend_items=None):
    legend = _legend_html(legend_items) if legend_items else ""
    return (
        f'<div class="section">'
        f'<div class="section-title">{title}</div>'
        f'<div class="chart-subtitle">{subtitle}</div>'
        f'<div class="chart-card">'
        f'<img src="data:image/png;base64,{img_b64}" style="width:100%;display:block;" loading="lazy"/>'
        f"{legend}"
        f"</div>"
        f"</div>"
    )


def _no_data_html(title, subtitle):
    return (
        f'<div class="section">'
        f'<div class="section-title">{title}</div>'
        f'<div class="chart-subtitle">{subtitle}</div>'
        f'<div class="chart-card" style="text-align:center;padding:24px;'
        f'color:#94A3B8;font-size:13px;">尚無足夠資料</div>'
        f"</div>"
    )


def generate_html():
    try:
        raw = _fetch_data()
    except Exception as e:
        return f'<div class="wip">資料載入失敗：{e}</div>'

    if not raw:
        return '<div class="wip">尚無日常時間紀錄</div>'

    by_date = _parse_records(raw)
    morning, evening           = _calc_commute(by_date)
    my_sleep                   = _calc_my_sleep(by_date)
    xuan_sleep                 = _calc_xuan_sleep(by_date)
    my_sleep_t, xuan_t, bath_t = _calc_time_points(by_date)

    parts = [f"<style>{_CHART_CSS}</style>"]

    if morning or evening:
        img = _chart_duration([morning, evening], [_COLOR_MORNING, _COLOR_EVENING])
        parts.append(_section_html(
            "通勤時間趨勢", "分鐘 · 30天滾動平均", img,
            [("上班通勤", _COLOR_MORNING), ("下班通勤", _COLOR_EVENING)]
        ))
    else:
        parts.append(_no_data_html("通勤時間趨勢", "分鐘"))

    if my_sleep:
        img = _chart_duration([my_sleep], [_COLOR_SLEEP])
        parts.append(_section_html(
            "我的睡眠時長", "小時 · 30天滾動平均", img,
            [("睡眠時長", _COLOR_SLEEP)]
        ))
    else:
        parts.append(_no_data_html("我的睡眠時長", "小時"))

    if xuan_sleep:
        img = _chart_duration([xuan_sleep], [_COLOR_XUAN])
        parts.append(_section_html(
            "璇璇入睡耗時", "分鐘 · 30天滾動平均", img,
            [("入睡耗時", _COLOR_XUAN)]
        ))
    else:
        parts.append(_no_data_html("璇璇入睡耗時", "分鐘"))

    if my_sleep_t or xuan_t or bath_t:
        img = _chart_timepoints(
            [my_sleep_t, xuan_t, bath_t],
            [_COLOR_SLEEP, _COLOR_XUAN, _COLOR_BATH]
        )
        parts.append(_section_html(
            "時間點趨勢", "30天滾動平均", img,
            [("我的入睡", _COLOR_SLEEP), ("璇璇睡著", _COLOR_XUAN), ("洗澡", _COLOR_BATH)]
        ))
    else:
        parts.append(_no_data_html("時間點趨勢", "入睡 / 璇璇睡著 / 洗澡"))

    return "\n".join(parts)
