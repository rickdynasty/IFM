"""
具体股票数据类型实现
基于不同数据源和股票类型的特定实现
"""

import os
import pandas as pd
from typing import Dict, Optional, Any, List
from .base_stock_data import BaseStockData


class NorthboundStockData(BaseStockData):
    """北上资金持股数据"""
    
    def __init__(self, data_dir: str):
        super().__init__(data_dir, date_dependent=True)
        self.file_name = 'The_highest_proportion_of_northbound_funds_held.csv'
    
    def _determine_file_path(self) -> str:
        path = os.path.join(self.data_dir, self.file_name)
        
        return path
    
    def _extract_extra_data(self, df: pd.DataFrame, code_column: str) -> None:
        # 北上资金特有的额外列
        extra_columns = {
            '持股比': '持股比',
            '持有市值': '持有市值.亿',
        }
        
        for display_name, source_column in extra_columns.items():
            if display_name not in self.extra_data:
                self.extra_data[display_name] = {}
            
            if source_column in df.columns:
                for _, row in df.iterrows():
                    try:
                        code = self.clean_code(row[code_column])
                        if code and pd.notna(row[source_column]):
                            self.extra_data[display_name][code] = str(row[source_column]).strip()
                    except Exception:
                        pass


class HotStockData(BaseStockData):
    """热门股票数据"""
    
    def __init__(self, data_dir: str, time_period: str):
        super().__init__(data_dir, date_dependent=True)
        self.time_period = time_period
        self.period_mapping = {
            '近1天': 'day',
            '近3天': 'three_days',
            '近1周': 'week',
            '近1月': 'month',
            '近3月': 'three_months',
            '近6月': 'six_months',
            '近1年': 'year',
            '近3年': 'three_years'
        }
        self.file_pattern = 'Hot_stocks_in_the_past_{}.csv'
    
    def _determine_file_path(self) -> str:
        if self.time_period in self.period_mapping:
            period_value = self.period_mapping[self.time_period]
            path = os.path.join(self.data_dir, self.file_pattern.format(period_value))
            
            return path
        return ""
    
    def _extract_extra_data(self, df: pd.DataFrame, code_column: str) -> None:
        extra_columns = {
            '关注度': '关注度',
            'PE.扣非': '扣非PE',
            '北上持股': '北上持股'
        }
        
        for display_name, source_column in extra_columns.items():
            if display_name not in self.extra_data:
                self.extra_data[display_name] = {}
            
            if source_column in df.columns:
                for _, row in df.iterrows():
                    try:
                        code = self.clean_code(row[code_column])
                        if code and pd.notna(row[source_column]):
                            self.extra_data[display_name][code] = str(row[source_column]).strip()
                    except Exception:
                        pass


class CheapestStockData(BaseStockData):
    """最便宜股票数据"""
    
    def __init__(self, data_dir: str, stock_filter: str):
        super().__init__(data_dir, date_dependent=True)
        self.stock_filter = stock_filter
        self.filter_mapping = {
            '全部': 'stocks',
            '不包括周期性股票': 'non-cyclical_stocks',
            '不包括银行股': 'non-bank_stocks',
            '不包括周期性股票和银行股': 'non-cyclical_non-bank_stocks'
        }
        self.file_pattern = 'The_cheapest_{}.csv'
    
    def _determine_file_path(self) -> str:
        if self.stock_filter in self.filter_mapping:
            filter_value = self.filter_mapping[self.stock_filter]
            path = os.path.join(self.data_dir, self.file_pattern.format(filter_value))
            
            return path
        return ""
    
    def _extract_extra_data(self, df: pd.DataFrame, code_column: str) -> None:
        extra_columns = {
            '便宜指数': '便宜指数',
            '北上持股': '北上持股',
            'PE.扣非': 'PE.扣非',
            'PE.TTM': 'PE.TTM'
        }
        
        for display_name, source_column in extra_columns.items():
            if display_name not in self.extra_data:
                self.extra_data[display_name] = {}
            
            if source_column in df.columns:
                for _, row in df.iterrows():
                    try:
                        code = self.clean_code(row[code_column])
                        if code and pd.notna(row[source_column]):
                            self.extra_data[display_name][code] = str(row[source_column]).strip()
                    except Exception:
                        pass


class ROERankingStockData(BaseStockData):
    """ROE排名股票数据"""
    
    def __init__(self, data_dir: str):
        super().__init__(data_dir, date_dependent=True)
        self.file_name = 'Highest_ROE_ranking.csv'
    
    def _determine_file_path(self) -> str:
        path = os.path.join(self.data_dir, self.file_name)
        
        return path
    
    def _extract_extra_data(self, df: pd.DataFrame, code_column: str) -> None:
        extra_columns = {
            'ROE': 'ROE',
            'PE.扣非': '扣非PE'
        }
        
        for display_name, source_column in extra_columns.items():
            if display_name not in self.extra_data:
                self.extra_data[display_name] = {}
            
            if source_column in df.columns:
                for _, row in df.iterrows():
                    try:
                        code = self.clean_code(row[code_column])
                        if code and pd.notna(row[source_column]):
                            self.extra_data[display_name][code] = str(row[source_column]).strip()
                    except Exception:
                        pass


class ROEConsecutiveStockData(BaseStockData):
    """ROE连续超15%股票数据"""
    
    def __init__(self, data_dir: str, years: str):
        super().__init__(data_dir, date_dependent=True)
        self.years = years
        self.years_mapping = {
            '连续3年': 'three',
            '连续5年': 'five'
        }
        self.file_pattern = 'ROE_exceeded_15p_{}_consecutive_years.csv'
    
    def _determine_file_path(self) -> str:
        if self.years in self.years_mapping:
            years_value = self.years_mapping[self.years]
            path = os.path.join(self.data_dir, self.file_pattern.format(years_value))
            
            # 检查文件是否存在，如果不存在尝试其他可能的路径
            if not os.path.exists(path):
                
                # 尝试不同格式的文件名
                alt_pattern = "ROE_exceeded_15p_{}consecutive_years.csv"  # 移除下划线
                alt_path = os.path.join(self.data_dir, alt_pattern.format(years_value + "_"))
                
                if os.path.exists(alt_path):
                    return alt_path
                
                # 尝试直接名称
                direct_pattern = "ROE连续超15%{}年.csv"
                direct_path = os.path.join(self.data_dir, direct_pattern.format("三" if years_value == "three" else "五"))
                
                if os.path.exists(direct_path):
                    return direct_path
            else:
                return path
        
        return ""
    
    def _extract_extra_data(self, df: pd.DataFrame, code_column: str) -> None:
        # ROE连续超15%特有的额外列处理
        self._extract_roe_data(df, code_column)
        self._extract_northbound_data(df, code_column)
    
    def _extract_roe_data(self, df: pd.DataFrame, code_column: str) -> None:
        """提取ROE数据的特殊处理"""
        display_name = '平均ROE'
        if display_name not in self.extra_data:
            self.extra_data[display_name] = {}
        
        # 尝试多种可能的ROE列名
        roe_columns = ['ROE', 'roe', '平均ROE', '平均roe', 'ROE(%)', 'roe(%)', '平均ROE(%)', '平均roe(%)']
        
        # 查找匹配的列
        found_column = next((col for col in roe_columns if col in df.columns), None)
        
        if found_column:
            
            for _, row in df.iterrows():
                try:
                    code = self.clean_code(row[code_column])
                    if code and pd.notna(row[found_column]):
                        self.extra_data[display_name][code] = str(row[found_column]).strip()
                except Exception:
                    pass
        else:
            
            # 如果找不到ROE列，使用当前ROE数据
            for code in self.stock_codes:
                if code in self.stock_info and '当前ROE' in self.stock_info[code]:
                    self.extra_data[display_name][code] = self.stock_info[code]['当前ROE']
    
    def _extract_northbound_data(self, df: pd.DataFrame, code_column: str) -> None:
        """提取北上持股数据的特殊处理"""
        display_name = '北上持股'
        if display_name not in self.extra_data:
            self.extra_data[display_name] = {}
        
        if '北上持股' in df.columns:
            for _, row in df.iterrows():
                try:
                    code = self.clean_code(row[code_column])
                    if code and pd.notna(row['北上持股']):
                        self.extra_data[display_name][code] = str(row['北上持股']).strip()
                except Exception:
                    pass
        else:
            # 如果找不到北上持股列，默认标记为"否"
            for code in self.stock_codes:
                self.extra_data[display_name][code] = '否'


class PEGRankingStockData(BaseStockData):
    """PEG排名股票数据"""
    
    def __init__(self, data_dir: str, time_period: str):
        super().__init__(data_dir, date_dependent=True)
        self.time_period = time_period
        self.period_mapping = {
            '近1年': 'year',
            '近3年': 'three_years',
            '近5年': 'five_years'
        }
        self.file_pattern = 'PEG_ranking_in_the_past_{}.csv'
    
    def _determine_file_path(self) -> str:
        if self.time_period in self.period_mapping:
            period_value = self.period_mapping[self.time_period]
            path = os.path.join(self.data_dir, self.file_pattern.format(period_value))
            
            return path
        return ""
    
    def _extract_extra_data(self, df: pd.DataFrame, code_column: str) -> None:
        extra_columns = {
            'PEG': 'PEG',
            'PE.扣非': 'PE.扣非',
            '预测增速': '预测增速',
            '北上持股': '北上持股'
        }
        
        for display_name, source_column in extra_columns.items():
            if display_name not in self.extra_data:
                self.extra_data[display_name] = {}
            
            if source_column in df.columns:
                for _, row in df.iterrows():
                    try:
                        code = self.clean_code(row[code_column])
                        if code and pd.notna(row[source_column]):
                            self.extra_data[display_name][code] = str(row[source_column]).strip()
                    except Exception:
                        pass


class DividendYieldStockData(BaseStockData):
    """股息率排名股票数据"""
    
    def __init__(self, data_dir: str, time_period: str):
        super().__init__(data_dir, date_dependent=True)
        self.time_period = time_period
        self.period_mapping = {
            '近2年': 'two_years',
            '近3年': 'three_years',
            '近5年': 'five_years'
        }
        self.file_pattern = 'Highest_dividend_yield_in_the_past_{}.csv'
    
    def _determine_file_path(self) -> str:
        if self.time_period in self.period_mapping:
            period_value = self.period_mapping[self.time_period]
            path = os.path.join(self.data_dir, self.file_pattern.format(period_value))
            
            return path
        return ""
    
    def _extract_extra_data(self, df: pd.DataFrame, code_column: str) -> None:
        extra_columns = {
            '股息率': '最新股息',
            '平均股息': '平均股息'
        }
        
        for display_name, source_column in extra_columns.items():
            if display_name not in self.extra_data:
                self.extra_data[display_name] = {}
            
            if source_column in df.columns:
                for _, row in df.iterrows():
                    try:
                        code = self.clean_code(row[code_column])
                        if code and pd.notna(row[source_column]):
                            self.extra_data[display_name][code] = str(row[source_column]).strip()
                    except Exception:
                        pass


class ControlRankingStockData(BaseStockData):
    """控盘度排名股票数据"""
    
    def __init__(self, data_dir: str):
        super().__init__(data_dir, date_dependent=True)
        self.file_name = 'Strongest_control_top200.txt'
    
    def _determine_file_path(self) -> str:
        path = os.path.join(self.data_dir, self.file_name)
        
        return path
    
    def _extract_extra_data(self, df: pd.DataFrame, code_column: str) -> None:
        extra_columns = {
            '控盘度': '控盘度',
            '北上持股': '北上持股',
            'PE.扣非': '扣非PE'
        }
        
        for display_name, source_column in extra_columns.items():
            if display_name not in self.extra_data:
                self.extra_data[display_name] = {}
            
            if source_column in df.columns:
                for _, row in df.iterrows():
                    try:
                        code = self.clean_code(row[code_column])
                        if code and pd.notna(row[source_column]):
                            self.extra_data[display_name][code] = str(row[source_column]).strip()
                    except Exception:
                        pass


class ShareholderCountStockData(BaseStockData):
    """股东数最少排名股票数据"""
    
    def __init__(self, data_dir: str):
        super().__init__(data_dir, date_dependent=True)
        self.file_name = 'The_lowest_shareholders_in_history_top200.txt'
    
    def _determine_file_path(self) -> str:
        path = os.path.join(self.data_dir, self.file_name)
        
        return path
    
    def _extract_extra_data(self, df: pd.DataFrame, code_column: str) -> None:
        extra_columns = {
            '股东数': '股东数.人',
            '北上持股': '北上持股',
            'PE.扣非': '扣非PE'
        }
        
        for display_name, source_column in extra_columns.items():
            if display_name not in self.extra_data:
                self.extra_data[display_name] = {}
            
            if source_column in df.columns:
                for _, row in df.iterrows():
                    try:
                        code = self.clean_code(row[code_column])
                        if code and pd.notna(row[source_column]):
                            self.extra_data[display_name][code] = str(row[source_column]).strip()
                    except Exception:
                        pass


class FundHoldingStockData(BaseStockData):
    """基金持仓股票数据"""
    
    def __init__(self, data_dir: str, quarter: str):
        super().__init__(data_dir, date_dependent=False)
        self.quarter = quarter
        self.file_pattern = 'Fund_holdings_ranking_{}.csv'
    
    def _determine_file_path(self) -> str:
        # 基金持仓数据文件在根目录，不依赖日期
        path = os.path.join('data', 'stock', self.file_pattern.format(self.quarter))
        
        return path
    
    def _extract_extra_data(self, df: pd.DataFrame, code_column: str) -> None:
        extra_columns = {
            '占总股本': '占总股本'
        }
        
        for display_name, source_column in extra_columns.items():
            if display_name not in self.extra_data:
                self.extra_data[display_name] = {}
            
            if source_column in df.columns:
                for _, row in df.iterrows():
                    try:
                        code = self.clean_code(row[code_column])
                        if code and pd.notna(row[source_column]):
                            self.extra_data[display_name][code] = str(row[source_column]).strip()
                    except Exception:
                        pass


class ResearchReportStockData(BaseStockData):
    """券商研报推荐股票数据"""
    
    def __init__(self, data_dir: str, time_period: str):
        super().__init__(data_dir, date_dependent=True)
        self.time_period = time_period
        self.period_mapping = {
            '近1周': 'week',
            '近3周': 'three_weeks',
            '近2月': 'two_months',
            '近6月': 'six_months',
            '近1年': 'year'
        }
        self.file_pattern = 'Research_report_recommends_hot_stocks_in_the_past_{}.csv'
    
    def _determine_file_path(self) -> str:
        if self.time_period in self.period_mapping:
            period_value = self.period_mapping[self.time_period]
            path = os.path.join(self.data_dir, self.file_pattern.format(period_value))
            
            return path
        return ""
    
    def _extract_extra_data(self, df: pd.DataFrame, code_column: str) -> None:
        extra_columns = {
            '推荐数': '推荐数'
        }
        
        for display_name, source_column in extra_columns.items():
            if display_name not in self.extra_data:
                self.extra_data[display_name] = {}
            
            if source_column in df.columns:
                for _, row in df.iterrows():
                    try:
                        code = self.clean_code(row[code_column])
                        if code and pd.notna(row[source_column]):
                            self.extra_data[display_name][code] = str(row[source_column]).strip()
                    except Exception:
                        pass


class FreeCashFlowStockData(BaseStockData):
    """自由现金流排名股票数据"""
    
    def __init__(self, data_dir: str):
        super().__init__(data_dir, date_dependent=True)
        self.file_name = 'Free_cash_flow_ranking.csv'
    
    def _determine_file_path(self) -> str:
        path = os.path.join(self.data_dir, self.file_name)
        
        return path
    
    def _extract_extra_data(self, df: pd.DataFrame, code_column: str) -> None:
        extra_columns = {
            '现金/市值': '现金/市值',
            '资产负债率': '资产负债率',
            'PE.扣非': 'PE.扣非',
            '市值.亿': '市值.亿'
        }
        
        for display_name, source_column in extra_columns.items():
            if display_name not in self.extra_data:
                self.extra_data[display_name] = {}
            
            if source_column in df.columns:
                for _, row in df.iterrows():
                    try:
                        code = self.clean_code(row[code_column])
                        if code and pd.notna(row[source_column]):
                            self.extra_data[display_name][code] = str(row[source_column]).strip()
                    except Exception:
                        pass


class DiscountedFreeCashFlowStockData(BaseStockData):
    """自由现金流折现排名股票数据"""
    
    def __init__(self, data_dir: str):
        super().__init__(data_dir, date_dependent=True)
        self.file_name = 'Discounted_free_cash_flow_ranking.csv'
    
    def _determine_file_path(self) -> str:
        path = os.path.join(self.data_dir, self.file_name)
        
        return path
    
    def _extract_extra_data(self, df: pd.DataFrame, code_column: str) -> None:
        extra_columns = {
            '低估率': '低估率',
            '资产负债率': '资产负债率',
            'PE': 'PE',
            'PB': 'PB'
        }
        
        for display_name, source_column in extra_columns.items():
            if display_name not in self.extra_data:
                self.extra_data[display_name] = {}
            
            if source_column in df.columns:
                for _, row in df.iterrows():
                    try:
                        code = self.clean_code(row[code_column])
                        if code and pd.notna(row[source_column]):
                            self.extra_data[display_name][code] = str(row[source_column]).strip()
                    except Exception:
                        pass