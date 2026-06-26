import json
import re
import html as html_lib
from datetime import datetime, timezone, timedelta
import requests

TAIWAN_TZ = timezone(timedelta(hours=8))
LARGE_INCOME_NAMES = {'生生收入', '老婆收入'}
MONTHLY_INCOME_NAMES = {'生生收入', '老婆收入', '租屋補助', '育兒補助'}
MONTHLY_INCOME_ORDER = ['生生收入', '老婆收入', '租屋補助', '育兒補助']
MONTH_NAMES = ['', '1月', '2月', '3月', '4月', '5月', '6月',
               '7月', '8月', '9月', '10月', '11月', '12月']
MEMO_BUY_RE = re.compile(r'(\d{1,2})月(初|中|底)買(.+)')
TIMING_ORDER = {'初': 1, '中': 2, '底': 3}


def _call_gas(gas_url, params):
    r = requests.get(gas_url, params=params, timeout=15)
    return json.loads(r.json()['responseMsg'])


def _call_gas_raw(gas_url, params):
    r = requests.get(gas_url, params=params, timeout=15)
    data = r.json()
    if data.get('statusCode') != 200:
        return ''
    return data.get('responseMsg', '')


def _fmt(n):
    return f'{int(n):,}'


def _e(s):
    return html_lib.escape(str(s))


def _fetch_all(gas_url):
    now = datetime.now(TAIWAN_TZ)
    year, month = now.year, now.month
    if month == 12:
        last_day = 31
    else:
        last_day = (datetime(year, month + 1, 1, tzinfo=TAIWAN_TZ) - timedelta(days=1)).day

    items = _call_gas(gas_url, {
        'action': 'action_get_accounting_items',
        'startDate': f'{year}/{month:02d}/01',
        'endDate': f'{year}/{month:02d}/{last_day:02d}'
    })
    budget = _call_gas(gas_url, {
        'action': 'action_get_budget_status',
        'year': year, 'month': month
    })
    schedule = _call_gas(gas_url, {'action': 'action_get_special_schedule'})
    memo_text = _call_gas_raw(gas_url, {'action': 'action_memo_get'})
    return now, items, budget, schedule, memo_text


def _next_income_info(schedule, current_month):
    income_by_month = {}
    for item in schedule:
        if item['name'] in LARGE_INCOME_NAMES:
            income_by_month.setdefault(item['specialMonth'], []).append(item)

    if not income_by_month:
        return None, [], {}

    sorted_months = sorted(income_by_month)
    future = [m for m in sorted_months if m > current_month]
    target = future[0] if future else sorted_months[0]

    income_items = income_by_month[target]
    expenses = {}
    for item in schedule:
        if item['name'] in LARGE_INCOME_NAMES:
            continue
        m = item['specialMonth']
        if target > current_month:
            in_range = current_month < m < target
        else:
            in_range = m > current_month or m < target
        if in_range:
            expenses.setdefault(m, []).append(item)

    return target, income_items, expenses


def generate_html(gas_url):
    now, items, budget, schedule, memo_text = _fetch_all(gas_url)
    year, month = now.year, now.month

    total_spent_all = sum(i['prize'] for i in items)
    active_cats = [c for c in budget['categories'] if c['spent'] > 0]
    budget_total = sum(c['effectiveBudget'] for c in active_cats)
    diff = budget_total - total_spent_all

    next_month, income_items, expense_by_month = _next_income_info(schedule, month)
    total_income = sum(i['specialAmount'] for i in income_items)
    total_special_expense = sum(
        i['specialAmount']
        for month_items in expense_by_month.values()
        for i in month_items
    )

    diff_cls = 'positive' if diff >= 0 else 'negative'
    diff_prefix = '+' if diff >= 0 else ''

    income_cat_map = {c['name']: c for c in budget['categories'] if c['name'] in MONTHLY_INCOME_NAMES}
    special_this_month = {}
    for s in schedule:
        if s['name'] in MONTHLY_INCOME_NAMES and s['specialMonth'] == month:
            special_this_month.setdefault(s['name'], []).append(s)
    income_breakdown = [
        {
            'name': name,
            'total': income_cat_map.get(name, {}).get('effectiveBudget', 0),
            'specials': special_this_month.get(name, [])
        }
        for name in MONTHLY_INCOME_ORDER
    ]
    monthly_income = sum(item['total'] for item in income_breakdown)
    income_diff = monthly_income - total_spent_all
    income_diff_cls = 'positive' if income_diff >= 0 else 'negative'
    income_diff_prefix = '+' if income_diff >= 0 else ''

    tooltip_rows = ''
    for item in income_breakdown:
        tooltip_rows += f'<div class="tooltip-row"><span>{_e(item["name"])}</span><span>＄{_fmt(item["total"])}</span></div>'
        for s in item['specials']:
            tooltip_rows += f'<div class="tooltip-row tooltip-special"><span>{_e(s["specialItem"])}</span><span class="tooltip-plus">+＄{_fmt(s["specialAmount"])}</span></div>'
    tooltip_rows += f'<div class="tooltip-total"><span>合計</span><span>＄{_fmt(monthly_income)}</span></div>'

    # ── Section 1: 概覽 ──────────────────────────────────────────
    section1 = f'''
  <div class="section">
    <h2 class="section-title">📅 {year}年{month}月概覽</h2>
    <div class="summary-cards">
      <div class="summary-card-main">
        <div class="card-label">當月總花費</div>
        <div class="card-value">＄{_fmt(total_spent_all)}</div>
      </div>
      <div class="summary-cards-right">
        <div class="summary-card-small">
          <div class="card-label">預算合計</div>
          <div class="card-value">＄{_fmt(budget_total)}</div>
        </div>
        <div class="summary-card-small">
          <div class="card-label">預算使用結餘</div>
          <div class="card-value {diff_cls}">{diff_prefix}＄{_fmt(abs(diff))}</div>
        </div>
        <div class="summary-card-small income-card">
          <div class="card-label">本月收入<button class="info-btn" onclick="toggleIncomeTooltip(event)">?</button></div>
          <div class="card-value">＄{_fmt(monthly_income)}</div>
          <div class="income-tooltip" id="income-tooltip">
            {tooltip_rows}
          </div>
        </div>
        <div class="summary-card-small">
          <div class="card-label">收支結餘</div>
          <div class="card-value {income_diff_cls}">{income_diff_prefix}＄{_fmt(abs(income_diff))}</div>
        </div>
      </div>
    </div>
  </div>'''

    # ── Section 2: 各分類預算 ────────────────────────────────────
    rows = ''
    for cat in active_cats:
        pct = int(cat['spent'] / cat['effectiveBudget'] * 100) if cat['effectiveBudget'] > 0 else 0
        bar_width = min(pct, 100)
        bar_cls = 'progress-over' if pct >= 100 else ('progress-warn' if pct >= 80 else 'progress-normal')
        row_cls = 'budget-row overspent' if cat['isOverBudget'] else 'budget-row'
        d = cat['diff']
        d_cls = 'negative' if d < 0 else 'dim'
        d_prefix = '-' if d < 0 else ''
        rows += f'''
      <div class="{row_cls}">
        <div class="row-header">
          <span class="cat-name">{_e(cat["name"])}</span>
          <span class="cat-diff {d_cls}">{d_prefix}＄{_fmt(abs(d))}</span>
        </div>
        <div class="row-meta">花費 ＄{_fmt(cat["spent"])} / 預算 ＄{_fmt(cat["effectiveBudget"])} ({pct}%)</div>
        <div class="progress-bar">
          <div class="progress-fill {bar_cls}" style="width:{bar_width}%"></div>
        </div>
      </div>'''

    section2 = f'''
  <div class="section">
    <h2 class="section-title">📊 各分類預算使用</h2>
    <div class="budget-list">{rows}
    </div>
  </div>'''

    # ── Section 3: 下次大筆入帳 ──────────────────────────────────
    section3 = ''
    if next_month:
        income_rows = ''
        for item in income_items:
            income_rows += f'''
        <div class="flow-row">
          <span>{_e(item["name"])}</span>
          <span class="positive">+＄{_fmt(item["specialAmount"])}</span>
        </div>'''
            if item.get('specialItem'):
                income_rows += f'''
        <div class="flow-item-desc">{_e(item["specialItem"])}</div>'''
        income_rows += f'''
        <div class="flow-row total-row">
          <span>合計</span>
          <span class="positive">+＄{_fmt(total_income)}</span>
        </div>'''

        # Parse pending purchases from memo items
        pending_by_month = {}
        if memo_text:
            for line in memo_text.splitlines():
                m_obj = MEMO_BUY_RE.search(line.strip())
                if m_obj:
                    m_num = int(m_obj.group(1))
                    timing = m_obj.group(2)
                    item_name = m_obj.group(3).strip()
                    if next_month > month:
                        in_range = month < m_num <= next_month
                    else:
                        in_range = m_num > month or m_num <= next_month
                    if in_range:
                        pending_by_month.setdefault(m_num, []).append({
                            'timing': timing, 'name': item_name
                        })
        for m_num in pending_by_month:
            pending_by_month[m_num].sort(key=lambda x: TIMING_ORDER.get(x['timing'], 99))

        all_months = sorted(set(list(expense_by_month.keys()) + list(pending_by_month.keys())))
        pending_count = sum(len(v) for v in pending_by_month.values())

        if all_months:
            expense_rows = ''
            for m in all_months:
                for item in expense_by_month.get(m, []):
                    item_desc = f'<div class="flow-item-desc">{_e(item["specialItem"])}</div>' if item.get('specialItem') else ''
                    expense_rows += f'''
        <div class="flow-row">
          <span class="month-tag">{MONTH_NAMES[m]}</span>
          <span class="flow-cat-group"><span>{_e(item["name"])}</span>{item_desc}</span>
          <span class="negative">＄{_fmt(item["specialAmount"])}</span>
        </div>'''
                for p in pending_by_month.get(m, []):
                    expense_rows += f'''
        <div class="flow-row pending-row">
          <span class="month-tag pending-tag">{MONTH_NAMES[m]}{p["timing"]}</span>
          <span class="flow-cat-group"><span>{_e(p["name"])}</span><div class="flow-item-desc">待購買</div></span>
          <span class="dim">—</span>
        </div>'''
            total_label = f'＄{_fmt(total_special_expense)}'
            if pending_count:
                total_label += f' + {pending_count}筆待購買'
            expense_rows += f'''
        <div class="flow-row total-row">
          <span></span><span>合計</span>
          <span class="negative">{total_label}</span>
        </div>'''
        else:
            expense_rows = '<div class="empty-msg">此期間無特殊支出</div>'

        section3 = f'''
  <div class="section">
    <h2 class="section-title">💰 下次大筆入帳前</h2>
    <div class="flow-card">
      <div class="flow-header">下次大筆入帳：{MONTH_NAMES[next_month]}</div>
      <div class="flow-block">{income_rows}</div>
      <div class="flow-divider"></div>
      <div class="flow-subheader">在此之前的特殊支出</div>
      <div class="flow-block">{expense_rows}</div>
    </div>
  </div>'''

    update_time = now.strftime('%Y/%m/%d %H:%M')
    return f'''{section1}
{section2}
{section3}
  <div class="update-time">資料更新時間：{update_time}</div>'''
