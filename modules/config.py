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

# 表格显示配置
TABLE_CONFIG = {
    "height": 500,  # 表格高度（像素）
    "row_height": 35,  # 行高（像素）
    "header_bg_color": "#f0f2f6",  # 表头背景色
    "header_text_color": "#333333",  # 表头文字颜色
    "border_color": "#e0e0e0",  # 边框颜色
    "link_color": "#1e88e5",  # 链接颜色
    "positive_color": "#ef4444",  # 正值颜色（红色）
    "negative_color": "#10b981",  # 负值颜色（绿色）
    "hover_color": "#f5f5f5"  # 鼠标悬停颜色
}

# 列宽配置
COLUMN_WIDTH = {
    "股票代码": 80,
    "基金代码": 80,
    "股票名称": 120,
    "基金简称": 150,
    "行业": 100,
    "基金类型": 80,
    "年化收益率": 100,
    "上市年限": 80,
    "default": 90  # 默认列宽
}

# 外部链接配置
EXTERNAL_LINKS = {
    "stock": {
        "同花顺": "https://stockpage.10jqka.com.cn/{code}",
        "雪球": "https://xueqiu.com/S/{exchange}{code}",
        "东方财富": "https://quote.eastmoney.com/{exchange}{code}.html"
    },
    "fund": {
        "同花顺": "https://fund.10jqka.com.cn/{code}",
        "东方财富": "https://fund.eastmoney.com/{code}.html",
        "天天基金": "https://fund.eastmoney.com/{code}.html"
    }
}

# 数据格式化配置
FORMAT_CONFIG = {
    "percent_columns": [
        "当前ROE", "ROE", "股息", "最新股息", "平均股息", 
        "今年来", "持股比", "平均ROE", "年化收益率"
    ],
    "money_columns": ["持有市值"],
    "float_columns": ["扣非PE", "PB", "PEG", "便宜指数"],
    "int_columns": ["股东数", "控盘度", "推荐数"]
}
