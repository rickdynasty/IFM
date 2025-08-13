"""
基金筛选模块
提供基金数据的筛选功能
"""

import pandas as pd
import os
from typing import Dict, List, Set, Optional, Any, Union

from .utils import get_available_dates, get_current_date, safe_read_csv
from .config import FUND_DATA_PATH


def get_available_fund_dates():
    """
    获取可用的基金数据日期列表
    
    Returns:
        List[str]: 可用的日期列表，按降序排序
    """
    return get_available_dates(data_type='fund')


def fund_filter(min_annual_return=5, min_consecutive_return=5, min_years_listed=3, 
               fund_type="全部", fund_manager=None, fund_company=None, data_date=None):
    """
    基金筛选函数
    
    Args:
        min_annual_return: 最低年化收益率
        min_consecutive_return: 最低连续收益率（所有有效年份都需大于该值）
        min_years_listed: 最低上市年限
        fund_type: 基金类型
        fund_manager: 基金经理筛选（可选）
        fund_company: 基金公司筛选（可选）
        data_date: 数据日期，格式为 "YYYY.MM"
        
    Returns:
        pd.DataFrame: 筛选结果
    """
    # 确定使用的数据日期
    if data_date is None:
        available_dates = get_available_fund_dates()
        if available_dates:
            data_date = available_dates[0]  # 使用最新日期
        else:
            return pd.DataFrame()  # 如果没有可用日期，返回空DataFrame
    
    # 加载基金数据
    df_all = None
    
    # 根据基金类型选择加载的文件
    file_mapping = {
        "全部": ["基金_股票型.txt", "基金_混合型.txt", "基金_债券型.txt", "基金_指数型.txt"],
        "股票型": ["基金_股票型.txt"],
        "混合型": ["基金_混合型.txt"],
        "债券型": ["基金_债券型.txt"],
        "指数型": ["基金_指数型.txt"]
    }
    
    files_to_load = file_mapping.get(fund_type, file_mapping["全部"])
    
    # 读取并合并数据
    dfs = []
    for file_name in files_to_load:
        file_path = os.path.join(FUND_DATA_PATH, data_date, file_name)
        df = safe_read_csv(file_path, sep='\t', encoding='utf-8')
        if not df.empty:
            # 添加基金类型列
            fund_type_name = file_name.replace('基金_', '').replace('.txt', '')
            df['基金类型'] = fund_type_name
            dfs.append(df)
    
    # 合并数据
    if dfs:
        df_all = pd.concat(dfs, ignore_index=True)
    else:
        return pd.DataFrame()  # 如果没有读取到数据，返回空DataFrame
    
    # 清理表头空格
    df_all.columns = [c.strip() for c in df_all.columns]
    
    # 转换百分比字符串为数值
    def pct2float(x):
        try:
            if pd.isna(x) or str(x).strip() == '---':
                return None
            return float(str(x).replace('%',''))
        except:
            return None
    
    # 转换各时间段收益率为数值
    time_periods = ['近1周', '近1月', '近3月', '近6月', '近1年', '近2年', '近3年']
    for period in time_periods:
        df_all[f'{period}_数值'] = df_all[period].map(pct2float)
    
    # 计算每一年的年收益率
    def calculate_annual_returns(row):
        """计算每一年的单独年收益率
        
        第1年：直接使用近1年数据
        第2年：近2年总收益 - 近1年总收益
        第3年：近3年总收益 - 近2年总收益
        """
        year1 = row.get('近1年_数值')
        year2 = row.get('近2年_数值')
        year3 = row.get('近3年_数值')
        
        # 计算第一年收益率
        year1_return = year1
        
        # 计算第二年收益率
        year2_return = None
        if year2 is not None and year1 is not None:
            # 计算第二年的收益率
            # (1+r2)^2 = (1+r1)(1+x) => x = (1+r2)^2/(1+r1) - 1
            year2_return = ((1 + year2/100)**2 / (1 + year1/100) - 1) * 100
        
        # 计算第三年收益率
        year3_return = None
        if year3 is not None and year2 is not None:
            # 计算第三年的收益率
            # (1+r3)^3 = (1+r2)^2(1+x) => x = (1+r3)^3/(1+r2)^2 - 1
            year3_return = ((1 + year3/100)**3 / (1 + year2/100)**2 - 1) * 100
        
        return {
            'year1': year1_return,
            'year2': year2_return,
            'year3': year3_return
        }
    
    # 应用函数计算各年收益率
    annual_returns = df_all.apply(calculate_annual_returns, axis=1)
    df_all['第1年收益率'] = annual_returns.apply(lambda x: x['year1'])
    df_all['第2年收益率'] = annual_returns.apply(lambda x: x['year2'])
    df_all['第3年收益率'] = annual_returns.apply(lambda x: x['year3'])
    
    # 计算总体年化收益率（三年平均，考虑有效年份）
    def calculate_annualized_return(row):
        years = []
        if row['第1年收益率'] is not None and not pd.isna(row['第1年收益率']):
            years.append(row['第1年收益率'])
        if row['第2年收益率'] is not None and not pd.isna(row['第2年收益率']):
            years.append(row['第2年收益率'])
        if row['第3年收益率'] is not None and not pd.isna(row['第3年收益率']):
            years.append(row['第3年收益率'])
        
        if years:
            return sum(years) / len(years)
        return None
    
    df_all['年化收益率'] = df_all.apply(calculate_annualized_return, axis=1)
    
    # 计算上市年限：根据最大有效时间点判断
    def calculate_listed_years(row):
        # 按时间从长到短检查，找到最大有效时间点
        period_years = {'近3年': 3, '近2年': 2, '近1年': 1, '近6月': 0.5, '近3月': 0.25, '近1月': 1/12, '近1周': 1/52}
        
        for period, years in period_years.items():
            value = row.get(f'{period}_数值')
            if value is not None and not pd.isna(value):
                return years
        
        return 0  # 如果没有任何有效时间点，返回0
    
    df_all['上市年限'] = df_all.apply(calculate_listed_years, axis=1)
    
    # 应用筛选条件
    # 1. 年化收益率筛选
    if min_annual_return > 0:
        df_all = df_all[df_all['年化收益率'] >= min_annual_return]
    
    # 2. 连续收益率筛选
    if min_consecutive_return > 0:
        # 创建一个筛选条件：所有有效年份的收益率都大于min_consecutive_return
        mask = pd.Series(True, index=df_all.index)
        
        for year_col in ['第1年收益率', '第2年收益率', '第3年收益率']:
            # 只考虑有效的年份（非空值）
            valid_years = ~df_all[year_col].isna()
            # 对于有效年份，检查是否大于等于min_consecutive_return
            meet_criteria = df_all[year_col] >= min_consecutive_return
            # 更新掩码：只有当年份有效且满足条件，或者年份无效时，才保留True
            mask = mask & (meet_criteria | ~valid_years)
        
        df_all = df_all[mask]
    
    # 3. 上市年限筛选
    if min_years_listed > 0:
        df_all = df_all[df_all['上市年限'] >= min_years_listed]
    
    # 4. 基金经理筛选
    if fund_manager:
        df_all = df_all[df_all['基金经理'].str.contains(fund_manager, na=False)]
    
    # 5. 基金公司筛选
    if fund_company:
        df_all = df_all[df_all['基金公司'].str.contains(fund_company, na=False)]
    
    # 如果没有符合条件的基金，返回空DataFrame
    if df_all.empty:
        return pd.DataFrame()
    
    # 按年化收益率降序排序
    result = df_all.sort_values(by='年化收益率', ascending=False).reset_index(drop=True)
    
    # 格式化显示
    result['年化收益率'] = result['年化收益率'].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "---")
    result['第1年收益率'] = result['第1年收益率'].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "---")
    result['第2年收益率'] = result['第2年收益率'].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "---")
    result['第3年收益率'] = result['第3年收益率'].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "---")
    
    return result.reset_index(drop=True)


def get_fund_managers(data_date=None):
    """
    获取所有基金经理
    
    Args:
        data_date: 数据日期，格式为 "YYYY.MM"
        
    Returns:
        List[str]: 基金经理列表
    """
    managers = set()
    
    # 确定使用的数据日期
    if data_date is None:
        available_dates = get_available_fund_dates()
        if available_dates:
            data_date = available_dates[0]  # 使用最新日期
        else:
            return []  # 如果没有可用日期，返回空列表
    
    try:
        # 读取所有基金类型文件
        fund_types = ["股票型", "混合型", "债券型", "指数型"]
        for fund_type in fund_types:
            file_path = os.path.join(FUND_DATA_PATH, data_date, f"基金_{fund_type}.txt")
            df = safe_read_csv(file_path, sep='\t', encoding='utf-8')
            if not df.empty and '基金经理' in df.columns:
                for manager in df['基金经理'].dropna().unique():
                    if isinstance(manager, str) and manager.strip():
                        # 处理可能包含多个经理的情况
                        for m in manager.split('、'):
                            if m.strip():
                                managers.add(m.strip())
    except Exception as e:
        print(f"读取基金经理信息时出错: {e}")
    
    return sorted(list(managers))


def get_fund_companies(data_date=None):
    """
    获取所有基金公司
    
    Args:
        data_date: 数据日期，格式为 "YYYY.MM"
        
    Returns:
        List[str]: 基金公司列表
    """
    companies = set()
    
    # 确定使用的数据日期
    if data_date is None:
        available_dates = get_available_fund_dates()
        if available_dates:
            data_date = available_dates[0]  # 使用最新日期
        else:
            return []  # 如果没有可用日期，返回空列表
    
    try:
        # 读取所有基金类型文件
        fund_types = ["股票型", "混合型", "债券型", "指数型"]
        for fund_type in fund_types:
            file_path = os.path.join(FUND_DATA_PATH, data_date, f"基金_{fund_type}.txt")
            df = safe_read_csv(file_path, sep='\t', encoding='utf-8')
            if not df.empty and '基金公司' in df.columns:
                for company in df['基金公司'].dropna().unique():
                    if isinstance(company, str) and company.strip():
                        companies.add(company.strip())
    except Exception as e:
        print(f"读取基金公司信息时出错: {e}")
    
    return sorted(list(companies))
