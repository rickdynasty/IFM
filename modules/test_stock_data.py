"""
测试股票数据模块的功能
"""

import pandas as pd
import os
import sys
from typing import Dict, List, Set, Optional, Any

# 添加上级目录到路径中
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.stock_data import StockDataManager, StockDataFactory


def test_stock_data_loading():
    """测试股票数据加载"""
    print("===== 测试股票数据加载 =====")
    
    # 获取最新日期
    from modules.stock_filter_new import get_current_date
    current_date = get_current_date()
    print(f"当前日期: {current_date}")
    
    # 获取所有股票类型
    stock_types = StockDataFactory.get_all_stock_types()
    print(f"支持的股票类型: {stock_types}")
    
    # 创建数据管理器
    data_manager = StockDataManager(selected_date=current_date)
    
    # 测试加载北上资金持股数据
    print("\n加载北上资金持股数据...")
    success = data_manager.load_stock_data('北上资金持股')
    print(f"加载成功: {success}")
    
    if success:
        # 获取股票代码
        instance_key = "北上资金持股"
        stock_data = data_manager.stock_data_instances[instance_key]
        stock_codes = stock_data.stock_codes
        print(f"股票数量: {len(stock_codes)}")
        print(f"前5个股票代码: {list(stock_codes)[:5]}")
        
        # 查看额外列数据
        extra_data = stock_data.extra_data
        print(f"额外列: {list(extra_data.keys())}")
        
        # 查看第一个股票的信息
        if stock_codes:
            first_code = list(stock_codes)[0]
            info = stock_data.stock_info.get(first_code, {})
            print(f"股票 {first_code} 信息: {info}")


def test_stock_filtering():
    """测试股票筛选功能"""
    print("\n===== 测试股票筛选 =====")
    
    # 获取最新日期
    from modules.stock_filter_new import get_current_date
    current_date = get_current_date()
    
    # 创建数据管理器
    data_manager = StockDataManager(selected_date=current_date)
    
    # 测试筛选ROE连续超15%的股票
    selected_types = ['ROE连续超15%']
    sub_types = {'ROE连续超15%': '连续3年'}
    
    print(f"筛选类型: {selected_types}, 子类型: {sub_types}")
    result = data_manager.filter_stocks(
        selected_types=selected_types,
        sub_types=sub_types
    )
    
    print(f"筛选结果数量: {len(result)}")
    if not result.empty:
        print("结果字段: ", result.columns.tolist())
        print("前3条结果:")
        print(result.head(3))
    
    # 测试ROE筛选
    print("\n添加ROE筛选(>= 12%)...")
    result_roe = data_manager.filter_stocks(
        selected_types=selected_types,
        sub_types=sub_types,
        roe_filter=12.0
    )
    print(f"筛选结果数量: {len(result_roe)}")
    
    # 测试股息筛选
    print("\n添加股息筛选(>= 3%)...")
    result_dividend = data_manager.filter_stocks(
        selected_types=selected_types,
        sub_types=sub_types,
        dividend_filter=3.0
    )
    print(f"筛选结果数量: {len(result_dividend)}")
    
    # 测试多条件筛选
    print("\n测试多条件筛选...")
    result_multiple = data_manager.filter_stocks(
        selected_types=['ROE连续超15%', '股息率排名'],
        sub_types={'ROE连续超15%': '连续3年', '股息率排名': '近3年'},
        roe_filter=10.0,
        dividend_filter=3.0
    )
    print(f"多条件筛选结果数量: {len(result_multiple)}")
    if not result_multiple.empty:
        print("结果字段: ", result_multiple.columns.tolist())
        print("前3条结果:")
        print(result_multiple.head(3))


def test_compare_with_original():
    """与原始筛选模块比较结果"""
    print("\n===== 与原始模块比较 =====")
    
    # 导入原始和新的筛选函数
    from modules.stock_filter import stock_filter as original_filter
    from modules.stock_filter_new import stock_filter as new_filter
    
    # 获取最新日期
    from modules.stock_filter_new import get_current_date
    current_date = get_current_date()
    
    # 测试参数
    selected_types = ['ROE连续超15%']
    sub_types = {'ROE连续超15%': '连续3年'}
    
    # 使用原始函数筛选
    print("使用原始函数筛选...")
    original_result = original_filter(
        selected_types=selected_types,
        sub_types=sub_types,
        selected_date=current_date
    )
    print(f"原始函数结果数量: {len(original_result)}")
    
    # 使用新函数筛选
    print("使用新函数筛选...")
    new_result = new_filter(
        selected_types=selected_types,
        sub_types=sub_types,
        selected_date=current_date
    )
    print(f"新函数结果数量: {len(new_result)}")
    
    # 比较结果
    if not original_result.empty and not new_result.empty:
        # 排序后比较股票代码
        original_codes = set(original_result['股票代码'].tolist())
        new_codes = set(new_result['股票代码'].tolist())
        
        common_codes = original_codes.intersection(new_codes)
        original_only = original_codes - new_codes
        new_only = new_codes - original_codes
        
        print(f"共同股票数: {len(common_codes)}")
        print(f"仅原始函数: {len(original_only)}")
        print(f"仅新函数: {len(new_only)}")
        
        if original_only:
            print(f"仅原始函数股票示例: {list(original_only)[:5]}")
        
        if new_only:
            print(f"仅新函数股票示例: {list(new_only)[:5]}")


if __name__ == "__main__":
    # 运行测试
    test_stock_data_loading()
    test_stock_filtering()
    test_compare_with_original()
