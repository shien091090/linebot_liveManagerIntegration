import json
import html as html_lib
from datetime import datetime, timezone, timedelta
import requests

TAIWAN_TZ = timezone(timedelta(hours=8))
LARGE_INCOME_NAMES = {'生生收入', '老婆收入'}
MONTHLY_INCOME_NAMES = {'生生收入', '老婆收入', '租屋補助', '育兒補助'}
MONTH_NAMES = ['', '1月', '2月', '3月', '4月', '5月', '6月',
               '7月', '8月', '9月', '10月', '11月', '12月']


def _call_gas(gas_url, params):
    r = requests.get(gas_url, params=params, timeout=15)
    return json.loads(r.json()['responseMsg'])


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
    return now, items, budget, schedule


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
    now, items, budget, schedule = _fetch_all(gas_url)
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

    monthly_income = sum(
        c['effectiveBudget'] for c in budget['categories']
        if c['name'] in MONTHLY_INCOME_NAMES
    )
    income_diff = monthly_income - total_spent_all
    income_diff_cls = 'positive' if income_diff >= 0 else 'negative'
    income_diff_prefix = '+' if income_diff >= 0 else ''

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
        <div class="summary-card-small">
          <div class="card-label">本月收入</div>
          <div class="card-value">＄{_fmt(monthly_income)}</div>
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
        income_rows += f'''
        <div class="flow-row total-row">
          <span>合計</span>
          <span class="positive">+＄{_fmt(total_income)}</span>
        </div>'''

        if expense_by_month:
            expense_rows = ''
            for m in sorted(expense_by_month):
                for item in expense_by_month[m]:
                    expense_rows += f'''
        <div class="flow-row">
          <span class="month-tag">{MONTH_NAMES[m]}</span>
          <span>{_e(item["name"])}</span>
          <span class="negative">＄{_fmt(item["specialAmount"])}</span>
        </div>'''
            expense_rows += f'''
        <div class="flow-row total-row">
          <span></span><span>合計</span>
          <span class="negative">＄{_fmt(total_special_expense)}</span>
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
