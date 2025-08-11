"""
股票数据管理器
管理多个StockData实例，提供统一的数据访问和筛选接口
"""

import pandas as pd
import os
from typing import Dict, List, Set, Optional, Any, Union
from .stock_data import StockData
from .stock_data_factory import StockDataFactory


class StockDataManager:
    """股票数据管理器，管理多个数据源，提供统一的筛选接口"""
    
    def __init__(self, data_dir: str = None, selected_date: str = None):
        """
        初始化股票数据管理器
        
        Args:
            data_dir: 数据根目录，默认为'data/stock'
            selected_date: 选择的日期，如'2025.08'
        """
        if data_dir is None:
            self.data_dir = os.path.join('data', 'stock')
        else:
            self.data_dir = data_dir
        
        self.selected_date = selected_date
        
        # 存储加载的StockData实例
        self.stock_data_instances: Dict[str, StockData] = {}
        
        # 存储所有股票的综合信息
        self.all_stock_info: Dict[str, Dict[str, Any]] = {}
        
        # 存储各筛选条件的股票代码集合
        self.filtered_codes: Dict[str, Set[str]] = {}
        
        # 缓存
        self._industries_cache = None
        self._loaded_types = set()  # 已加载的股票类型集合
    
    def load_stock_data(self, stock_type: str, sub_type: Optional[str] = None) -> bool:
        """
        加载特定类型的股票数据
        
        Args:
            stock_type: 股票类型
            sub_type: 子类型
            
        Returns:
            bool: 加载是否成功
        """
        # 生成数据实例的键
        instance_key = f"{stock_type}_{sub_type}" if sub_type else stock_type
        
        # 检查缓存：如果已经加载过，直接返回True
        if instance_key in self.stock_data_instances and self.stock_data_instances[instance_key].is_loaded:
            return True
        
        # 创建StockData实例
        stock_data = StockDataFactory.get_stock_data(
            stock_type=stock_type,
            sub_type=sub_type,
            data_dir=self.data_dir,
            selected_date=self.selected_date
        )
        
        if stock_data is None:
            return False
        
        # 加载数据
        if stock_data.load():
            # 缓存实例
            self.stock_data_instances[instance_key] = stock_data
            
            # 更新filtered_codes
            self.filtered_codes[instance_key] = stock_data.stock_codes
            
            # 更新all_stock_info
            self._update_all_stock_info(stock_data)
            
            # 记录已加载的类型
            self._loaded_types.add(stock_type)
            
            return True
        else:
            return False
    
    def _update_all_stock_info(self, stock_data: StockData) -> None:
        """
        更新综合股票信息
        
        Args:
            stock_data: StockData实例
        """
        # 获取数据
        stock_info = stock_data.get_data('stock_info')
        extra_data = stock_data.get_data('extra_data')
        
        # 更新股票基本信息
        for code, info in stock_info.items():
            if code not in self.all_stock_info:
                self.all_stock_info[code] = {}
            
            # 更新名称和行业（如果当前没有这些信息）
            if '名称' in info and info['名称'] and (not self.all_stock_info[code].get('名称')):
                self.all_stock_info[code]['名称'] = info['名称']
            
            if '行业' in info and info['行业'] and (not self.all_stock_info[code].get('行业')):
                self.all_stock_info[code]['行业'] = info['行业']
            
            # 更新其他财务指标
            for key, value in info.items():
                if key not in ['名称', '行业'] and value:
                    self.all_stock_info[code][key] = value
        
        # 更新额外数据
        for display_name, data_dict in extra_data.items():
            for code, value in data_dict.items():
                if code in self.all_stock_info and value:
                    self.all_stock_info[code][display_name] = value
    
    def get_available_industries(self) -> List[str]:
        """
        获取所有可用的行业列表
        
        Returns:
            List[str]: 行业列表
        """
        # 使用缓存
        if self._industries_cache is not None:
            return self._industries_cache
        
        # 收集所有行业
        industries = set()
        
        # 确保至少加载了一种股票类型的数据
        if not self.stock_data_instances:
            # 尝试加载至少一种类型的数据
            stock_types = StockDataFactory.get_all_stock_types()
            if stock_types:
                self.load_stock_data(stock_types[0])
        
        # 从已加载的数据中提取行业信息
        for stock_data in self.stock_data_instances.values():
            stock_info = stock_data.get_data('stock_info')
            if stock_info:
                for info in stock_info.values():
                    if '行业' in info and info['行业']:
                        industries.add(info['行业'])
        
        # 转换为排序列表
        industry_list = sorted(list(industries))
        
        # 缓存结果
        self._industries_cache = industry_list
        
        return industry_list
    
    def filter_stocks(self, selected_types: List[str], sub_types: Dict[str, str] = None, 
                     industry_filter: List[str] = None, roe_filter: Optional[float] = None, 
                     dividend_filter: Optional[float] = None) -> pd.DataFrame:
        """
        根据多条件筛选股票
        
        Args:
            selected_types: 选择的股票类型列表
            sub_types: 每种类型选择的子类型
            industry_filter: 行业筛选条件
            roe_filter: ROE筛选阈值
            dividend_filter: 股息率筛选阈值
            
        Returns:
            pd.DataFrame: 筛选结果
        """
        if not selected_types:
            return pd.DataFrame()
        
        sub_types = sub_types or {}
        
        # 批量加载所有选定的股票数据
        instance_keys = []
        for stock_type in selected_types:
            sub_type = sub_types.get(stock_type)
            instance_key = f"{stock_type}_{sub_type}" if sub_type else stock_type
            instance_keys.append(instance_key)
            
            # 如果未加载，尝试加载
            if instance_key not in self.stock_data_instances:
                if not self.load_stock_data(stock_type, sub_type):
                    # 加载失败，返回空结果
                    return pd.DataFrame()
        
        # 找出同时满足所有类型条件的股票（交集）
        if not instance_keys:
            return pd.DataFrame()
            
        # 使用集合操作找出交集
        common_codes = None
        for instance_key in instance_keys:
            if instance_key in self.filtered_codes:
                if common_codes is None:
                    common_codes = self.filtered_codes[instance_key].copy()
                else:
                    common_codes &= self.filtered_codes[instance_key]
        
        if not common_codes:
            return pd.DataFrame()
        
        # 应用ROE筛选
        if roe_filter is not None:
            roe_filtered_codes = set()
            
            # 遍历所有股票
            for code in common_codes:
                if code in self.all_stock_info:
                    info = self.all_stock_info[code]
                    
                    # 尝试从不同字段获取ROE值
                    roe_value = None
                    
                    if '平均ROE' in info:
                        roe_value = StockData.safe_get_numeric(info['平均ROE'])
                    
                    if roe_value is None and '当前ROE' in info:
                        roe_value = StockData.safe_get_numeric(info['当前ROE'])
                    
                    if roe_value is None and 'ROE' in info:
                        roe_value = StockData.safe_get_numeric(info['ROE'])
                    
                    # 检查ROE值是否满足条件
                    if roe_value is not None and roe_value >= roe_filter:
                        roe_filtered_codes.add(code)
            
            common_codes = roe_filtered_codes
        
        # 应用股息筛选
        if dividend_filter is not None:
            dividend_filtered_codes = set()
            
            # 遍历所有股票
            for code in common_codes:
                if code in self.all_stock_info:
                    info = self.all_stock_info[code]
                    
                    # 尝试从不同字段获取股息值
                    dividend_value = None
                    
                    if '平均股息' in info:
                        dividend_value = StockData.safe_get_numeric(info['平均股息'])
                    
                    if dividend_value is None and '股息率' in info:
                        dividend_value = StockData.safe_get_numeric(info['股息率'])
                    
                    if dividend_value is None and '股息' in info:
                        dividend_value = StockData.safe_get_numeric(info['股息'])
                    
                    # 检查股息值是否满足条件
                    if dividend_value is not None and dividend_value >= dividend_filter:
                        dividend_filtered_codes.add(code)
            
            common_codes = dividend_filtered_codes
        
        # 应用行业筛选
        if industry_filter:
            industry_filtered_codes = set()
            
            for code in common_codes:
                if (code in self.all_stock_info and 
                    '行业' in self.all_stock_info[code] and 
                    self.all_stock_info[code]['行业'] in industry_filter):
                    industry_filtered_codes.add(code)
            
            common_codes = industry_filtered_codes
        
        if not common_codes:
            return pd.DataFrame()
        
        # 构建结果DataFrame
        result_data = []
        
        # 标准列顺序 - 基本列和财务指标列
        base_cols = ['股票代码', '股票名称']
        finance_cols = ['股息率']
        end_cols = ['今年来', '行业']  # 这些列将放在最后
        
        # 收集所有可用的额外列
        extra_cols = set()
        for instance in self.stock_data_instances.values():
            for col_name in instance.extra_data.keys():
                # 避免重复列
                if (col_name not in finance_cols and 
                    col_name not in end_cols and 
                    not (col_name == 'ROE' and '当前ROE' in finance_cols)):
                    extra_cols.add(col_name)
        
        # 为每个股票构建数据行
        for code in common_codes:
            if code not in self.all_stock_info:
                continue
                
            info = self.all_stock_info[code]
            
            # 基本信息
            row = {
                '股票代码': code,
                '股票名称': info.get('名称', ''),
                '行业': info.get('行业', '')
            }
            
            # 财务指标
            for col in finance_cols:
                row[col] = info.get(col, '')
                
            # 末尾列（今年来、行业）
            for col in end_cols:
                row[col] = info.get(col, '')
            
            # 额外列数据
            for col in extra_cols:
                row[col] = info.get(col, '')
            
            result_data.append(row)
        
        # 创建DataFrame并设置列顺序
        result_df = pd.DataFrame(result_data)
        
        if not result_df.empty:
            # 确定最终列顺序 - 财务指标在中间，"今年来"和"行业"放在最后
            cols = base_cols + finance_cols + list(extra_cols) + end_cols
            
            # 确保所有列都在DataFrame中
            valid_cols = [col for col in cols if col in result_df.columns]
            
            # 重新排序列
            result_df = result_df[valid_cols]
        
        return result_df
