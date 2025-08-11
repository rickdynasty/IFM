"""
股票数据工厂类
负责创建和管理不同类型的StockData实例
"""

import os
from typing import Dict, Optional, Any, List
from .stock_data import StockData


class StockDataFactory:
    """股票数据工厂类，负责创建和管理StockData实例"""
    
    # 股票数据类型定义
    STOCK_DATA_TYPES = {
        '北上资金持股': {
            'file': 'The_highest_proportion_of_northbound_funds_held.csv',
            'sub_types': None,
            'date_dependent': True,  # 依赖日期文件夹
            'extra_columns': {
                '持有市值': '持有市值.亿',
                '持股比': '持股比'
            },
            'display_name': '北上持股排名'
        },
        '热门股票': {
            'file_pattern': 'Hot_stocks_in_the_past_{}.csv',
            'sub_types': {
                '近1天': 'day',
                '近3天': 'three_days', 
                '近1周': 'week',
                '近1月': 'month',
                '近3月': 'three_months',
                '近6月': 'six_months',
                '近1年': 'year',
                '近3年': 'three_years'
            },
            'date_dependent': True,  # 依赖日期文件夹
            'extra_columns': {
                '关注度': '关注度'
            }
        },
        '最便宜股票': {
            'file_pattern': 'The_cheapest_{}.csv',
            'sub_types': {
                '全部': 'stocks',
                '不包括周期性股票': 'non-cyclical_stocks',
                '不包括银行股': 'non-bank_stocks',
                '不包括周期性股票和银行股': 'non-cyclical_non-bank_stocks'
            },
            'date_dependent': True,  # 依赖日期文件夹
            'extra_columns': {
                '便宜指数': '便宜指数'
            }
        },
        'ROE排名': {
            'file': 'Highest_ROE_ranking.csv',
            'sub_types': None,
            'date_dependent': True,  # 依赖日期文件夹
            'extra_columns': {
                'ROE': 'ROE'
            },
            'display_name': 'ROE最高'
        },
        'ROE连续超15%': {
            'file_pattern': 'ROE_exceeded_15p_{}_consecutive_years.csv',
            'sub_types': {
                '连续3年': 'three',
                '连续5年': 'five'
            },
            'date_dependent': True,  # 依赖日期文件夹
            'extra_columns': {
                '平均ROE': 'ROE',
                '北上持股': '北上持股'
            }
        },
        'PEG排名': {
            'file_pattern': 'PEG_ranking_in_the_past_{}.csv',
            'sub_types': {
                '近1年': 'year',
                '近3年': 'three_years',
                '近5年': 'five_years'
            },
            'date_dependent': True,  # 依赖日期文件夹
            'extra_columns': {
                'PEG': 'PEG'
            }
        },
        '股息率排名': {
            'file_pattern': 'Highest_dividend_yield_in_the_past_{}.csv',
            'sub_types': {
                '近2年': 'two_years',
                '近3年': 'three_years',
                '近5年': 'five_years'
            },
            'date_dependent': True,  # 依赖日期文件夹
            'extra_columns': {
                '平均股息': '平均股息'  # 修正列名，去掉空格
            }
        },
        '控盘度排名': {
            'file': 'Strongest_control_top200.txt',
            'sub_types': None,
            'date_dependent': True,  # 依赖日期文件夹
            'extra_columns': {
                '控盘度': '控盘度'
            }
        },
        '股东数最少排名': {
            'file': 'The_lowest_shareholders_in_history_top200.txt',
            'sub_types': None,
            'date_dependent': True,  # 依赖日期文件夹
            'extra_columns': {
                '股东数': '股东数.人'
            }
        },
        '基金重仓股': {
            'file_pattern': 'Fund_holdings_ranking_{}.csv',
            'sub_types': {
                '2025Q2': '2025Q2',
                '2025Q1': '2025Q1',
                '2024Q4': '2024Q4',
                '2024Q3': '2024Q3',
                '2024Q2': '2024Q2'
            },
            'date_dependent': False,  # 不依赖日期文件夹，在根目录
            'extra_columns': {
                '占总股本': '基金总持有'
            }
        },
        '券商研报推荐': {
            'file_pattern': 'Research_report_recommends_hot_stocks_in_the_past_{}.csv',
            'sub_types': {
                '近1周': 'week',
                '近3周': 'three_weeks',
                '近2月': 'two_months',
                '近6月': 'six_months',
                '近1年': 'year'
            },
            'date_dependent': True,  # 依赖日期文件夹
            'extra_columns': {
                '推荐数': '推荐数'
            }
        }
    }
    
    @classmethod
    def get_stock_data(cls, stock_type: str, sub_type: Optional[str] = None, 
                      data_dir: str = None, selected_date: str = None) -> Optional[StockData]:
        """
        获取特定类型的StockData实例
        
        Args:
            stock_type: 股票类型
            sub_type: 子类型
            data_dir: 数据根目录
            selected_date: 选择的日期
            
        Returns:
            StockData: StockData实例，如果类型不支持则返回None
        """
        if stock_type not in cls.STOCK_DATA_TYPES:
            print(f"不支持的股票类型: {stock_type}")
            return None
        
        config = cls.STOCK_DATA_TYPES[stock_type]
        
        # 确定数据目录
        if data_dir is None:
            data_dir = os.path.join('data', 'stock')
        
        if selected_date and config['date_dependent']:
            full_data_dir = os.path.join(data_dir, selected_date)
        else:
            full_data_dir = data_dir
        
        # 创建并返回StockData实例
        return StockData(
            data_dir=full_data_dir,
            stock_type=stock_type,
            sub_type=sub_type,
            config=config,
            date_dependent=config['date_dependent']
        )
    
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
            config = cls.STOCK_DATA_TYPES[stock_type]
            if 'sub_types' in config and config['sub_types']:
                return list(config['sub_types'].keys())
        return []
