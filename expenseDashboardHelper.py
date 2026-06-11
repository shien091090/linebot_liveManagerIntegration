import requests
import csv
import io
import re
import json
import urllib.parse

_SHEET_ID = '1vDFl5qpQb_oTj0xZt1PRw-39yvfbvsYZx04BN10ZQHQ'
_SHEET_NAME = '花費統計'

_PALETTE = [
    '#e57373', '#f06292', '#ba68c8', '#7986cb', '#64b5f6',
    '#4dd0e1', '#4db6ac', '#81c784', '#aed581', '#dce775',
    '#ffd54f', '#ffb74d', '#ff8a65', '#a1887f', '#90a4ae',
    '#b0bec5', '#ef5350', '#ec407a', '#ab47bc', '#5c6bc0',
    '#26a69a', '#66bb6a',
]


def fetch_expense_data(start_year=2026, start_month=1):
    url = (
        f'https://docs.google.com/spreadsheets/d/{_SHEET_ID}'
        f'/gviz/tq?tqx=out:csv&sheet={urllib.parse.quote(_SHEET_NAME)}'
    )
    r = requests.get(url, allow_redirects=True, timeout=15)
    r.encoding = 'utf-8'

    reader = csv.reader(io.StringIO(r.text))
    rows = list(reader)
    if not rows or rows[0][0].strip() != '預算種類':
        return [], {}

    header = rows[0]
    col_map = []
    for i, h in enumerate(header):
        m = re.match(r'(\d{4})/(\d+)月', h.strip())
        if m:
            y, mo = int(m.group(1)), int(m.group(2))
            if y > start_year or (y == start_year and mo >= start_month):
                col_map.append((i, h.strip()))

    cats = {}
    for row in rows[1:]:
        if not row:
            continue
        name = row[0].strip()
        if name in ('', 'Total'):
            continue
        vals = []
        for ci, _ in col_map:
            s = row[ci].strip().replace(',', '') if ci < len(row) else '0'
            try:
                vals.append(int(s))
            except ValueError:
                vals.append(0)
        if any(v > 0 for v in vals):
            cats[name] = vals

    if not cats:
        return [], {}

    n_cols = len(col_map)
    valid_idx = [i for i in range(n_cols) if any(cats[c][i] > 0 for c in cats)]
    months = [col_map[i][1] for i in valid_idx]
    cats = {n: [v[i] for i in valid_idx] for n, v in cats.items()}
    cats = {n: v for n, v in cats.items() if any(x > 0 for x in v)}
    cats = dict(sorted(cats.items(), key=lambda x: -sum(x[1])))
    return months, cats


def generate_expense_dashboard_html(months, cats):
    if not months or not cats:
        return '<html><body><p>No data available.</p></body></html>'

    n_months = len(months)
    cat_names = list(cats.keys())
    monthly_totals = [sum(cats[c][i] for c in cat_names) for i in range(n_months)]
    avg_monthly = sum(monthly_totals) / n_months
    cat_avgs = {n: sum(v) / n_months for n, v in cats.items()}

    max_idx = monthly_totals.index(max(monthly_totals))
    max_cat = cat_names[0]

    bar_datasets = [
        {
            'label': n,
            'data': cats[n],
            'backgroundColor': _PALETTE[i % len(_PALETTE)],
            'borderWidth': 0,
        }
        for i, n in enumerate(cat_names)
    ]
    donut_totals = [sum(cats[n]) for n in cat_names]
    donut_colors = [_PALETTE[i % len(_PALETTE)] for i in range(len(cat_names))]

    def _cell_style(val, avg):
        if val == 0:
            return 'background:#f0f0f0;color:#ccc'
        if avg == 0:
            return 'background:#fff;color:#333'
        r = val / avg
        if r <= 1.0:
            return 'background:#f0f7ff;color:#555'
        elif r <= 1.5:
            return 'background:#fff9c4;color:#555'
        elif r <= 2.5:
            return 'background:#ffcc80;color:#444'
        else:
            return 'background:#ef9a9a;color:#b71c1c'

    heatmap_rows = ''
    for name in cat_names:
        avg = cat_avgs[name]
        cells = f'<td class="cn">{name}</td>'
        for v in cats[name]:
            style = _cell_style(v, avg)
            txt = f'{v:,}' if v > 0 else '—'
            cells += f'<td style="{style}">{txt}</td>'
        cells += f'<td class="ac">{avg:,.0f}</td>'
        heatmap_rows += f'<tr>{cells}</tr>\n'

    month_ths = ''.join(f'<th>{m}</th>' for m in months)

    html = (
        '<!DOCTYPE html>\n'
        '<html lang="zh-TW">\n'
        '<head>\n'
        '<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '<title>家庭花費統計</title>\n'
        '<style>\n'
        '* { box-sizing: border-box; margin: 0; padding: 0; }\n'
        'body { font-family: -apple-system, "Noto Sans TC", sans-serif; background: #f5f7fa; color: #333; }\n'
        '.wrap { max-width: 1100px; margin: 0 auto; padding: 20px; }\n'
        'h1 { color: #587cbe; font-size: 22px; margin-bottom: 4px; }\n'
        '.sub { color: #aaa; font-size: 13px; margin-bottom: 22px; }\n'
        '.cards { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 22px; }\n'
        '.card { background: #fff; border-radius: 10px; padding: 14px 18px; flex: 1; min-width: 140px; box-shadow: 0 1px 5px rgba(0,0,0,.09); }\n'
        '.cl { font-size: 11px; color: #aaa; margin-bottom: 5px; }\n'
        '.cv { font-size: 20px; font-weight: 700; color: #587cbe; }\n'
        '.cs { font-size: 11px; color: #bbb; margin-top: 3px; }\n'
        '.panel { background: #fff; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 1px 5px rgba(0,0,0,.09); }\n'
        '.panel h2 { font-size: 13px; color: #777; margin-bottom: 14px; padding-left: 9px; border-left: 3px solid #587cbe; }\n'
        '.row2 { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; }\n'
        '@media(max-width:700px) { .row2 { grid-template-columns: 1fr; } }\n'
        '.hw { overflow-x: auto; }\n'
        'table.hm { width: 100%; border-collapse: collapse; font-size: 13px; }\n'
        'table.hm th { background: #f0f4ff; color: #587cbe; padding: 7px 10px; text-align: center; white-space: nowrap; font-size: 12px; }\n'
        'table.hm td { padding: 6px 10px; text-align: right; border-bottom: 1px solid #f5f5f5; white-space: nowrap; }\n'
        'table.hm td.cn { text-align: left; color: #444; font-weight: 500; min-width: 120px; }\n'
        'table.hm td.ac { background: #f0f4ff !important; color: #587cbe; font-weight: 600; }\n'
        '.leg { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 12px; font-size: 12px; color: #666; }\n'
        '.li { display: flex; align-items: center; gap: 4px; }\n'
        '.ld { width: 13px; height: 13px; border-radius: 3px; }\n'
        '</style>\n'
        '<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>\n'
        '</head>\n'
        '<body>\n'
        '<div class="wrap">\n'
        '  <h1>家庭花費統計</h1>\n'
        '  <p class="sub">__SUBTITLE__</p>\n'
        '  <div class="cards">\n'
        '    <div class="card"><div class="cl">月均總支出</div><div class="cv">__AVG__</div><div class="cs">__NM__ 個月</div></div>\n'
        '    <div class="card"><div class="cl">最高支出月</div><div class="cv" style="font-size:17px">__MAX_M__</div><div class="cs">__MAX_MT__</div></div>\n'
        '    <div class="card"><div class="cl">最大支出類別</div><div class="cv" style="font-size:15px">__MAX_C__</div><div class="cs">__MAX_CT__</div></div>\n'
        '  </div>\n'
        '  <div class="row2">\n'
        '    <div class="panel"><h2>每月花費走勢（堆疊）</h2><canvas id="bc"></canvas></div>\n'
        '    <div class="panel"><h2>類別佔比（全期間）</h2><canvas id="dc"></canvas></div>\n'
        '  </div>\n'
        '  <div class="panel">\n'
        '    <h2>各類別超支熱圖</h2>\n'
        '    <div class="leg">\n'
        '      <span class="li"><span class="ld" style="background:#f0f0f0;border:1px solid #ddd"></span>無支出</span>\n'
        '      <span class="li"><span class="ld" style="background:#f0f7ff"></span>低於平均</span>\n'
        '      <span class="li"><span class="ld" style="background:#fff9c4"></span>超出平均</span>\n'
        '      <span class="li"><span class="ld" style="background:#ffcc80"></span>超出 1.5×</span>\n'
        '      <span class="li"><span class="ld" style="background:#ef9a9a"></span>超出 2.5×</span>\n'
        '    </div>\n'
        '    <div class="hw"><table class="hm"><thead><tr><th>類別</th>__MONTH_THS__<th>月均</th></tr></thead>'
        '<tbody>__HEATMAP_ROWS__</tbody></table></div>\n'
        '  </div>\n'
        '</div>\n'
        '<script>\n'
        'new Chart(document.getElementById("bc"), {\n'
        '  type: "bar",\n'
        '  data: { labels: __BAR_LABELS__, datasets: __BAR_DATASETS__ },\n'
        '  options: {\n'
        '    responsive: true,\n'
        '    plugins: {\n'
        '      legend: { position: "right", labels: { font: { size: 10 }, boxWidth: 12, padding: 6 } },\n'
        '      tooltip: { callbacks: { label: c => c.dataset.label + ": NT$" + c.raw.toLocaleString() } }\n'
        '    },\n'
        '    scales: {\n'
        '      x: { stacked: true, ticks: { font: { size: 11 } } },\n'
        '      y: { stacked: true, ticks: { font: { size: 11 }, callback: v => "NT$" + v.toLocaleString() } }\n'
        '    }\n'
        '  }\n'
        '});\n'
        'new Chart(document.getElementById("dc"), {\n'
        '  type: "doughnut",\n'
        '  data: { labels: __DONUT_LABELS__, datasets: [{ data: __DONUT_DATA__, backgroundColor: __DONUT_COLORS__, borderWidth: 1 }] },\n'
        '  options: {\n'
        '    responsive: true,\n'
        '    plugins: {\n'
        '      legend: { position: "bottom", labels: { font: { size: 10 }, boxWidth: 12, padding: 5 } },\n'
        '      tooltip: { callbacks: { label: c => c.label + ": NT$" + c.raw.toLocaleString() +\n'
        '        " (" + (c.raw / c.dataset.data.reduce((a,b)=>a+b,0) * 100).toFixed(1) + "%)" } }\n'
        '    }\n'
        '  }\n'
        '});\n'
        '</script>\n'
        '</body>\n'
        '</html>'
    )

    html = html.replace('__SUBTITLE__', f'{months[0]} ～ {months[-1]}')
    html = html.replace('__AVG__', f'NT${avg_monthly:,.0f}')
    html = html.replace('__NM__', str(n_months))
    html = html.replace('__MAX_M__', months[max_idx])
    html = html.replace('__MAX_MT__', f'NT${monthly_totals[max_idx]:,}')
    html = html.replace('__MAX_C__', max_cat)
    html = html.replace('__MAX_CT__', f'NT${sum(cats[max_cat]):,}')
    html = html.replace('__MONTH_THS__', month_ths)
    html = html.replace('__HEATMAP_ROWS__', heatmap_rows)
    html = html.replace('__BAR_LABELS__', json.dumps(months))
    html = html.replace('__BAR_DATASETS__', json.dumps(bar_datasets))
    html = html.replace('__DONUT_LABELS__', json.dumps(cat_names))
    html = html.replace('__DONUT_DATA__', json.dumps(donut_totals))
    html = html.replace('__DONUT_COLORS__', json.dumps(donut_colors))

    return html
