"""
股票数据管理器
管理多个股票数据实例，提供统一的数据访问和筛选接口，实现缓存机制
"""

import pandas as pd
import os
import pickle
from typing import Dict, List, Set, Optional, Any, Tuple
from datetime import datetime

from .base_stock_data import BaseStockData
from .stock_data_factory import StockDataFactory


class StockDataManager:
    """
    股票数据管理器，管理多个数据源，提供统一的筛选接口和缓存机制
    """
    
    CACHE_DIR = "user_data/cache"  # 缓存目录
    
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
        
        # 存储加载的数据实例
        self.stock_data_instances: Dict[str, BaseStockData] = {}
        
        # 存储所有股票的综合信息
        self.all_stock_info: Dict[str, Dict[str, Any]] = {}
        
        # 存储各筛选条件的股票代码集合
        self.filtered_codes: Dict[str, Set[str]] = {}
        
        # 缓存和加载记录
        self._industries_cache = None
        self._loaded_types = set()  # 已加载的股票类型集合
        
        # 确保缓存目录存在
        os.makedirs(self.CACHE_DIR, exist_ok=True)
    
    def load_stock_data(self, stock_type: str, sub_type: Optional[str] = None) -> bool:
        """
        加载特定类型的股票数据，优先从缓存加载
        
        Args:
            stock_type: 股票类型
            sub_type: 子类型
            
        Returns:
            bool: 加载是否成功
        """
        # 生成数据实例的键
        instance_key = f"{stock_type}_{sub_type}" if sub_type else stock_type
        
        # 检查内存缓存：如果已经加载过，直接返回True
        if instance_key in self.stock_data_instances and self.stock_data_instances[instance_key].is_loaded:
            return True
        
        # 尝试从磁盘缓存加载
        if self._load_from_cache(instance_key):
            return True
        
        # 如果缓存不存在或过期，创建新的数据实例
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
            
            # 保存到磁盘缓存
            self._save_to_cache(instance_key, stock_data)
            
            return True
        else:
            return False
    
    def load_all_stock_data(self) -> bool:
        """
        加载所有类型的股票数据，用于股票查询场景
        
        Returns:
            bool: 是否所有数据都加载成功
        """
        all_success = True
        stock_types = StockDataFactory.get_all_stock_types()
        
        for stock_type in stock_types:
            if StockDataFactory.STOCK_DATA_TYPES[stock_type].get('has_sub_types', False):
                sub_types = StockDataFactory.get_sub_types(stock_type)
                if sub_types:
                    for sub_type in sub_types:
                        if not self.load_stock_data(stock_type, sub_type):
                            all_success = False
            else:
                if not self.load_stock_data(stock_type):
                    all_success = False
        
        return all_success
    
    def _get_cache_file_path(self, instance_key: str) -> str:
        """
        获取缓存文件路径
        
        Args:
            instance_key: 实例键名
            
        Returns:
            str: 缓存文件路径
        """
        date_part = self.selected_date.replace('.', '_') if self.selected_date else 'current'
        return os.path.join(self.CACHE_DIR, f"{instance_key}_{date_part}.pkl")
    
    def _load_from_cache(self, instance_key: str) -> bool:
        """
        从缓存加载数据
        
        Args:
            instance_key: 实例键名
            
        Returns:
            bool: 是否成功加载缓存
        """
        cache_file = self._get_cache_file_path(instance_key)
        
        if os.path.exists(cache_file):
            try:
                # 检查缓存文件是否是当天创建的
                file_mtime = os.path.getmtime(cache_file)
                file_date = datetime.fromtimestamp(file_mtime).date()
                today = datetime.now().date()
                
                # 如果缓存文件不是当天创建的，则认为过期
                if file_date != today:
                    return False
                
                # 从缓存文件加载数据
                with open(cache_file, 'rb') as f:
                    cached_data = pickle.load(f)
                
                # 更新内存中的数据
                self.stock_data_instances[instance_key] = cached_data
                self.filtered_codes[instance_key] = cached_data.stock_codes
                self._update_all_stock_info(cached_data)
                
                # 如果是特定股票类型，记录
                stock_type = instance_key.split('_')[0] if '_' in instance_key else instance_key
                self._loaded_types.add(stock_type)
                
                return True
            except Exception:
                # 如果加载失败，删除可能损坏的缓存文件
                try:
                    os.remove(cache_file)
                except:
                    pass
                return False
        
        return False
    
    def _save_to_cache(self, instance_key: str, stock_data: BaseStockData) -> bool:
        """
        保存数据到缓存
        
        Args:
            instance_key: 实例键名
            stock_data: 要缓存的数据实例
            
        Returns:
            bool: 是否成功保存缓存
        """
        cache_file = self._get_cache_file_path(instance_key)
        
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(stock_data, f)
            return True
        except Exception:
            return False
    
    def _update_all_stock_info(self, stock_data: BaseStockData) -> None:
        """
        更新综合股票信息
        
        Args:
            stock_data: 股票数据实例
        """
        # 获取数据
        stock_info = stock_data.get_data('stock_info')
        extra_data = stock_data.get_data('extra_data')
        
        if not stock_info:
            return
        
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
        if extra_data:
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
        
        # 找出同时满足所有类型条件的股票
        result_codes = set()
        
        # 如果只有一种类型，直接使用该类型的所有股票代码
        if len(instance_keys) == 1:
            instance_key = instance_keys[0]
            if instance_key in self.filtered_codes:
                result_codes = self.filtered_codes[instance_key].copy()
        else:
            # 多种类型，需要计算交集
            for instance_key in instance_keys:
                if instance_key in self.filtered_codes:
                    if not result_codes:  # 第一次迭代，直接赋值
                        result_codes = self.filtered_codes[instance_key].copy()
                    else:  # 后续迭代，计算交集
                        result_codes &= self.filtered_codes[instance_key]
        
        if not result_codes:
            return pd.DataFrame()
        
        # 应用ROE筛选
        if roe_filter is not None:
            roe_filtered_codes = set()
            
            for code in result_codes:
                if code in self.all_stock_info:
                    info = self.all_stock_info[code]
                    
                    # 尝试从不同字段获取ROE值
                    roe_value = None
                    
                    if '平均ROE' in info:
                        roe_value = BaseStockData.safe_get_numeric(info['平均ROE'])
                    
                    if roe_value is None and '当前ROE' in info:
                        roe_value = BaseStockData.safe_get_numeric(info['当前ROE'])
                    
                    if roe_value is None and 'ROE' in info:
                        roe_value = BaseStockData.safe_get_numeric(info['ROE'])
                    
                    if roe_value is not None and roe_value >= roe_filter:
                        roe_filtered_codes.add(code)
            
            result_codes = roe_filtered_codes
        
        # 应用股息筛选
        if dividend_filter is not None:
            dividend_filtered_codes = set()
            
            for code in result_codes:
                if code in self.all_stock_info:
                    info = self.all_stock_info[code]
                    
                    # 尝试从不同字段获取股息值
                    dividend_value = None
                    
                    if '平均股息' in info:
                        dividend_value = BaseStockData.safe_get_numeric(info['平均股息'])
                    
                    if dividend_value is None and '股息率' in info:
                        dividend_value = BaseStockData.safe_get_numeric(info['股息率'])
                    
                    if dividend_value is None and '股息' in info:
                        dividend_value = BaseStockData.safe_get_numeric(info['股息'])
                    
                    if dividend_value is not None and dividend_value >= dividend_filter:
                        dividend_filtered_codes.add(code)
            
            result_codes = dividend_filtered_codes
        
        # 应用行业筛选
        if industry_filter:
            industry_filtered_codes = set()
            
            for code in result_codes:
                if (code in self.all_stock_info and 
                    '行业' in self.all_stock_info[code] and 
                    self.all_stock_info[code]['行业'] in industry_filter):
                    industry_filtered_codes.add(code)
            
            result_codes = industry_filtered_codes
        
        if not result_codes:
            return pd.DataFrame()
        
        # 构建结果DataFrame
        return self._build_result_dataframe(result_codes, selected_types, sub_types)
    
    def _build_result_dataframe(self, common_codes: Set[str], 
                              selected_types: List[str], 
                              sub_types: Dict[str, str]) -> pd.DataFrame:
        """
        构建结果DataFrame
        
        Args:
            common_codes: 筛选后的股票代码集合
            selected_types: 选择的股票类型列表
            sub_types: 每种类型选择的子类型
            
        Returns:
            pd.DataFrame: 结果DataFrame
        """
        result_data = []
        
        # 标准列顺序 - 基本列和财务指标列
        base_cols = ['股票代码', '股票名称']
        finance_cols = ['当前ROE', '扣非PE', 'PB', '股息率']
        end_cols = ['今年来', '行业']  # 这些列将放在最后
        
        # 收集所有可用的额外列
        extra_cols = set()
        for stock_type in selected_types:
            sub_type = sub_types.get(stock_type)
            instance_key = f"{stock_type}_{sub_type}" if sub_type else stock_type
            
            if instance_key in self.stock_data_instances:
                for col_name in self.stock_data_instances[instance_key].extra_data.keys():
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
                if col != '行业':  # 行业已经在基本信息中添加
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
        
    def search_stock(self, search_term: str) -> Dict[str, Any]:
        """
        搜索股票，根据代码或名称查找
        
        Args:
            search_term: 搜索条件，可以是股票代码或名称的一部分
            
        Returns:
            Dict: 搜索结果，包含股票基本信息和所属分类
        """
        # 定义重新加载函数，强制清除当前内存中的数据
        def reload_all_data():
            # 清除现有数据
            self.stock_data_instances.clear()
            self.filtered_codes.clear()
        
        # 清除旧数据，确保重新加载
        reload_all_data()
        
        # 先加载一些常用类型，找到股票代码
        initial_types = ['北上资金持股', 'ROE排名', '热门股票']
        stock_code = None
        stock_name = None
        
        for initial_type in initial_types:
            if initial_type == '热门股票':
                sub_type = '近1天'
                self.load_stock_data(initial_type, sub_type)
            else:
                self.load_stock_data(initial_type)
                
            # 查找股票代码
            for code, info in self.all_stock_info.items():
                if search_term.lower() in info.get('名称', '').lower() or search_term.lower() == code.lower():
                    stock_code = code
                    stock_name = info.get('名称', '')
                    break
            
            if stock_code:
                break
        
        if not stock_code:
            return {'stock_info': None, 'categories': []}
        
        # 获取股票基本信息
        basic_info = {
            '股票代码': stock_code,
            '股票名称': stock_name,
            '行业': self.all_stock_info.get(stock_code, {}).get('行业', ''),
            '当前ROE': self.all_stock_info.get(stock_code, {}).get('当前ROE', ''),
            '扣非PE': self.all_stock_info.get(stock_code, {}).get('扣非PE', ''),
            'PB': self.all_stock_info.get(stock_code, {}).get('PB', ''),
            '股息率': self.all_stock_info.get(stock_code, {}).get('股息率', ''),
            '今年来': self.all_stock_info.get(stock_code, {}).get('今年来', '')
        }
        
        # 查找股票所属的分类
        categories = []
        
        # 检查每种股票类型
        for stock_type, stock_data_dict in StockDataFactory.STOCK_DATA_TYPES.items():
            if stock_data_dict.get('has_sub_types', False):
                # 处理有子类型的情况
                sub_types = StockDataFactory.get_sub_types(stock_type)
                for sub_type in sub_types:
                    # 每次都重新加载数据，确保没有缓存干扰
                    instance_key = f"{stock_type}_{sub_type}"
                    if instance_key in self.stock_data_instances:
                        del self.stock_data_instances[instance_key]
                    if instance_key in self.filtered_codes:
                        del self.filtered_codes[instance_key]
                    
                    # 加载数据
                    success = self.load_stock_data(stock_type, sub_type)
                    
                    # 只有在已加载的数据集中才能检查
                    if success and instance_key in self.filtered_codes:
                        # 仅当股票代码确实存在于此分类数据中时添加
                        if stock_code in self.filtered_codes[instance_key]:
                            display_name = f"{stock_type} - {sub_type}"
                            categories.append(display_name)
            else:
                # 处理没有子类型的情况
                # 每次都重新加载数据，确保没有缓存干扰
                if stock_type in self.stock_data_instances:
                    del self.stock_data_instances[stock_type]
                if stock_type in self.filtered_codes:
                    del self.filtered_codes[stock_type]
                
                # 加载数据
                success = self.load_stock_data(stock_type)
                
                # 只有在已加载的数据集中才能检查
                if success and stock_type in self.filtered_codes:
                    # 仅当股票代码确实存在于此分类数据中时添加
                    if stock_code in self.filtered_codes[stock_type]:
                        categories.append(stock_type)
        
        # 返回结果
        return {
            'stock_info': basic_info,
            'categories': categories
        }