import pandas as pd
import os
import re
from datetime import datetime

def get_available_fund_dates():
    """获取可用的基金数据日期列表"""
    data_dir = os.path.join('data', 'fund')
    if not os.path.exists(data_dir):
        return []
    
    dates = []
    for item in os.listdir(data_dir):
        if os.path.isdir(os.path.join(data_dir, item)) and re.match(r'^\d{4}\.\d{2}$', item):
            dates.append(item)
    
    # 按日期降序排序，最新的在前面
    dates.sort(reverse=True)
    return dates

def fund_filter(min_annual_return=5, min_consecutive_return=5, min_years_listed=3, fund_type="全部", fund_manager=None, fund_company=None, data_date=None):
    """
    基金筛选函数
    
    Args:
        min_annual_return: 最低年化收益率
        min_consecutive_return: 最低连续收益率（所有有效年份都需大于该值）
        min_years_listed: 最低上市年限
        fund_type: 基金类型
        fund_manager: 基金经理筛选（可选）
        fund_company: 基金公司筛选（可选）
        data_date: 数据日期，格式为 'YYYY.MM'，如果为None则使用最新日期
    """
    # 确定使用的数据日期
    if data_date is None:
        available_dates = get_available_fund_dates()
        if not available_dates:
            raise ValueError("未找到可用的基金数据")
        data_date = available_dates[0]  # 使用最新日期
    
    # 读取指定日期的基金数据文件
    data_dir = os.path.join('data', 'fund', data_date)
    
    if not os.path.exists(data_dir):
        raise ValueError(f"未找到日期 {data_date} 的基金数据")
    
    # 根据基金类型选择文件
    if fund_type == "全部":
        files = [f for f in os.listdir(data_dir) if f.endswith('.txt')]
    else:
        files = [f for f in os.listdir(data_dir) if f.endswith('.txt') and fund_type in f]
    
    dfs = []
    for file in files:
        df = pd.read_csv(os.path.join(data_dir, file), sep='\t', encoding='utf-8')
        # 添加基金类型列 - 从文件名提取实际类型
        if fund_type != "全部":
            df['基金类型'] = fund_type
        else:
            # 从文件名提取基金类型
            file_type = file.replace('.txt', '').replace('基金_', '')
            df['基金类型'] = file_type
        dfs.append(df)
    
    if dfs:
        df_all = pd.concat(dfs, ignore_index=True)
    else:
        return pd.DataFrame()
    
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
    
    # 转换所有时间段的收益率字段
    time_periods = ['近1周', '近1月', '近3月', '近6月', '近1年', '近2年', '近3年']
    for period in time_periods:
        df_all[f'{period}_数值'] = df_all[period].map(pct2float)
    
    # 计算每一年的年化收益率
    def calculate_annual_returns(row):
        """计算每一年的单独年化收益率
        
        第1年：直接使用近1年数据
        第2年：(近2年 - 近1年) 的年化收益
        第3年：(近3年 - 近2年) 的年化收益
        不满1年的按最新最大的月份数据进行折算
        """
        # 计算第1年收益率
        year1 = None
        if row.get('近1年_数值') is not None and not pd.isna(row.get('近1年_数值')):
            year1 = row.get('近1年_数值')  # 直接使用近1年的收益率
        elif row.get('近6月_数值') is not None and not pd.isna(row.get('近6月_数值')):
            year1 = row.get('近6月_数值') * 2  # 6个月数据年化
        elif row.get('近3月_数值') is not None and not pd.isna(row.get('近3月_数值')):
            year1 = row.get('近3月_数值') * 4  # 3个月数据年化
        elif row.get('近1月_数值') is not None and not pd.isna(row.get('近1月_数值')):
            year1 = row.get('近1月_数值') * 12  # 1个月数据年化
        
        # 计算第2年收益率
        year2 = None
        if (row.get('近2年_数值') is not None and not pd.isna(row.get('近2年_数值')) and
            row.get('近1年_数值') is not None and not pd.isna(row.get('近1年_数值'))):
            # 近2年总收益转换为单期收益
            total_2y = (1 + row.get('近2年_数值')/100)
            total_1y = (1 + row.get('近1年_数值')/100)
            # 第2年的单期收益
            if total_1y != 0:  # 避免除以零错误
                year2 = (total_2y / total_1y - 1) * 100
            
        # 计算第3年收益率
        year3 = None
        if (row.get('近3年_数值') is not None and not pd.isna(row.get('近3年_数值')) and
            row.get('近2年_数值') is not None and not pd.isna(row.get('近2年_数值'))):
            # 近3年总收益转换为单期收益
            total_3y = (1 + row.get('近3年_数值')/100)
            total_2y = (1 + row.get('近2年_数值')/100)
            # 第3年的单期收益
            if total_2y != 0:  # 避免除以零错误
                year3 = (total_3y / total_2y - 1) * 100
        
        # 返回三年的单独收益率
        return {
            'year1': year1,
            'year2': year2,
            'year3': year3
        }
    
    # 计算每一年的收益率并添加到DataFrame
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
            return sum(years) / len(years)  # 计算平均年化收益率
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
        return 0
    
    df_all['上市年限'] = df_all.apply(calculate_listed_years, axis=1)
    
    # 根据上市年限判断有效年数
    df_all['有效年数'] = df_all['上市年限'].apply(lambda x: min(int(x) if x >= 1 else 0, 3))
    
    # 年化收益率筛选 - 要求每一年都大于指定值
    if min_annual_return > 0:
        # 根据有效年数筛选
        valid_rows = []
        for _, row in df_all.iterrows():
            valid = True
            # 检查第1年
            if row['有效年数'] >= 1 and (pd.isna(row['第1年收益率']) or row['第1年收益率'] < min_annual_return):
                valid = False
            # 检查第2年
            if row['有效年数'] >= 2 and (pd.isna(row['第2年收益率']) or row['第2年收益率'] < min_annual_return):
                valid = False
            # 检查第3年
            if row['有效年数'] >= 3 and (pd.isna(row['第3年收益率']) or row['第3年收益率'] < min_annual_return):
                valid = False
            
            if valid and row['年化收益率'] is not None and not pd.isna(row['年化收益率']):
                valid_rows.append(True)
            else:
                valid_rows.append(False)
        
        df_all = df_all[valid_rows]
    
    # 连续收益率筛选 - 要求所有有效年份都大于指定值
    if min_consecutive_return > 0:
        # 检查是否有足够的历史数据
        df_all = df_all[df_all['上市年限'] >= 1]  # 至少需要1年数据
        
        # 筛选所有有效年份都满足连续收益率要求的基金
        valid_rows = []
        for _, row in df_all.iterrows():
            valid = True
            
            # 检查第1年 (基础年份，必须检查)
            if pd.isna(row['第1年收益率']) or row['第1年收益率'] < min_consecutive_return:
                valid = False
                
            # 检查第2年（如果有效）
            if row['有效年数'] >= 2:
                if pd.isna(row['第2年收益率']) or row['第2年收益率'] < min_consecutive_return:
                    valid = False
                
            # 检查第3年（如果有效）
            if row['有效年数'] >= 3:
                if pd.isna(row['第3年收益率']) or row['第3年收益率'] < min_consecutive_return:
                    valid = False
            
            valid_rows.append(valid)
        
        df_all = df_all[valid_rows]
    
    # 上市年限筛选 - 使用整数年份
    if min_years_listed > 0:
        # 上市年限是float值，需要向下取整后比较
        df_all = df_all[df_all['上市年限'] >= min_years_listed]
    
    # 基金经理筛选
    if fund_manager and '基金经理' in df_all.columns:
        df_all = df_all[df_all['基金经理'].str.contains(fund_manager, na=False)]
    
    # 基金公司筛选
    if fund_company and '基金公司' in df_all.columns:
        df_all = df_all[df_all['基金公司'].str.contains(fund_company, na=False)]
    
    # 选择显示的列，添加各年收益率
    display_cols = ['基金代码', '基金简称', '基金类型', '年化收益率', '上市年限', 
                  '第1年收益率', '第2年收益率', '第3年收益率',
                  '近1年', '近2年', '近3年', '今年来', '成立来']
    
    # 如果有基金经理和基金公司信息，也显示
    if '基金经理' in df_all.columns:
        display_cols.append('基金经理')
    if '基金公司' in df_all.columns:
        display_cols.append('基金公司')
    
    result = df_all[display_cols].copy()
    
    # 格式化显示
    result['年化收益率'] = result['年化收益率'].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "---")
    result['上市年限'] = result['上市年限'].apply(lambda x: f"{int(x)}年" if pd.notna(x) else "---")  # 整数年份显示
    result['第1年收益率'] = result['第1年收益率'].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "---")
    result['第2年收益率'] = result['第2年收益率'].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "---")
    result['第3年收益率'] = result['第3年收益率'].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "---")
    
    return result.reset_index(drop=True)

def get_fund_managers(data_date=None):
    """获取所有基金经理"""
    managers = set()
    
    # 确定使用的数据日期
    if data_date is None:
        available_dates = get_available_fund_dates()
        if not available_dates:
            return []
        data_date = available_dates[0]  # 使用最新日期
    
    data_dir = os.path.join('data', 'fund', data_date)
    
    try:
        for file in os.listdir(data_dir):
            if file.endswith('.txt'):
                df = pd.read_csv(os.path.join(data_dir, file), sep='\t', encoding='utf-8')
                if '基金经理' in df.columns:
                    for mgr in df['基金经理'].dropna().unique():
                        if isinstance(mgr, str) and mgr.strip():
                            # 一个基金可能有多个经理，用分号分隔
                            for m in mgr.split(';'):
                                if m.strip():
                                    managers.add(m.strip())
    except Exception as e:
        print(f"读取基金经理信息时出错: {e}")
    
    return sorted(list(managers))

def get_fund_companies(data_date=None):
    """获取所有基金公司"""
    companies = set()
    
    # 确定使用的数据日期
    if data_date is None:
        available_dates = get_available_fund_dates()
        if not available_dates:
            return []
        data_date = available_dates[0]  # 使用最新日期
    
    data_dir = os.path.join('data', 'fund', data_date)
    
    try:
        for file in os.listdir(data_dir):
            if file.endswith('.txt'):
                df = pd.read_csv(os.path.join(data_dir, file), sep='\t', encoding='utf-8')
                if '基金公司' in df.columns:
                    for company in df['基金公司'].dropna().unique():
                        if isinstance(company, str) and company.strip():
                            companies.add(company.strip())
    except Exception as e:
        print(f"读取基金公司信息时出错: {e}")
    
    return sorted(list(companies))
