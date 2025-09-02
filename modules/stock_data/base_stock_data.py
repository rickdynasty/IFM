"""
股票数据基类
定义股票数据的基本结构和通用方法
"""

import pandas as pd
import os
import re
from typing import Dict, List, Set, Optional, Any, Union
from abc import ABC, abstractmethod
from .base_data import BaseData


class BaseStockData(BaseData):
    """
    股票数据基类，定义股票通用基础数据结构
    """
    
    def __init__(self, data_dir: str, date_dependent: bool = True):
        """
        初始化基础股票数据类
        
        Args:
            data_dir: 数据目录路径
            date_dependent: 是否依赖日期目录
        """
        super().__init__(data_dir)
        self.date_dependent = date_dependent
        
        # 基础股票数据
        self.stock_codes = set()  # 股票代码集合
        self.stock_info = {}      # 股票基本信息
        self.extra_data = {}      # 额外列数据
    
    @abstractmethod
    def _determine_file_path(self) -> str:
        """确定数据文件路径"""
        pass
        
    def load(self) -> bool:
        """
        加载数据
        
        Returns:
            bool: 加载是否成功
        """
        file_path = self._determine_file_path()
        
        if not file_path:
            self._is_loaded = False
            return False
            
        if not os.path.exists(file_path):
            self._is_loaded = False
            return False
        
        try:
            # 读取数据文件
            if file_path.endswith('.txt'):
                df = self._read_csv_file(file_path, sep='\t')
            else:
                df = self._read_csv_file(file_path)
                
            # 处理列名，去除可能的空格
            if not df.empty:
                df.columns = [col.strip() if isinstance(col, str) else col for col in df.columns]
            
            if df.empty:
                self._is_loaded = False
                return False
            
            # 提取数据
            code_column = self._find_code_column(df)
            if code_column:
                self._extract_stock_codes(df, code_column)
                self._extract_stock_info(df, code_column)
                self._extract_extra_data(df, code_column)
                
                self._is_loaded = True
                return True
            else:
                self._is_loaded = False
                return False
                
        except Exception:
            self._is_loaded = False
            return False
    
    def _find_code_column(self, df: pd.DataFrame) -> Optional[str]:
        """
        查找股票代码列
        
        Args:
            df: 数据帧
            
        Returns:
            str: 代码列名，如果找不到则返回None
        """
        code_columns = ['代码', '股票代码', 'code', 'stock_code', '股票', '序']
        
        for col in code_columns:
            if col in df.columns:
                return col
        
        # 如果找不到预定义的列名，尝试使用第一列
        if not df.empty:
            return df.columns[0]
        
        return None
    
    def _extract_stock_codes(self, df: pd.DataFrame, code_column: str) -> None:
        """
        从数据帧提取股票代码
        
        Args:
            df: 数据帧
            code_column: 代码列名
        """
        self.stock_codes = set()
        
        for value in df[code_column]:
            code = self.clean_code(value)
            if code:
                self.stock_codes.add(code)
    
    def _extract_stock_info(self, df: pd.DataFrame, code_column: str) -> None:
        """
        从数据帧提取股票基本信息
        
        Args:
            df: 数据帧
            code_column: 代码列名
        """
        # 查找名称列
        name_columns = ['名称', '股票名称', '股票']
        name_column = next((col for col in name_columns if col in df.columns), None)
        
        # 查找行业列
        industry_columns = ['行业', '所属行业', '申万行业', '行业分类']
        industry_column = next((col for col in industry_columns if col in df.columns), None)
        
        # 查找常见财务指标列
        financial_columns = {
            '当前ROE': ['当前ROE', 'ROE', 'roe'],
            '扣非PE': ['扣非PE', '扣非pe', 'PE', 'pe'],
            'PB': ['PB', 'pb'],
            '股息率': ['股息', '股息率', '股息%', '最新股息'],
            '今年来': ['今年来', '今年涨幅', '年初至今']
        }
        
        # 实际数据帧中的列映射
        column_mapping = {}
        for std_col, possible_cols in financial_columns.items():
            for col in possible_cols:
                if col in df.columns:
                    column_mapping[col] = std_col
                    break
        
        # 提取每行数据
        for _, row in df.iterrows():
            try:
                code = self.clean_code(row[code_column])
                if not code:
                    continue
                
                # 初始化股票信息
                if code not in self.stock_info:
                    self.stock_info[code] = {}
                
                # 提取名称
                if name_column and pd.notna(row.get(name_column)):
                    if '.' in str(row[code_column]):
                        # 如果代码列中包含名称（格式为"代码.名称"）
                        parts = str(row[code_column]).split('.')
                        if len(parts) > 1:
                            name = parts[1].strip()
                            if name and (not self.stock_info[code].get('名称') or not self.stock_info[code]['名称']):
                                self.stock_info[code]['名称'] = name
                    elif not self.stock_info[code].get('名称') or not self.stock_info[code]['名称']:
                        self.stock_info[code]['名称'] = str(row[name_column]).strip()
                
                # 提取行业
                if industry_column and pd.notna(row.get(industry_column)):
                    if not self.stock_info[code].get('行业') or not self.stock_info[code]['行业']:
                        self.stock_info[code]['行业'] = str(row[industry_column]).strip()
                
                # 提取财务指标
                for orig_col, std_col in column_mapping.items():
                    if pd.notna(row.get(orig_col)) and (not self.stock_info[code].get(std_col) or not self.stock_info[code][std_col]):
                        self.stock_info[code][std_col] = str(row[orig_col]).strip()
            except Exception:
                pass
    
    def _extract_extra_data(self, df: pd.DataFrame, code_column: str) -> None:
        """
        从数据帧提取额外列数据，子类需要重写此方法以处理特定的额外数据
        
        Args:
            df: 数据帧
            code_column: 代码列名
        """
        pass
    
    def get_data(self, key: str = None) -> Any:
        """
        获取数据
        
        Args:
            key: 数据键，如果为None则返回所有数据
            
        Returns:
            请求的数据
        """
        if not self.is_loaded:
            return None
        
        if key is None:
            return {
                'stock_codes': self.stock_codes,
                'stock_info': self.stock_info,
                'extra_data': self.extra_data
            }
        
        if key == 'stock_codes':
            return self.stock_codes
        elif key == 'stock_info':
            return self.stock_info
        elif key == 'extra_data':
            return self.extra_data
        else:
            return None
    
    def filter_by_roe(self, min_roe: float) -> Set[str]:
        """
        按ROE过滤股票
        
        Args:
            min_roe: 最小ROE阈值(%)
            
        Returns:
            Set[str]: 符合条件的股票代码集合
        """
        if not self.is_loaded:
            return set()
            
        filtered_codes = set()
        
        for code in self.stock_codes:
            roe_value = None
            
            # 尝试从额外数据中获取平均ROE
            if '平均ROE' in self.extra_data and code in self.extra_data['平均ROE']:
                roe_value = self.safe_get_numeric(self.extra_data['平均ROE'][code])
            
            # 尝试从股票信息中获取当前ROE
            if roe_value is None and code in self.stock_info and '当前ROE' in self.stock_info[code]:
                roe_value = self.safe_get_numeric(self.stock_info[code]['当前ROE'])
            
            # 尝试从额外数据中获取ROE
            if roe_value is None and 'ROE' in self.extra_data and code in self.extra_data['ROE']:
                roe_value = self.safe_get_numeric(self.extra_data['ROE'][code])
            
            if roe_value is not None and roe_value >= min_roe:
                filtered_codes.add(code)
        
        return filtered_codes
    
    def filter_by_dividend(self, min_dividend: float) -> Set[str]:
        """
        按股息率过滤股票
        
        Args:
            min_dividend: 最小股息率阈值(%)
            
        Returns:
            Set[str]: 符合条件的股票代码集合
        """
        if not self.is_loaded:
            return set()
            
        filtered_codes = set()
        
        for code in self.stock_codes:
            dividend_value = None
            
            # 尝试从额外数据中获取平均股息
            if '平均股息' in self.extra_data and code in self.extra_data['平均股息']:
                dividend_value = self.safe_get_numeric(self.extra_data['平均股息'][code])
            
            # 尝试从额外数据中获取股息率
            if dividend_value is None and '股息率' in self.extra_data and code in self.extra_data['股息率']:
                dividend_value = self.safe_get_numeric(self.extra_data['股息率'][code])
            
            # 尝试从股票信息中获取股息率
            if dividend_value is None and code in self.stock_info and '股息率' in self.stock_info[code]:
                dividend_value = self.safe_get_numeric(self.stock_info[code]['股息率'])
            
            # 尝试从股票信息中获取股息
            if dividend_value is None and code in self.stock_info and '股息' in self.stock_info[code]:
                dividend_value = self.safe_get_numeric(self.stock_info[code]['股息'])
            
            if dividend_value is not None and dividend_value >= min_dividend:
                filtered_codes.add(code)
        
        return filtered_codes
    
    def filter_by_industry(self, industries: List[str]) -> Set[str]:
        """
        按行业过滤股票
        
        Args:
            industries: 行业列表
            
        Returns:
            Set[str]: 符合条件的股票代码集合
        """
        if not self.is_loaded or not industries:
            return self.stock_codes
            
        filtered_codes = set()
        
        for code in self.stock_codes:
            if code in self.stock_info and '行业' in self.stock_info[code]:
                industry = self.stock_info[code]['行业']
                if industry and industry in industries:
                    filtered_codes.add(code)
        
        return filtered_codes