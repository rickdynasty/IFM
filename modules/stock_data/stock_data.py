"""
股票数据类
处理不同类型股票数据的加载和筛选
"""

import pandas as pd
import os
import re
from typing import Dict, List, Set, Optional, Any, Union, Tuple
from .base_data import BaseData


class StockData(BaseData):
    """股票数据类，处理特定类型股票数据的加载和筛选"""
    
    def __init__(self, data_dir: str, stock_type: str, sub_type: Optional[str] = None, 
                 config: Dict[str, Any] = None, date_dependent: bool = True):
        """
        初始化股票数据类
        
        Args:
            data_dir: 基础数据目录
            stock_type: 股票类型，如'北上资金持股', 'ROE排名'等
            sub_type: 子类型，如'近1天', '连续3年'等
            config: 数据配置字典，包含文件名模式和列映射等
            date_dependent: 是否依赖日期目录
        """
        super().__init__(data_dir)
        self.stock_type = stock_type
        self.sub_type = sub_type
        self.config = config or {}
        self.date_dependent = date_dependent
        
        # 存储处理后的数据
        self.stock_codes = set()  # 股票代码集合
        self.stock_info = {}  # 股票基本信息
        self.extra_data = {}  # 额外列数据
        
        # 确定文件路径
        self.file_path = self._determine_file_path()
    
    def _determine_file_path(self) -> str:
        """
        确定数据文件路径
        
        Returns:
            str: 文件路径
        """
        if 'sub_types' not in self.config or self.config['sub_types'] is None:
            # 无子类型的情况
            if self.date_dependent and 'file' in self.config:
                return os.path.join(self.data_dir, self.config['file'])
            elif not self.date_dependent and 'file' in self.config:
                # 不依赖日期目录，直接从根目录读取
                return os.path.join(os.path.dirname(os.path.dirname(self.data_dir)), self.config['file'])
        else:
            # 有子类型的情况
            if self.sub_type is None and self.config['sub_types']:
                # 默认使用第一个子类型
                self.sub_type = list(self.config['sub_types'].keys())[0]
            
            if self.sub_type in self.config['sub_types'] and 'file_pattern' in self.config:
                sub_type_value = self.config['sub_types'][self.sub_type]
                
                if not self.date_dependent:
                    # 不依赖日期目录，直接从根目录读取
                    return os.path.join(
                        os.path.dirname(os.path.dirname(self.data_dir)), 
                        self.config['file_pattern'].format(sub_type_value)
                    )
                else:
                    # 依赖日期目录
                    return os.path.join(self.data_dir, self.config['file_pattern'].format(sub_type_value))
        
        # 如果无法确定路径，返回空字符串
        return ""
    
    def load(self) -> bool:
        """
        加载数据
        
        Returns:
            bool: 加载是否成功
        """
        if not self.file_path or not os.path.exists(self.file_path):
            self._is_loaded = False
            return False
        
        try:
            # 根据文件类型加载数据
            if self.file_path.endswith('.txt'):
                df = self._read_csv_file(self.file_path, sep='\t')
            else:
                df = self._read_csv_file(self.file_path)
            
            if df.empty:
                self._is_loaded = False
                return False
            
            # 提取股票代码
            code_column = self._find_code_column(df)
            if code_column:
                self._extract_stock_codes(df, code_column)
            else:
                self._is_loaded = False
                return False
            
            # 提取股票基本信息
            self._extract_stock_info(df, code_column)
            
            # 提取额外列数据
            self._extract_extra_data(df, code_column)
            
            self._is_loaded = True
            return True
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
        
        # 遍历代码列，处理每个代码
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
        name_column = None
        
        for col in name_columns:
            if col in df.columns:
                name_column = col
                break
        
        # 查找行业列
        industry_columns = ['行业', '所属行业', '申万行业', '行业分类']
        industry_column = None
        
        for col in industry_columns:
            if col in df.columns:
                industry_column = col
                break
        
        # 查找常见财务指标列
        financial_columns = {
            '当前ROE': ['当前ROE', 'ROE', 'roe'],
            '扣非PE': ['扣非PE', '扣非pe', 'PE', 'pe'],
            'PB': ['PB', 'pb'],
            '股息率': ['股息', '股息率', '股息%', '最新股息'],  # 添加'最新股息'作为可能的股息列
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
                # 获取股票代码
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
        从数据帧提取额外列数据
        
        Args:
            df: 数据帧
            code_column: 代码列名
        """
        if 'extra_columns' not in self.config:
            return
        
        # 遍历配置中的额外列
        for display_name, source_column in self.config['extra_columns'].items():
            # 初始化额外数据字典
            if display_name not in self.extra_data:
                self.extra_data[display_name] = {}
            
            # 处理特殊情况
            if self.stock_type == 'ROE连续超15%' and display_name == '平均ROE':
                self._extract_roe_data(df, code_column, display_name)
            elif self.stock_type == 'ROE连续超15%' and display_name == '北上持股':
                self._extract_northbound_data(df, code_column, display_name)
            elif display_name == '股息率':
                self._extract_dividend_data(df, code_column, display_name)
            # 常规情况
            elif source_column in df.columns:
                for _, row in df.iterrows():
                    try:
                        code = self.clean_code(row[code_column])
                        if code and pd.notna(row[source_column]):
                            self.extra_data[display_name][code] = str(row[source_column]).strip()
                    except Exception:
                        pass
            else:
                pass
    
    def _extract_roe_data(self, df: pd.DataFrame, code_column: str, display_name: str) -> None:
        """
        提取ROE数据的特殊处理
        
        Args:
            df: 数据帧
            code_column: 代码列名
            display_name: 显示名称
        """
        # 尝试多种可能的ROE列名
        roe_columns = ['ROE', 'roe', '平均ROE', '平均roe', 'ROE(%)', 'roe(%)', '平均ROE(%)', '平均roe(%)']
        
        # 查找匹配的列
        found_column = next((col for col in roe_columns if col in df.columns), None)
        
        if found_column:
            # 从数据帧提取ROE数据
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
    
    def _extract_northbound_data(self, df: pd.DataFrame, code_column: str, display_name: str) -> None:
        """
        提取北上持股数据的特殊处理
        
        Args:
            df: 数据帧
            code_column: 代码列名
            display_name: 显示名称
        """
        if '北上持股' in df.columns:
            # 从数据帧提取北上持股数据
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
    
    def _extract_dividend_data(self, df: pd.DataFrame, code_column: str, display_name: str) -> None:
        """
        提取股息率数据的特殊处理
        
        Args:
            df: 数据帧
            code_column: 代码列名
            display_name: 显示名称
        """
        # 尝试多种可能的股息列名
        dividend_columns = ['股息', '股息率', '最新股息', '股息%', '股息(%)', '股息率(%)']
        
        # 查找匹配的列
        found_column = next((col for col in dividend_columns if col in df.columns), None)
        
        if found_column:
            # 从数据帧提取股息数据
            for _, row in df.iterrows():
                try:
                    code = self.clean_code(row[code_column])
                    if code and pd.notna(row[found_column]):
                        self.extra_data[display_name][code] = str(row[found_column]).strip()
                except Exception:
                    pass
        else:
            # 如果没有找到股息列，尝试使用stock_info中的股息数据
            for code in self.stock_codes:
                if code in self.stock_info and '股息' in self.stock_info[code]:
                    self.extra_data[display_name][code] = self.stock_info[code]['股息']
    
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
                'extra_data': self.extra_data,
                'stock_type': self.stock_type,
                'sub_type': self.sub_type
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
            
            # 如果有有效的ROE值且大于等于阈值，则添加到结果中
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
            
            # 如果有有效的股息值且大于等于阈值，则添加到结果中
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
