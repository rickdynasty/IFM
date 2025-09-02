"""
股票数据工厂类
负责创建和管理不同类型的股票数据实例
"""

import os
from typing import Dict, Optional, Any, List
from .base_stock_data import BaseStockData
from .stock_data_types import (
    NorthboundStockData,
    HotStockData,
    CheapestStockData,
    ROERankingStockData,
    ROEConsecutiveStockData,
    PEGRankingStockData,
    DividendYieldStockData,
    ControlRankingStockData,
    ShareholderCountStockData,
    FundHoldingStockData,
    ResearchReportStockData,
    FreeCashFlowStockData,
    DiscountedFreeCashFlowStockData
)


class StockDataFactory:
    """股票数据工厂类，负责创建和管理不同类型的股票数据实例"""
    
    # 股票数据类型定义
    STOCK_DATA_TYPES = {
        '北上资金持股': {
            'display_name': '北上持股排名',
            'has_sub_types': False
        },
        '热门股票': {
            'sub_types': [
                '近1天',
                '近3天', 
                '近1周',
                '近1月',
                '近3月',
                '近6月',
                '近1年',
                '近3年'
            ],
            'has_sub_types': True
        },
        '最便宜股票': {
            'sub_types': [
                '全部',
                '不包括周期性股票',
                '不包括银行股',
                '不包括周期性股票和银行股'
            ],
            'has_sub_types': True
        },
        'ROE排名': {
            'display_name': 'ROE最高',
            'has_sub_types': False
        },
        'ROE连续超15%': {
            'sub_types': [
                '连续3年',
                '连续5年'
            ],
            'has_sub_types': True
        },
        'PEG排名': {
            'sub_types': [
                '近1年',
                '近3年',
                '近5年'
            ],
            'has_sub_types': True
        },
        '股息率排名': {
            'sub_types': [
                '近2年',
                '近3年',
                '近5年'
            ],
            'has_sub_types': True
        },
        '控盘度排名': {
            'has_sub_types': False
        },
        '股东数最少排名': {
            'has_sub_types': False
        },
        '自由现金流排名': {
            'has_sub_types': False
        },
        '自由现金流折现排名': {
            'has_sub_types': False
        },
        '基金重仓股': {
            'sub_types': [
                '2025Q2',
                '2025Q1',
                '2024Q4',
                '2024Q3',
                '2024Q2'
            ],
            'has_sub_types': True
        },
        '券商研报推荐': {
            'sub_types': [
                '近1周',
                '近3周',
                '近2月',
                '近6月',
                '近1年'
            ],
            'has_sub_types': True
        }
    }
    
    @classmethod
    def get_stock_data(cls, stock_type: str, sub_type: Optional[str] = None, 
                      data_dir: str = None, selected_date: str = None) -> Optional[BaseStockData]:
        """
        获取特定类型的股票数据实例
        
        Args:
            stock_type: 股票类型
            sub_type: 子类型
            data_dir: 数据根目录
            selected_date: 选择的日期
            
        Returns:
            BaseStockData: 股票数据实例，如果类型不支持则返回None
        """
        if stock_type not in cls.STOCK_DATA_TYPES:
            print(f"不支持的股票类型: {stock_type}")
            return None
        
        # 确定数据目录
        if data_dir is None:
            data_dir = os.path.join('data', 'stock')
        
        # 如果有日期，添加到路径中
        if selected_date:
            full_data_dir = os.path.join(data_dir, selected_date)
        else:
            full_data_dir = data_dir
        
        # 根据股票类型创建对应的实例
        if stock_type == '北上资金持股':
            return NorthboundStockData(full_data_dir)
            
        elif stock_type == '热门股票':
            if not sub_type:
                sub_type = cls.STOCK_DATA_TYPES[stock_type]['sub_types'][0]
            return HotStockData(full_data_dir, sub_type)
            
        elif stock_type == '最便宜股票':
            if not sub_type:
                sub_type = cls.STOCK_DATA_TYPES[stock_type]['sub_types'][0]
            return CheapestStockData(full_data_dir, sub_type)
            
        elif stock_type == 'ROE排名':
            return ROERankingStockData(full_data_dir)
            
        elif stock_type == 'ROE连续超15%':
            if not sub_type:
                sub_type = cls.STOCK_DATA_TYPES[stock_type]['sub_types'][0]
            return ROEConsecutiveStockData(full_data_dir, sub_type)
            
        elif stock_type == 'PEG排名':
            if not sub_type:
                sub_type = cls.STOCK_DATA_TYPES[stock_type]['sub_types'][0]
            return PEGRankingStockData(full_data_dir, sub_type)
            
        elif stock_type == '股息率排名':
            if not sub_type:
                sub_type = cls.STOCK_DATA_TYPES[stock_type]['sub_types'][0]
            return DividendYieldStockData(full_data_dir, sub_type)
            
        elif stock_type == '控盘度排名':
            return ControlRankingStockData(full_data_dir)
            
        elif stock_type == '股东数最少排名':
            return ShareholderCountStockData(full_data_dir)
            
        elif stock_type == '基金重仓股':
            if not sub_type:
                sub_type = cls.STOCK_DATA_TYPES[stock_type]['sub_types'][0]
            return FundHoldingStockData(data_dir, sub_type)  # 注意这里用原始data_dir
            
        elif stock_type == '券商研报推荐':
            if not sub_type:
                sub_type = cls.STOCK_DATA_TYPES[stock_type]['sub_types'][0]
            return ResearchReportStockData(full_data_dir, sub_type)
            
        elif stock_type == '自由现金流排名':
            return FreeCashFlowStockData(full_data_dir)
            
        elif stock_type == '自由现金流折现排名':
            return DiscountedFreeCashFlowStockData(full_data_dir)
            
        return None
    
    @classmethod
    def get_all_stock_types(cls) -> List[str]:
        """
        获取所有支持的股票类型
        
        Returns:
            List[str]: 股票类型列表
        """
        return list(cls.STOCK_DATA_TYPES.keys())
    
    @classmethod
    def get_sub_types(cls, stock_type: str) -> List[str]:
        """
        获取指定股票类型的子类型
        
        Args:
            stock_type: 股票类型
            
        Returns:
            List[str]: 子类型列表，如果没有子类型则返回空列表
        """
        if stock_type in cls.STOCK_DATA_TYPES:
            if cls.STOCK_DATA_TYPES[stock_type].get('has_sub_types', False):
                return cls.STOCK_DATA_TYPES[stock_type].get('sub_types', [])
        return []
    
    @classmethod
    def get_display_name(cls, stock_type: str) -> str:
        """
        获取股票类型的显示名称
        
        Args:
            stock_type: 股票类型
            
        Returns:
            str: 显示名称
        """
        if stock_type in cls.STOCK_DATA_TYPES:
            return cls.STOCK_DATA_TYPES[stock_type].get('display_name', stock_type)
        return stock_type