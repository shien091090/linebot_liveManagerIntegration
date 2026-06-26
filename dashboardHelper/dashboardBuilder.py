from dashboardHelper.economySection import generate_html as economy_html
from dashboardHelper.futureSection import generate_html as future_html
from dashboardHelper.recentSection import generate_html as recent_html

_CSS = '''
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
    background: #F8FAFC;
    color: #0F172A;
    font-size: 14px;
    line-height: 1.5;
}
.tabs {
    display: flex;
    background: #fff;
    border-bottom: 1px solid #E2E8F0;
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.tab-btn {
    flex: 1;
    padding: 14px 4px;
    border: none;
    background: transparent;
    cursor: pointer;
    font-size: 13px;
    font-weight: 500;
    color: #94A3B8;
    border-bottom: 2px solid transparent;
    transition: color 0.15s, border-color 0.15s;
    font-family: inherit;
}
.tab-btn.active { color: #2563EB; border-bottom-color: #2563EB; font-weight: 600; }
.tab-btn:hover:not(.active) { color: #475569; background: #F8FAFC; }
.container { max-width: 640px; margin: 0 auto; padding: 16px; }
.section { margin-bottom: 20px; }
.section-title { font-size: 15px; font-weight: 600; color: #1E293B; margin-bottom: 12px; }

/* Summary cards */
.summary-cards { display: flex; gap: 10px; align-items: stretch; }
.summary-card-main {
    flex: 1.1; min-width: 0;
    background: #fff; border-radius: 12px; padding: 18px 14px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.07), 0 0 0 1px rgba(0,0,0,0.04);
    display: flex; flex-direction: column; justify-content: center;
}
.summary-cards-right {
    flex: 1; display: grid;
    grid-template-columns: 1fr 1fr; gap: 8px;
}
.summary-card-small {
    background: #fff; border-radius: 10px; padding: 10px 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.07), 0 0 0 1px rgba(0,0,0,0.04);
    min-width: 0;
}
.card-label {
    font-size: 10px; font-weight: 600; color: #94A3B8;
    letter-spacing: 0.04em; margin-bottom: 6px;
    white-space: normal; overflow: hidden;
}
.summary-card-main .card-value {
    font-size: 22px; font-weight: 700; color: #0F172A;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.summary-card-small .card-value {
    font-size: 14px; font-weight: 700; color: #0F172A;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}

/* Budget list */
.budget-list {
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.07), 0 0 0 1px rgba(0,0,0,0.04);
    overflow: hidden;
}
.budget-row { padding: 12px 16px; border-bottom: 1px solid #F1F5F9; }
.budget-row:last-child { border-bottom: none; }
.budget-row.overspent { background: #FEF2F2; }
.row-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 3px; }
.cat-name { font-size: 14px; font-weight: 500; color: #1E293B; }
.cat-diff { font-size: 13px; font-weight: 600; }
.row-meta { font-size: 11px; color: #94A3B8; margin-bottom: 7px; }
.progress-bar { height: 5px; background: #E2E8F0; border-radius: 3px; overflow: hidden; }
.progress-fill { height: 100%; border-radius: 3px; }
.progress-normal { background: #2563EB; }
.progress-warn { background: #D97706; }
.progress-over { background: #DC2626; }

/* Flow card */
.flow-card {
    background: #fff;
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.07), 0 0 0 1px rgba(0,0,0,0.04);
}
.flow-header { font-size: 15px; font-weight: 700; color: #1E293B; margin-bottom: 10px; }
.flow-subheader { font-size: 12px; font-weight: 600; color: #64748B; margin: 2px 0 8px; }
.flow-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 5px 0; font-size: 14px; gap: 8px;
}
.flow-row.total-row {
    font-weight: 700;
    border-top: 1px solid #E2E8F0;
    padding-top: 8px; margin-top: 4px;
}
.month-tag {
    font-size: 11px; font-weight: 600; color: #64748B;
    background: #F1F5F9; padding: 2px 7px;
    border-radius: 4px; min-width: 32px; text-align: center;
    flex-shrink: 0;
}
.flow-divider { height: 1px; background: #E2E8F0; margin: 12px 0; }
.empty-msg { font-size: 13px; color: #94A3B8; padding: 6px 0; }

/* Colors */
.positive { color: #059669; }
.negative { color: #DC2626; }
.dim { color: #64748B; }
.card-value.positive { color: #059669; }
.card-value.negative { color: #DC2626; }

/* Income tooltip */
.income-card { position: relative; }
.info-btn {
    display: inline-flex; align-items: center; justify-content: center;
    width: 13px; height: 13px; border-radius: 50%;
    background: #CBD5E1; color: #64748B;
    border: none; cursor: pointer; font-size: 9px; font-weight: 700;
    margin-left: 4px; vertical-align: middle;
    font-family: inherit; padding: 0; line-height: 1; flex-shrink: 0;
}
.info-btn:hover { background: #94A3B8; color: #fff; }
.income-tooltip {
    display: none; position: absolute;
    top: calc(100% + 6px); left: 0;
    background: #1E293B; color: #F1F5F9;
    border-radius: 8px; padding: 10px 12px;
    font-size: 12px; min-width: 160px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.25);
    z-index: 200; white-space: nowrap;
}
.income-tooltip.show { display: block; }
.tooltip-row {
    display: flex; justify-content: space-between;
    gap: 16px; padding: 2px 0; color: #CBD5E1;
}
.tooltip-special {
    padding-left: 10px; font-size: 11px; color: #94A3B8;
}
.tooltip-plus { color: #34D399; }
.tooltip-total {
    display: flex; justify-content: space-between; gap: 16px;
    border-top: 1px solid #334155; margin-top: 6px; padding-top: 6px;
    font-weight: 600; color: #F1F5F9;
}

/* Responsive: stack summary cards vertically on narrow screens */
@media (max-width: 480px) {
    .summary-cards { flex-direction: column; }
    .summary-card-small .card-value { font-size: 16px; }
}

/* Update time */
.update-time { font-size: 11px; color: #94A3B8; text-align: right; margin-top: 4px; }

/* WIP */
.wip {
    background: #fff; border-radius: 12px;
    padding: 48px 20px; text-align: center;
    color: #94A3B8; font-size: 14px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.07);
}
'''

_JS = '''
function switchTab(btn, name) {
    document.querySelectorAll('.tab-content').forEach(function(el) { el.style.display = 'none'; });
    document.querySelectorAll('.tab-btn').forEach(function(el) { el.classList.remove('active'); });
    document.getElementById('tab-' + name).style.display = 'block';
    btn.classList.add('active');
}
function toggleIncomeTooltip(e) {
    e.stopPropagation();
    document.getElementById('income-tooltip').classList.toggle('show');
}
document.addEventListener('click', function() {
    var t = document.getElementById('income-tooltip');
    if (t) t.classList.remove('show');
});
'''


def build_dashboard(gas_url):
    econ = economy_html(gas_url)
    fut = future_html()
    rec = recent_html()

    return f'''<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>家庭財務總覽</title>
<style>{_CSS}</style>
</head>
<body>
<div class="tabs">
  <button class="tab-btn active" onclick="switchTab(this, 'economy')">經濟狀況</button>
  <button class="tab-btn" onclick="switchTab(this, 'future')">未來安排</button>
  <button class="tab-btn" onclick="switchTab(this, 'recent')">近期狀況</button>
</div>
<div class="container">
  <div id="tab-economy" class="tab-content">{econ}</div>
  <div id="tab-future" class="tab-content" style="display:none">{fut}</div>
  <div id="tab-recent" class="tab-content" style="display:none">{rec}</div>
</div>
<script>{_JS}</script>
</body>
</html>'''
