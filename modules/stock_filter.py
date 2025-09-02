"""
股票筛选模块
提供股票数据的筛选功能，使用面向对象的数据管理方式
"""

import pandas as pd
from typing import Dict, List, Set, Optional, Any, Union

from .stock_data.stock_data_manager import StockDataManager
from .stock_data.stock_data_factory import StockDataFactory
from .utils import get_available_dates, get_current_date


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
        
    Returns:
        pd.DataFrame: 筛选结果
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


def search_stock(search_term: str, selected_date: Optional[str] = None) -> Dict[str, Any]:
    """
    搜索股票
    
    Args:
        search_term: 搜索条件，股票代码或名称
        selected_date: 选择的日期，格式为 "YYYY.MM"，如果为None则使用当前日期
        
    Returns:
        Dict: 搜索结果，包含股票基本信息和所属分类
    """
    # 如果没有指定日期，使用当前日期
    if selected_date is None:
        selected_date = get_current_date()
    
    # 创建StockDataManager实例
    data_manager = StockDataManager(selected_date=selected_date)
    
    # 尝试直接加载常用类型以找到股票代码
    initial_types = ['北上资金持股', 'ROE排名', '热门股票']
    stock_code = None
    stock_name = None
    stock_info = None
    
    for stock_type in initial_types:
        if stock_type == '热门股票':
            data_manager.load_stock_data(stock_type, '近1天')
        else:
            data_manager.load_stock_data(stock_type)
            
        # 查找股票代码和名称
        for code, info in data_manager.all_stock_info.items():
            name = info.get('名称', '')
            
            if (search_term == code or 
                (name and search_term == name) or 
                (name and search_term in name)):
                stock_code = code
                stock_name = name
                stock_info = info.copy()
                stock_info['股票代码'] = code
                break
                
        if stock_code:
            break
    
    if not stock_code:
        return {'stock_info': None, 'categories': []}
    
    # 查找股票所属的分类
    categories = []
    
    # 先清理数据缓存
    data_manager.stock_data_instances.clear()
    data_manager.filtered_codes.clear()
    
    # 检查每种股票类型
    for stock_type, stock_data_dict in StockDataFactory.STOCK_DATA_TYPES.items():
        if stock_data_dict.get('has_sub_types', False):
            # 处理有子类型的情况
            sub_types = StockDataFactory.get_sub_types(stock_type)
            for sub_type in sub_types:
                # 每次都清除缓存并重新加载数据
                instance_key = f"{stock_type}_{sub_type}"
                if instance_key in data_manager.stock_data_instances:
                    del data_manager.stock_data_instances[instance_key]
                if instance_key in data_manager.filtered_codes:
                    del data_manager.filtered_codes[instance_key]
                
                # 加载数据
                success = data_manager.load_stock_data(stock_type, sub_type)
                
                # 检查股票是否在此分类中
                if success and instance_key in data_manager.filtered_codes:
                    if stock_code in data_manager.filtered_codes[instance_key]:
                        category_name = f"{stock_type} - {sub_type}"
                        categories.append(category_name)
        else:
            # 处理没有子类型的情况
            # 每次都清除缓存并重新加载数据
            if stock_type in data_manager.stock_data_instances:
                del data_manager.stock_data_instances[stock_type]
            if stock_type in data_manager.filtered_codes:
                del data_manager.filtered_codes[stock_type]
            
            # 加载数据
            success = data_manager.load_stock_data(stock_type)
            
            # 检查股票是否在此分类中
            if success and stock_type in data_manager.filtered_codes:
                if stock_code in data_manager.filtered_codes[stock_type]:
                    categories.append(stock_type)
    
    # 返回结果
    return {
        'stock_info': stock_info,
        'categories': categories
    }


def get_stock_type_options() -> List[str]:
    """
    获取股票类型选项
    
    Returns:
        List[str]: 可用的股票类型列表
    """
    return StockDataFactory.get_all_stock_types()


def get_sub_type_options(stock_type: str) -> List[str]:
    """
    获取指定股票类型的子类型选项
    
    Args:
        stock_type: 股票类型名称
        
    Returns:
        List[str]: 子类型选项列表
    """
    return StockDataFactory.get_sub_types(stock_type)


def get_industry_options(selected_date: Optional[str] = None) -> List[str]:
    """
    获取所有可用行业选项
    
    Args:
        selected_date: 选择的日期，格式为 "YYYY.MM"，如果为None则使用当前日期
        
    Returns:
        List[str]: 可用的行业列表
    """
    # 如果没有指定日期，使用当前日期
    if selected_date is None:
        selected_date = get_current_date()
    
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


def get_stock_display_name(stock_type: str) -> str:
    """
    获取股票类型的显示名称
    
    Args:
        stock_type: 股票类型
        
    Returns:
        str: 显示名称
    """
    return StockDataFactory.get_display_name(stock_type)