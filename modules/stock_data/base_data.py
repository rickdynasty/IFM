"""
数据管理基类
定义通用的数据处理接口和方法
"""

from abc import ABC, abstractmethod
import pandas as pd
import os
import re
from typing import Dict, List, Set, Optional, Any, Union


class BaseData(ABC):
    """数据管理基类，定义通用的数据加载和处理方法"""
    
    def __init__(self, data_dir: str):
        """
        初始化数据基类
        
        Args:
            data_dir: 数据目录路径
        """
        self.data_dir = data_dir
        self.data = {}  # 存储数据的字典
        self._is_loaded = False
    
    @property
    def is_loaded(self) -> bool:
        """数据是否已加载"""
        return self._is_loaded
    
    @abstractmethod
    def load(self) -> bool:
        """
        加载数据
        
        Returns:
            bool: 加载是否成功
        """
        pass
    
    @abstractmethod
    def get_data(self, key: str = None) -> Any:
        """
        获取数据
        
        Args:
            key: 数据键，如果为None则返回所有数据
            
        Returns:
            请求的数据，如果key不存在则返回None
        """
        if key is None:
            return self.data
        return self.data.get(key)
    
    def _read_csv_file(self, file_path: str, sep: str = ',', encoding: str = 'utf-8') -> pd.DataFrame:
        """
        安全读取CSV文件
        
        Args:
            file_path: 文件路径
            sep: 分隔符，默认为逗号
            encoding: 文件编码，默认为utf-8
            
        Returns:
            pd.DataFrame: 读取的数据，如果读取失败则返回空DataFrame
        """
        try:
            if os.path.exists(file_path):
                if file_path.endswith('.txt'):
                    return pd.read_csv(file_path, sep=sep, encoding=encoding)
                return pd.read_csv(file_path, encoding=encoding)
            return pd.DataFrame()
        except Exception as e:
            print(f"读取文件 {file_path} 失败: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def clean_code(code_str: str) -> str:
        """
        清理并标准化股票代码
        
        Args:
            code_str: 原始股票代码字符串
            
        Returns:
            str: 标准化的6位股票代码
        """
        if not code_str or pd.isna(code_str):
            return ""
        
        code_str = str(code_str).replace("'", "").strip()
        
        # 处理"SH600519.贵州茅台"或"600519.贵州茅台"格式
        if '.' in code_str:
            code_part = code_str.split('.')[0]
            clean_code = re.sub(r'^(SH|SZ)', '', code_part)
        # 处理可能包含逗号的格式
        elif ',' in code_str:
            parts = code_str.split(',')
            if len(parts) > 1:
                # 假设第二部分是代码
                code_part = parts[1].strip()
                clean_code = re.sub(r'^(SH|SZ)', '', code_part)
            else:
                # 只有一部分，可能是纯代码
                clean_code = code_str
        else:
            # 假设是纯代码
            clean_code = code_str
        
        # 确保代码只包含数字
        clean_code = re.sub(r'\D', '', clean_code)
        
        # 标准化为6位数字
        if clean_code:
            return clean_code.zfill(6)
        
        return ""
    
    @staticmethod
    def safe_get_numeric(value: Any, allow_percent: bool = True) -> Optional[float]:
        """
        安全获取数值，处理各种格式
        
        Args:
            value: 要转换的值
            allow_percent: 是否允许百分比格式
            
        Returns:
            float: 转换后的数值，如果转换失败则返回None
        """
        if pd.isna(value) or value == '' or value == '-':
            return None
            
        try:
            if isinstance(value, (int, float)):
                return float(value)
                
            value_str = str(value).replace("'", "").strip()
            
            # 处理百分比格式
            if allow_percent and '%' in value_str:
                return float(value_str.replace('%', ''))
            
            # 处理带有单位的格式，如"亿"
            if '亿' in value_str:
                return float(value_str.replace('亿', ''))
                
            return float(value_str)
        except Exception:
            return None
