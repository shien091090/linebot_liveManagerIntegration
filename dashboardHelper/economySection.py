import json
import os
import re
import tempfile
import threading
import time
import html as html_lib
from contextlib import contextmanager
from datetime import datetime, timezone, timedelta
import requests

try:
    import fcntl
except ImportError:
    fcntl = None

TAIWAN_TZ = timezone(timedelta(hours=8))
LARGE_INCOME_NAMES = {'生生收入', '老婆收入'}
MONTHLY_INCOME_NAMES = {'生生收入', '老婆收入', '租屋補助', '育兒補助'}
MONTHLY_INCOME_ORDER = ['生生收入', '老婆收入', '租屋補助', '育兒補助']
# 預算設定表中收入區段的起訖列; 區段內的臨時收入列(如一次性賣東西)也算當月收入
INCOME_SECTION_START = '收入Memo'
INCOME_SECTION_END = '每月固定收入'
MONTH_NAMES = ['', '1月', '2月', '3月', '4月', '5月', '6月',
               '7月', '8月', '9月', '10月', '11月', '12月']
MEMO_BUY_RE = re.compile(r'(\d{1,2})月(初|中|底)買(.+)')
TIMING_ORDER = {'初': 1, '中': 2, '底': 3}


def _fmt(n):
    return f'{int(n):,}'


def _e(s):
    return html_lib.escape(str(s))


def _sort_months_from(months, from_month):
    return sorted(months, key=lambda m: (m - from_month) % 12)


def _month_display(m, from_month, to_month, base_year, current_year):
    is_cross_year = to_month < from_month
    disp_year = base_year + 1 if (is_cross_year and m <= to_month) else base_year
    if disp_year > current_year:
        return f'{disp_year}/{MONTH_NAMES[m]}'
    return MONTH_NAMES[m]


def _income_month_label(m, year_offset, base_year):
    if year_offset > 0:
        return f'{base_year + year_offset}/{MONTH_NAMES[m]}'
    return MONTH_NAMES[m]


def _parse_pending_purchases(memo_text):
    items = []
    if memo_text:
        for line in memo_text.splitlines():
            m_obj = MEMO_BUY_RE.search(line.strip())
            if m_obj:
                items.append((int(m_obj.group(1)), m_obj.group(2), m_obj.group(3).strip()))
    return items


def _filter_pending_for_range(all_pending, from_month, to_month):
    pending_by_month = {}
    for m_num, timing, name in all_pending:
        if to_month >= from_month:
            in_range = from_month <= m_num <= to_month
        else:
            in_range = m_num >= from_month or m_num <= to_month
        if in_range:
            pending_by_month.setdefault(m_num, []).append({'timing': timing, 'name': name})
    for m_num in pending_by_month:
        pending_by_month[m_num].sort(key=lambda x: TIMING_ORDER.get(x['timing'], 99))
    return pending_by_month


def _build_expense_rows(expense_by_month, pending_by_month, from_month, to_month,
                        base_year, current_year, total_expense):
    all_months = _sort_months_from(
        sorted(set(list(expense_by_month.keys()) + list(pending_by_month.keys()))),
        from_month
    )
    pending_count = sum(len(v) for v in pending_by_month.values())

    if not all_months:
        return '<div class="empty-msg">此期間無特殊支出</div>', 0

    rows = ''
    for m in all_months:
        tag = _month_display(m, from_month, to_month, base_year, current_year)
        for item in expense_by_month.get(m, []):
            item_desc = (f'<div class="flow-item-desc">{_e(item["specialItem"])}</div>'
                         if item.get('specialItem') else '')
            rows += f'''
        <div class="flow-row">
          <span class="month-tag">{tag}</span>
          <span class="flow-cat-group"><span>{_e(item["name"])}</span>{item_desc}</span>
          <span class="negative">＄{_fmt(item["specialAmount"])}</span>
        </div>'''
        for p in pending_by_month.get(m, []):
            rows += f'''
        <div class="flow-row pending-row">
          <span class="month-tag pending-tag">{tag}{p["timing"]}</span>
          <span class="flow-cat-group"><span>{_e(p["name"])}</span><div class="flow-item-desc">待購買</div></span>
          <span class="dim">—</span>
        </div>'''

    total_label = f'＄{_fmt(total_expense)}'
    if pending_count:
        total_label += f' + {pending_count}筆待購買'
    rows += f'''
        <div class="flow-row total-row">
          <span>合計</span>
          <span class="negative">{total_label}</span>
        </div>'''

    return rows, pending_count


def _next_income_info(schedule, current_month):
    income_by_month = {}
    for item in schedule:
        if item['name'] in LARGE_INCOME_NAMES:
            income_by_month.setdefault(item['specialMonth'], []).append(item)

    if not income_by_month:
        return None, [], {}

    sorted_months = sorted(income_by_month)
    # 本月本身也算「下次大筆入帳」（specialMonth 只有月份沒有日期，無法判斷本月的是否已入帳），
    # 用嚴格大於會把本月跳過、繞回明年最早的那筆
    future = [m for m in sorted_months if m >= current_month]
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


def _next_next_income_info(schedule, next_month):
    income_by_month = {}
    for item in schedule:
        if item['name'] in LARGE_INCOME_NAMES:
            income_by_month.setdefault(item['specialMonth'], []).append(item)

    if not income_by_month:
        return None, [], {}

    sorted_months = sorted(income_by_month)
    future = [m for m in sorted_months if m > next_month]
    target = future[0] if future else sorted_months[0]

    if target == next_month:
        return None, [], {}

    income_items = income_by_month[target]
    expenses = {}
    for item in schedule:
        if item['name'] in LARGE_INCOME_NAMES:
            continue
        m = item['specialMonth']
        if target > next_month:
            in_range = next_month <= m <= target
        else:
            in_range = m >= next_month or m <= target
        if in_range:
            expenses.setdefault(m, []).append(item)

    return target, income_items, expenses


def _extra_income_categories(categories):
    names = [c['name'] for c in categories]
    if INCOME_SECTION_START not in names:
        return []
    start = names.index(INCOME_SECTION_START) + 1
    end = names.index(INCOME_SECTION_END) if INCOME_SECTION_END in names[start:] else len(names)
    return [c for c in categories[start:end]
            if c['name'] not in MONTHLY_INCOME_NAMES and c['effectiveBudget'] != 0]


def _income_breakdown(categories, schedule, month):
    income_cat_map = {c['name']: c for c in categories if c['name'] in MONTHLY_INCOME_NAMES}
    special_this_month = {}
    for s in schedule:
        if s['name'] in MONTHLY_INCOME_NAMES and s['specialMonth'] == month:
            special_this_month.setdefault(s['name'], []).append(s)
    breakdown = [
        {
            'name': name,
            'total': income_cat_map.get(name, {}).get('effectiveBudget', 0),
            'specials': special_this_month.get(name, [])
        }
        for name in MONTHLY_INCOME_ORDER
    ]
    breakdown += [{'name': c['name'], 'total': c['effectiveBudget'], 'specials': []}
                  for c in _extra_income_categories(categories)]
    return breakdown


def _render_month_pane(year, month, items, budget, budget_types, schedule, prefix):
    total_spent_all = sum(i['prize'] for i in items)
    active_cats = [c for c in budget.get('categories', [])
                   if (c['spent'] > 0 or c['effectiveBudget'] > 0)
                   and c['name'] not in MONTHLY_INCOME_NAMES
                   and (not budget_types or c['name'] in budget_types)]
    budget_total = sum(c['effectiveBudget'] for c in active_cats)
    diff = budget_total - total_spent_all

    diff_cls = 'positive' if diff >= 0 else 'negative'
    diff_prefix = '+' if diff >= 0 else '-'

    income_breakdown = _income_breakdown(budget.get('categories', []), schedule, month)
    monthly_income = sum(item['total'] for item in income_breakdown)
    income_diff = monthly_income - total_spent_all
    income_diff_cls = 'positive' if income_diff >= 0 else 'negative'
    income_diff_prefix = '+' if income_diff >= 0 else '-'

    tooltip_rows = ''
    for item in income_breakdown:
        tooltip_rows += f'<div class="tooltip-row"><span>{_e(item["name"])}</span><span>＄{_fmt(item["total"])}</span></div>'
        for s in item['specials']:
            tooltip_rows += f'<div class="tooltip-row tooltip-special"><span>{_e(s["specialItem"])}</span><span class="tooltip-plus">+＄{_fmt(s["specialAmount"])}</span></div>'
    tooltip_rows += f'<div class="tooltip-total"><span>合計</span><span>＄{_fmt(monthly_income)}</span></div>'

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
          <div class="card-label">{month}月收入<button class="info-btn" onclick="toggleIncomeTooltip(event)">?</button></div>
          <div class="card-value">＄{_fmt(monthly_income)}</div>
          <div class="income-tooltip">
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

    cat_items_map = {}
    for orig_idx, item in enumerate(items):
        if item['prize'] > 0 and item.get('budgetType'):
            cat_items_map.setdefault(item['budgetType'], []).append((orig_idx, item))
    top_items_by_cat = {}
    for cat_name, cat_list in cat_items_map.items():
        sorted_list = sorted(
            cat_list,
            key=lambda x: (-x[1]['prize'], -int(x[1]['date'].replace('/', '')), x[0])
        )
        top_items_by_cat[cat_name] = [item for _, item in sorted_list[:5]]

    rows = ''
    for i, cat in enumerate(active_cats):
        pct = int(cat['spent'] / cat['effectiveBudget'] * 100) if cat['effectiveBudget'] > 0 else 0
        bar_width = min(pct, 100)
        bar_cls = 'progress-over' if pct >= 100 else ('progress-warn' if pct >= 80 else 'progress-normal')
        row_cls = 'budget-row overspent' if cat['isOverBudget'] else 'budget-row'
        d = cat['diff']
        d_cls = 'negative' if d < 0 else 'dim'
        d_prefix = '-' if d < 0 else ''
        top_items = top_items_by_cat.get(cat['name'], [])
        uid = f'{prefix}_{i}'
        if top_items:
            detail_rows = ''.join(
                f'<div class="budget-detail-row">'
                f'<span class="detail-rank">{r}</span>'
                f'<span class="detail-content">{_e(item["content"])}</span>'
                f'<span class="detail-amount">＄{_fmt(item["prize"])}</span>'
                f'</div>'
                for r, item in enumerate(top_items, 1)
            )
            toggle_html = f'<button class="detail-toggle" id="btoggle-{uid}" onclick="toggleBudgetDetail(\'{uid}\')">&#9658;</button>'
            detail_html = f'<div class="budget-details" id="bdetail-{uid}">{detail_rows}</div>'
        else:
            toggle_html = ''
            detail_html = ''
        rows += f'''
      <div class="{row_cls}">
        <div class="row-header">
          <span class="cat-name">{_e(cat["name"])}</span>
          <div class="row-header-right">
            <span class="cat-diff {d_cls}">{d_prefix}＄{_fmt(abs(d))}</span>
            {toggle_html}
          </div>
        </div>
        <div class="row-meta">花費 ＄{_fmt(cat["spent"])} / 預算 ＄{_fmt(cat["effectiveBudget"])} ({pct}%)</div>
        <div class="progress-bar">
          <div class="progress-fill {bar_cls}" style="width:{bar_width}%"></div>
        </div>
        {detail_html}
      </div>'''

    section2 = f'''
  <div class="section">
    <h2 class="section-title">📊 各分類預算使用</h2>
    <div class="budget-list">{rows}
    </div>
  </div>'''

    return section1 + section2


# Heroku 向 GAS 取結果偶爾會卡數十秒, 所以改由背景定時抓好存成檔案, 打開 dashboard 時直接讀檔。
# 存檔案而不是存記憶體, 是因為 gunicorn 有兩個 worker, 要共用同一份結果
CACHE_PATH = os.path.join(tempfile.gettempdir(), 'economy_dashboard_cache.json')
REFRESH_INTERVAL_SECONDS = 600
# 背景抓取沒有人在等, 可以等久一點; Heroku 對外部請求的 30 秒上限只限制使用者開頁面
BACKGROUND_FETCH_TIMEOUT_SECONDS = 90
FOREGROUND_FETCH_TIMEOUT_SECONDS = 25
_CHECK_INTERVAL_SECONDS = 60
_refresh_thread = None


def _read_cache():
    try:
        with open(CACHE_PATH, encoding='utf-8') as f:
            data = json.load(f)
        return data['html'], datetime.fromisoformat(data['at'])
    except (OSError, ValueError, KeyError):
        return None


def _write_cache(html, at):
    tmp_path = f'{CACHE_PATH}.{os.getpid()}.tmp'
    with open(tmp_path, 'w', encoding='utf-8') as f:
        json.dump({'html': html, 'at': at.isoformat()}, f, ensure_ascii=False)
    os.replace(tmp_path, CACHE_PATH)


def _is_cache_stale():
    cached = _read_cache()
    if cached is None:
        return True
    age = (datetime.now(TAIWAN_TZ) - cached[1]).total_seconds()
    # 提早一個檢查週期視為過期, 避免剛好差幾秒而多等一輪
    return age >= REFRESH_INTERVAL_SECONDS - _CHECK_INTERVAL_SECONDS


@contextmanager
def _refresh_lock(blocking):
    # 兩個 worker 同時到期時只讓一個去抓; 本機 Windows 沒有 fcntl, 直接放行
    if fcntl is None:
        yield True
        return
    with open(CACHE_PATH + '.lock', 'w') as lock_file:
        try:
            fcntl.flock(lock_file, fcntl.LOCK_EX | (0 if blocking else fcntl.LOCK_NB))
        except BlockingIOError:
            yield False
            return
        try:
            yield True
        finally:
            fcntl.flock(lock_file, fcntl.LOCK_UN)


def refresh_cache(gas_url, blocking=True, only_if_stale=False, timeout=FOREGROUND_FETCH_TIMEOUT_SECONDS):
    with _refresh_lock(blocking) as acquired:
        if not acquired:
            return
        # 等鎖期間另一個 worker 可能已經更新好了
        if only_if_stale and not _is_cache_stale():
            return
        started = time.time()
        _write_cache(_generate_html_inner(gas_url, timeout=timeout), datetime.now(TAIWAN_TZ))
        print(f'[economySection] cache refreshed pid={os.getpid()} in {time.time() - started:.1f}s')


def request_refresh(gas_url):
    # 記帳等會改動經濟資料的操作完成後呼叫, 不必等下一輪定時更新; 在背景執行不拖慢回覆
    def run():
        try:
            refresh_cache(gas_url, timeout=BACKGROUND_FETCH_TIMEOUT_SECONDS)
        except Exception as e:
            print(f'[economySection] refresh failed: {e}')
    threading.Thread(target=run, daemon=True).start()


def start_background_refresh(gas_url):
    global _refresh_thread
    if _refresh_thread is not None:
        return

    def loop():
        while True:
            if _is_cache_stale():
                try:
                    refresh_cache(gas_url, blocking=False, only_if_stale=True,
                                  timeout=BACKGROUND_FETCH_TIMEOUT_SECONDS)
                except Exception as e:
                    print(f'[economySection] refresh failed: {e}')
            time.sleep(_CHECK_INTERVAL_SECONDS)

    _refresh_thread = threading.Thread(target=loop, daemon=True)
    _refresh_thread.start()


def _with_data_time(html, at):
    return f'<div class="update-time">資料時間 {at:%m/%d %H:%M}（每 10 分鐘更新）</div>' + html


def generate_html(gas_url):
    cached = _read_cache()
    if cached is not None:
        return _with_data_time(*cached)
    # 還沒有快取(剛重啟): 背景已在抓就不讓使用者乾等, 否則(本機開發)當場抓一次
    if _refresh_thread is not None:
        return '<div class="wip">資料準備中，請稍後重新整理</div>'
    try:
        refresh_cache(gas_url, only_if_stale=True)
    except Exception as e:
        return f'<div class="wip">資料載入失敗：{html_lib.escape(str(e))}</div>'
    cached = _read_cache()
    if cached is None:
        return '<div class="wip">資料載入失敗：無法讀取快取</div>'
    return _with_data_time(*cached)


def _generate_html_inner(gas_url, timeout=FOREGROUND_FETCH_TIMEOUT_SECONDS):
    now = datetime.now(TAIWAN_TZ)
    r = requests.get(gas_url, params={'action': 'action_get_dashboard_economy_all_months'}, timeout=timeout)
    data = json.loads(r.json()['responseMsg'])

    year = data['year']
    current_month = data['currentMonth']
    months_map = {m['month']: m for m in data['months']}
    schedule = data['schedule']
    memo_text = data['memo']
    budget_types = set(data.get('budgetTypes', []))

    # Month toggle tabs
    tab_buttons = ''
    for m in range(1, current_month + 1):
        active_cls = ' active' if m == current_month else ''
        tab_buttons += f'<button class="month-tab{active_cls}" data-month="{m}" onclick="switchMonth({m})">{m}月</button>'

    # All month panes (only current month visible by default)
    all_panes = ''
    for m in range(1, current_month + 1):
        md = months_map.get(m, {})
        pane_html = _render_month_pane(
            year, m,
            md.get('items', []),
            md.get('budget', {'categories': []}),
            budget_types, schedule, f'm{m}'
        )
        display = 'block' if m == current_month else 'none'
        all_panes += f'<div class="month-pane" data-month="{m}" style="display:{display}">{pane_html}</div>'

    # Section 3: 下次大筆入帳前 (always based on current month, unaffected by toggle)
    next_month, income_items, _ = _next_income_info(schedule, current_month)
    total_income = sum(i['specialAmount'] for i in income_items)

    section3 = ''
    if next_month:
        all_pending = _parse_pending_purchases(memo_text)
        next_year_offset = 1 if next_month < current_month else 0

        income_rows = ''
        for item in income_items:
            income_rows += f'''
        <div class="flow-row">
          <span>{_e(item["name"])}</span>
          <span class="positive">+＄{_fmt(item["specialAmount"])}</span>
        </div>'''
            if item.get('specialItem'):
                income_rows += f'<div class="flow-item-desc">{_e(item["specialItem"])}</div>'
        income_rows += f'''
        <div class="flow-row total-row">
          <span>合計</span>
          <span class="positive">+＄{_fmt(total_income)}</span>
        </div>'''

        nn_month, _, nn_expense_by_month = _next_next_income_info(schedule, next_month)
        next_hdr = _income_month_label(next_month, next_year_offset, year)

        if nn_month:
            nn_year_offset = next_year_offset + (1 if nn_month < next_month else 0)
            nn_base_year = year + next_year_offset
            nn_total_expense = sum(
                i['specialAmount']
                for m_items in nn_expense_by_month.values()
                for i in m_items
            )
            nn_hdr = _income_month_label(nn_month, nn_year_offset, year)
            pending_for_nn = _filter_pending_for_range(all_pending, next_month, nn_month)
            expense_rows, _ = _build_expense_rows(
                nn_expense_by_month, pending_for_nn,
                next_month, nn_month, nn_base_year, year, nn_total_expense
            )
            expense_subheader = f'在此之後的特殊支出（截至下下次大筆入帳前，時間：{nn_hdr}）'
        else:
            expense_rows = '<div class="empty-msg">無下下次入帳資訊</div>'
            expense_subheader = '在此之後的特殊支出'

        section3 = f'''
  <div class="section">
    <h2 class="section-title">💰 下次大筆入帳前</h2>
    <div class="flow-card">
      <div class="flow-header">下次大筆入帳：{next_hdr}</div>
      <div class="flow-block">{income_rows}</div>
      <div class="flow-divider"></div>
      <div class="flow-subheader">{expense_subheader}</div>
      <div class="flow-block">{expense_rows}</div>
    </div>
  </div>'''

    update_time = now.strftime('%Y/%m/%d %H:%M')
    return f'''<div class="month-tabs">{tab_buttons}</div>
{all_panes}
{section3}
  <div class="update-time">資料更新時間：{update_time}</div>'''
