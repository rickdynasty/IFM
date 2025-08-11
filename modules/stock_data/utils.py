"""
股票数据工具函数
提供通用的辅助函数
"""

import os
from datetime import datetime
from typing import List


def get_available_dates() -> List[str]:
    """
    获取可用的数据日期列表
    
    Returns:
        List[str]: 可用的日期列表，按降序排序
    """
    stock_dir = os.path.join('data', 'stock')
    available_dates = []
    
    if os.path.exists(stock_dir):
        for item in os.listdir(stock_dir):
            if os.path.isdir(os.path.join(stock_dir, item)) and '.' in item:
                # 检查是否是年月格式的目录
                try:
                    year, month = item.split('.')
                    if year.isdigit() and month.isdigit():
                        available_dates.append(item)
                except:
                    continue
    
    # 按日期排序，最新的在前面
    available_dates.sort(reverse=True)
    return available_dates


def get_current_date() -> str:
    """
    获取当前日期，格式为 YYYY.MM
    
    Returns:
        str: 当前日期字符串
    """
    now = datetime.now()
    return f"{now.year}.{now.month:02d}"
