"""
全局配置文件
"""

import os

# 应用基本信息
APP_TITLE = "投资理财筛选系统"
APP_ICON = "📈"
APP_VERSION = "2.0.0"

# 数据路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data")
FUND_DATA_PATH = os.path.join(DATA_PATH, "fund")
STOCK_DATA_PATH = os.path.join(DATA_PATH, "stock")

# 当前数据日期
CURRENT_DATA_DATE = "2025.08"

# 用户数据目录
USER_DATA_PATH = os.path.join(BASE_DIR, "user_data")
if not os.path.exists(USER_DATA_PATH):
    try:
        os.makedirs(USER_DATA_PATH)
    except Exception:
        pass

# 股票数据类型映射
STOCK_TYPE_MAPPING = {
    "hot": "热门股票",
    "dividend": "股息率排名",
    "roe": "ROE排名",
    "peg": "PEG排名",
    "cheapest": "最便宜股票",
    "fund_holding": "基金重仓股",
    "research": "券商研报推荐",
    "northbound": "北上资金持股",
    "control": "控盘度排名",
    "shareholders": "股东数最少排名"
}

# 基金类型映射
FUND_TYPE_MAPPING = {
    "stock": "股票型",
    "hybrid": "混合型",
    "bond": "债券型",
    "index": "指数型"
}

# 时间段映射
TIME_PERIOD_MAPPING = {
    "day": "近1天",
    "three_days": "近3天",
    "week": "近1周",
    "month": "近1月",
    "three_months": "近3月",
    "six_months": "近6月",
    "year": "近1年",
    "three_years": "近3年",
    "five_years": "近5年"
}
