import json
import re
import statistics
from collections import defaultdict
from datetime import datetime

import requests

import settings

_COLOR_STOMACH = "#14B8A6"

STOMACH_CHART_NAMES = ['胃病']

# 餐前/餐後感覺的下拉選單選項，數字為不適度（越大越不舒服）
_DISCOMFORT_LEVELS = {
    '沒感覺': 0,
    '幾乎沒感覺': 1,
    '輕微違和感': 2,
    '有點不舒服': 3,
    '非常不舒服': 4,
}
_MAX_DISCOMFORT = 4

# 每惡化一級要扣的分數
_WORSENING_PENALTY = 8

_DATE_FORMAT = '%Y/%m/%d'
_NUMBER_PATTERN = re.compile(r'-?\d+(?:\.\d+)?')


def _fetch_records():
    resp = requests.get(
        settings.URL_GAS_API,
        params={"action": "action_get_stomach_records"},
        timeout=30
    )
    data = resp.json()
    return json.loads(data["responseMsg"])


def _parse_level(text):
    """把感覺欄的中文轉成不適度 0~4，無法辨識回傳 None"""
    if text is None:
        return None
    return _DISCOMFORT_LEVELS.get(str(text).strip())


def _parse_weight(value):
    """把重量欄轉成公克數，無法辨識或非正數回傳 None

    表上實際存的是「42 g」這種帶單位的值，所以只抽出數字部分。"""
    if value is None:
        return None
    match = _NUMBER_PATTERN.search(str(value))
    if not match:
        return None
    weight = float(match.group())
    return weight if weight > 0 else None


def _parse_date(value):
    """把日期欄轉成 date，無法辨識回傳 None

    表上實際存的是「2026/07/02 週四」，星期部分直接捨去。"""
    if value is None:
        return None
    head = str(value).strip().split()
    if not head:
        return None
    try:
        return datetime.strptime(head[0], _DATE_FORMAT).date()
    except ValueError:
        return None


def _base_weights(records):
    """各餐別各自的基準重量（同餐別重量的中位數）

    早餐與晚餐的份量本來就差一倍以上，用同一個全域基準會讓早餐永遠被
    當成吃太少、晚餐永遠被當成吃很多，圖表就變成在反映餐別而不是病情。
    """
    weights_by_meal_type = defaultdict(list)
    for record in records:
        weight = _parse_weight(record.get('weight'))
        if weight is None:
            continue
        weights_by_meal_type[str(record.get('mealType', '')).strip()].append(weight)

    return {meal_type: statistics.median(weights)
            for meal_type, weights in weights_by_meal_type.items()}


def _score_meal(weight, before, after, base_weight):
    """單餐耐受度分數（下限 0，不封頂）

    舒適度   = (4 - 餐後) / 4
    惡化     = max(0, 餐後 - 餐前)
    食量係數 = 重量 / 同餐別基準重量
    分數     = 100 x 舒適度 x 食量係數 - 8 x 惡化

    刻意不封頂：吃得比過去的自己更多而且沒有不適，就該拿到超過 100 分，
    食量成長本身就是恢復的主要訊號，壓在上限等於把它丟掉。
    """
    weight_value = _parse_weight(weight)
    before_level = _parse_level(before)
    after_level = _parse_level(after)
    if weight_value is None or before_level is None or after_level is None:
        return None
    if not base_weight:
        return None

    comfort = (_MAX_DISCOMFORT - after_level) / _MAX_DISCOMFORT
    worsening = max(0, after_level - before_level)
    weight_factor = weight_value / base_weight

    score = 100 * comfort * weight_factor - _WORSENING_PENALTY * worsening
    return max(0.0, score)


def _daily_scores(records):
    """回傳依日期排序的 [(date, 當日平均分數)]，無法使用的列直接略過"""
    base_weights = _base_weights(records)
    if not base_weights:
        return []

    by_date = defaultdict(list)
    for record in records:
        day = _parse_date(record.get('date'))
        if day is None:
            continue
        base_weight = base_weights.get(str(record.get('mealType', '')).strip())
        score = _score_meal(record.get('weight'), record.get('before'),
                            record.get('after'), base_weight)
        if score is None:
            continue
        by_date[day].append(score)

    return [(day, sum(scores) / len(scores))
            for day, scores in sorted(by_date.items())]


def generate_stomach_chart():
    """回傳 (file_name, error_message)，成功時 error_message 為 None"""
    from dashboardHelper.recentSection import (
        _new_axes, _plot_series, _finalize_and_save)

    try:
        records = _fetch_records()
    except Exception as e:
        return None, f'資料載入失敗：{e}'

    daily = _daily_scores(records)
    if not daily:
        return None, '尚無足夠資料'

    file_name = 'stomach_chart.jpg'
    fig, ax = _new_axes()
    _plot_series(ax, daily, _COLOR_STOMACH, '每日平均分數')
    ax.set_ylim(bottom=0)
    # 100 分 = 吃到平常份量且完全沒感覺，超過代表比過去的自己吃得更多還沒事
    ax.axhline(100, color='#94A3B8', linestyle='--', linewidth=1, alpha=0.7)
    _finalize_and_save(fig, ax, '胃病恢復狀況', '分數', file_name)
    return file_name, None
