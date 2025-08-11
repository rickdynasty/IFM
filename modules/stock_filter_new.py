"""
股票筛选模块 - 使用面向对象框架的新实现
提供股票数据的筛选功能
"""

import pandas as pd
from typing import Dict, List, Set, Optional, Any

from .stock_data import StockDataManager, StockDataFactory
from .stock_data.utils import get_available_dates, get_current_date


def stock_filter(selected_types=None, sub_types=None, industry_filter=None, 
                selected_date=None, roe_filter=None, dividend_filter=None):
    """
    股票筛选函数 - 使用面向对象的数据管理方式
    
    Args:
        selected_types: 选择的股票类型列表
        sub_types: 每种类型选择的子类型
        industry_filter: 行业筛选条件
        selected_date: 选择的日期，格式为 "YYYY.MM"，如果为None则使用当前日期
        roe_filter: ROE筛选阈值，如8表示筛选ROE大于等于8%的股票
        dividend_filter: 股息率筛选阈值，如3表示筛选股息率大于等于3%的股票
    """
    if selected_types is None:
        selected_types = []
    if sub_types is None:
        sub_types = {}
    if industry_filter is None:
        industry_filter = []
    
    # 如果没有指定日期，使用当前日期
    if selected_date is None:
        selected_date = get_current_date()
    
    # 创建StockDataManager实例
    data_manager = StockDataManager(selected_date=selected_date)
    
    # 筛选股票
    result_df = data_manager.filter_stocks(
        selected_types=selected_types,
        sub_types=sub_types,
        industry_filter=industry_filter,
        roe_filter=roe_filter,
        dividend_filter=dividend_filter
    )
    
    return result_df


def get_stock_type_options():
    """获取股票类型选项"""
    return StockDataFactory.get_all_stock_types()


def get_sub_type_options(stock_type):
    """获取指定股票类型的子类型选项"""
    return StockDataFactory.get_sub_types(stock_type)


def get_industry_options(selected_date=None):
    """获取所有可用行业选项"""
    # 创建临时数据管理器
    data_manager = StockDataManager(selected_date=selected_date)
    
    # 获取所有股票类型
    stock_types = StockDataFactory.get_all_stock_types()
    
    # 加载至少一个类型的数据，以获取行业信息
    for stock_type in stock_types:
        # 尝试加载数据
        if data_manager.load_stock_data(stock_type):
            break
    
    # 获取行业列表
    return data_manager.get_available_industries()
