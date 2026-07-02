import json
import requests
from collections import defaultdict
from datetime import datetime, timedelta

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
.linechart { position: relative; }
.linechart svg { width: 100%; height: auto; display: block; touch-action: pan-y; }
.chart-tooltip {
  display: none; position: absolute;
  background: #1E293B; color: #F1F5F9;
  border-radius: 8px; padding: 8px 10px;
  font-size: 11px; line-height: 1.6;
  pointer-events: none; white-space: nowrap;
  box-shadow: 0 4px 16px rgba(0,0,0,0.25);
  z-index: 50;
}
.chart-tooltip .tooltip-date { font-weight: 700; margin-bottom: 2px; color: #fff; }
.chart-tooltip .tooltip-line { display: flex; align-items: center; gap: 5px; }
.chart-tooltip .tooltip-dot { width: 7px; height: 7px; border-radius: 50%; display: inline-block; flex-shrink: 0; }
"""

_CHART_JS = """
function renderLineChart(containerId, config) {
  var container = document.getElementById(containerId);
  if (!container || !config || !config.series || !config.series.length) return;

  var width = 800, height = 260;
  var padL = 42, padR = 12, padT = 10, padB = 24;
  var plotW = width - padL - padR;
  var plotH = height - padT - padB;

  function parseDay(s) {
    var p = s.split('-');
    return Date.UTC(+p[0], +p[1] - 1, +p[2]) / 86400000;
  }

  var allDays = [], allVals = [];
  config.series.forEach(function(s) {
    s.avg.forEach(function(pt) { allDays.push(parseDay(pt[0])); allVals.push(pt[1]); });
    s.raw.forEach(function(pt) { allDays.push(parseDay(pt[0])); allVals.push(pt[1]); });
  });
  if (!allDays.length) return;

  var minDay = Math.min.apply(null, allDays);
  var maxDay = Math.max.apply(null, allDays);
  if (minDay === maxDay) maxDay = minDay + 1;

  var minVal = Math.min.apply(null, allVals);
  var maxVal = Math.max.apply(null, allVals);
  var vPad = (maxVal - minVal) * 0.15 || 1;
  minVal -= vPad; maxVal += vPad;

  function xPix(day) { return padL + (day - minDay) / (maxDay - minDay) * plotW; }
  function yPix(val) { return padT + (1 - (val - minVal) / (maxVal - minVal)) * plotH; }

  function pad2(n) { return n < 10 ? '0' + n : '' + n; }

  function fmtTime(v) {
    var h = Math.floor(v), m = Math.round((v - h) * 60);
    if (m === 60) { h += 1; m = 0; }
    return pad2(h) + ':' + pad2(m);
  }

  function fmtVal(v) {
    if (config.unit === 'minutes') return Math.round(v) + ' 分';
    if (config.unit === 'hours') return v.toFixed(1) + ' 小時';
    return fmtTime(v);
  }

  function fmtAxisVal(v) {
    if (config.unit === 'minutes') return Math.round(v);
    if (config.unit === 'hours') return Math.round(v * 10) / 10;
    return fmtTime(v);
  }

  function fmtAxisDate(day) {
    var d = new Date(day * 86400000);
    return pad2(d.getUTCMonth() + 1) + '/' + pad2(d.getUTCDate());
  }

  function fmtFullDate(day) {
    var d = new Date(day * 86400000);
    return d.getUTCFullYear() + '/' + fmtAxisDate(day);
  }

  var yTickCount = 5;
  var yTicks = [];
  for (var i = 0; i <= yTickCount; i++) {
    yTicks.push(minVal + (maxVal - minVal) * i / yTickCount);
  }
  var xTickCount = Math.max(2, Math.min(5, Math.round((maxDay - minDay) / 5)));
  var xTicks = [];
  for (var j = 0; j <= xTickCount; j++) {
    xTicks.push(minDay + (maxDay - minDay) * j / xTickCount);
  }

  var svgParts = [];
  svgParts.push('<svg viewBox="0 0 ' + width + ' ' + height + '">');

  yTicks.forEach(function(v) {
    var y = yPix(v);
    svgParts.push('<line x1="' + padL + '" y1="' + y + '" x2="' + (width - padR) + '" y2="' + y + '" stroke="#E2E8F0" stroke-dasharray="3,3" stroke-width="1"/>');
    svgParts.push('<text x="' + (padL - 6) + '" y="' + (y + 3) + '" text-anchor="end" font-size="9" fill="#64748B">' + fmtAxisVal(v) + '</text>');
  });
  xTicks.forEach(function(day) {
    var x = xPix(day);
    svgParts.push('<text x="' + x + '" y="' + (height - 7) + '" text-anchor="middle" font-size="9" fill="#64748B">' + fmtAxisDate(day) + '</text>');
  });

  config.series.forEach(function(s) {
    s.raw.forEach(function(pt) {
      var x = xPix(parseDay(pt[0])), y = yPix(pt[1]);
      svgParts.push('<circle cx="' + x + '" cy="' + y + '" r="2.6" fill="' + s.color + '" fill-opacity="0.25"/>');
    });
    if (s.avg.length) {
      var pts = s.avg.map(function(pt) { return xPix(parseDay(pt[0])) + ',' + yPix(pt[1]); }).join(' ');
      svgParts.push('<polyline points="' + pts + '" fill="none" stroke="' + s.color + '" stroke-width="1.8" stroke-linejoin="round" stroke-linecap="round"/>');
    }
  });

  svgParts.push('<line id="' + containerId + '-guide" x1="0" y1="' + padT + '" x2="0" y2="' + (height - padB) + '" stroke="#94A3B8" stroke-width="1" style="display:none"/>');
  config.series.forEach(function(s, idx) {
    svgParts.push('<circle id="' + containerId + '-dot-' + idx + '" r="3.4" fill="' + s.color + '" stroke="#fff" stroke-width="1.2" style="display:none"/>');
  });
  svgParts.push('<rect id="' + containerId + '-overlay" x="' + padL + '" y="0" width="' + plotW + '" height="' + height + '" fill="transparent"/>');
  svgParts.push('</svg>');
  svgParts.push('<div class="chart-tooltip" id="' + containerId + '-tooltip"></div>');

  container.innerHTML = svgParts.join('');

  var svgEl = container.querySelector('svg');
  var overlay = document.getElementById(containerId + '-overlay');
  var tooltip = document.getElementById(containerId + '-tooltip');
  var guide = document.getElementById(containerId + '-guide');

  var dayMap = {};
  config.series.forEach(function(s) {
    s.avg.forEach(function(pt) { dayMap[parseDay(pt[0])] = true; });
  });
  var masterDays = Object.keys(dayMap).map(Number).sort(function(a, b) { return a - b; });

  function nearestDay(day) {
    var lo = 0, hi = masterDays.length - 1;
    if (day <= masterDays[0]) return masterDays[0];
    if (day >= masterDays[hi]) return masterDays[hi];
    while (hi - lo > 1) {
      var mid = (lo + hi) >> 1;
      if (masterDays[mid] < day) lo = mid; else hi = mid;
    }
    return (day - masterDays[lo] <= masterDays[hi] - day) ? masterDays[lo] : masterDays[hi];
  }

  function showAt(clientX) {
    var rect = svgEl.getBoundingClientRect();
    if (!rect.width) return;
    var scale = width / rect.width;
    var px = (clientX - rect.left) * scale;
    var day = nearestDay(minDay + (px - padL) / plotW * (maxDay - minDay));
    var x = xPix(day);

    guide.setAttribute('x1', x); guide.setAttribute('x2', x);
    guide.style.display = 'block';

    var rows = [];
    config.series.forEach(function(s, idx) {
      var dot = document.getElementById(containerId + '-dot-' + idx);
      var match = null;
      for (var k = 0; k < s.avg.length; k++) {
        if (parseDay(s.avg[k][0]) === day) { match = s.avg[k]; break; }
      }
      if (match) {
        dot.setAttribute('cx', x);
        dot.setAttribute('cy', yPix(match[1]));
        dot.style.display = 'block';
        rows.push('<div class="tooltip-line"><span class="tooltip-dot" style="background:' + s.color + '"></span>' + s.label + '：' + fmtVal(match[1]) + '</div>');
      } else {
        dot.style.display = 'none';
      }
    });

    if (!rows.length) { hide(); return; }

    tooltip.innerHTML = '<div class="tooltip-date">' + fmtFullDate(day) + '</div>' + rows.join('');
    tooltip.style.display = 'block';

    var left = (x / width) * rect.width;
    var maxLeft = rect.width - tooltip.offsetWidth - 4;
    tooltip.style.left = Math.max(4, Math.min(left + 8, maxLeft)) + 'px';
    tooltip.style.top = '4px';
  }

  function hide() {
    guide.style.display = 'none';
    config.series.forEach(function(s, idx) {
      document.getElementById(containerId + '-dot-' + idx).style.display = 'none';
    });
    tooltip.style.display = 'none';
  }

  overlay.addEventListener('mousemove', function(e) { showAt(e.clientX); });
  overlay.addEventListener('mouseleave', hide);
  overlay.addEventListener('touchstart', function(e) { showAt(e.touches[0].clientX); }, { passive: true });
  overlay.addEventListener('touchmove', function(e) { showAt(e.touches[0].clientX); }, { passive: true });
  overlay.addEventListener('touchend', hide);
}
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


def _build_chart_config(series_list, names, colors, unit):
    series = []
    for data, name, color in zip(series_list, names, colors):
        if not data:
            continue
        rolling = _rolling_avg(data)
        series.append({
            "label": name,
            "color": color,
            "raw": [[d.strftime("%Y-%m-%d"), round(v, 2)] for d, v in data],
            "avg": [[d.strftime("%Y-%m-%d"), round(v, 2)] for d, v in rolling],
        })
    return {"unit": unit, "series": series}


def _legend_html(items):
    dots = "".join(
        f'<span class="chart-legend-item">'
        f'<span class="legend-dot" style="background:{color}"></span>{label}</span>'
        for label, color in items
    )
    return f'<div class="chart-legend">{dots}</div>'


def _interactive_chart_html(chart_id, title, subtitle, config, legend_items):
    legend = _legend_html(legend_items)
    config_json = json.dumps(config, ensure_ascii=False)
    return (
        f'<div class="section">'
        f'<div class="section-title">{title}</div>'
        f'<div class="chart-subtitle">{subtitle}</div>'
        f'<div class="chart-card">'
        f'<div class="linechart" id="{chart_id}"></div>'
        f"{legend}"
        f"</div>"
        f"</div>"
        f'<script>renderLineChart("{chart_id}", {config_json});</script>'
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

    parts = [f"<style>{_CHART_CSS}</style>", f"<script>{_CHART_JS}</script>"]

    if morning or evening:
        config = _build_chart_config(
            [morning, evening], ["上班通勤", "下班通勤"], [_COLOR_MORNING, _COLOR_EVENING], "minutes"
        )
        parts.append(_interactive_chart_html(
            "chart-commute", "通勤時間趨勢", "分鐘 · 30天滾動平均", config,
            [("上班通勤", _COLOR_MORNING), ("下班通勤", _COLOR_EVENING)]
        ))
    else:
        parts.append(_no_data_html("通勤時間趨勢", "分鐘"))

    if my_sleep:
        config = _build_chart_config([my_sleep], ["睡眠時長"], [_COLOR_SLEEP], "hours")
        parts.append(_interactive_chart_html(
            "chart-mysleep", "我的睡眠時長", "小時 · 30天滾動平均", config,
            [("睡眠時長", _COLOR_SLEEP)]
        ))
    else:
        parts.append(_no_data_html("我的睡眠時長", "小時"))

    if xuan_sleep:
        config = _build_chart_config([xuan_sleep], ["入睡耗時"], [_COLOR_XUAN], "minutes")
        parts.append(_interactive_chart_html(
            "chart-xuansleep", "璇璇入睡耗時", "分鐘 · 30天滾動平均", config,
            [("入睡耗時", _COLOR_XUAN)]
        ))
    else:
        parts.append(_no_data_html("璇璇入睡耗時", "分鐘"))

    if my_sleep_t or xuan_t or bath_t:
        config = _build_chart_config(
            [my_sleep_t, xuan_t, bath_t], ["我的入睡", "璇璇睡著", "洗澡"],
            [_COLOR_SLEEP, _COLOR_XUAN, _COLOR_BATH], "time"
        )
        parts.append(_interactive_chart_html(
            "chart-timepoints", "時間點趨勢", "30天滾動平均", config,
            [("我的入睡", _COLOR_SLEEP), ("璇璇睡著", _COLOR_XUAN), ("洗澡", _COLOR_BATH)]
        ))
    else:
        parts.append(_no_data_html("時間點趨勢", "入睡 / 璇璇睡著 / 洗澡"))

    return "\n".join(parts)
