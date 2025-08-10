import pandas as pd
import os
import re
from datetime import datetime

def get_available_dates():
    """获取可用的数据日期列表"""
    stock_dir = os.path.join('data', 'stock')
    available_dates = []
    
    if os.path.exists(stock_dir):
        for item in os.listdir(stock_dir):
            if os.path.isdir(os.path.join(stock_dir, item)) and '.' in item:
                # 检查是否是年月格式的目录
                try:
                    year, month = item.split('.')
                    if year.isdigit() and month.isdigit():
                        available_dates.append(item)
                except:
                    continue
    
    # 按日期排序，最新的在前面
    available_dates.sort(reverse=True)
    return available_dates

def get_current_date():
    """获取当前日期，格式为 YYYY.MM"""
    now = datetime.now()
    return f"{now.year}.{now.month:02d}"

def extract_stock_codes(series):
    """
    从各种格式的股票数据中提取规范的股票代码
    
    支持的格式:
    - "SH600519.贵州茅台" -> "600519"
    - "600519.贵州茅台" -> "600519"
    - 纯数字代码，如 "600519" -> "600519"
    - 带逗号的代码，如 "code,SH600519" -> "600519"
    
    Args:
        series: pandas Series，包含股票代码和名称的数据
        
    Returns:
        set: 规范化的股票代码集合，如 {"600519"}
    """
    codes = set()
    for value in series:
        value_str = str(value).replace("'", "").strip()
        
        # 处理"SH600519.贵州茅台"或"600519.贵州茅台"格式
        if '.' in value_str:
            parts = value_str.split('.')
            code_part = parts[0]
            # 移除可能的前缀如SH、SZ
            clean_code = re.sub(r'^(SH|SZ)', '', code_part)
            
            # 如果有名称部分，保存股票名称
            if len(parts) > 1 and hasattr(extract_stock_codes, 'stock_names'):
                name = parts[1].strip()
                if clean_code and name:
                    extract_stock_codes.stock_names[clean_code.zfill(6)] = name
        
        # 处理可能包含逗号的格式
        elif ',' in value_str:
            parts = value_str.split(',')
            if len(parts) > 1:
                # 假设第二部分是代码
                code_part = parts[1].strip()
                clean_code = re.sub(r'^(SH|SZ)', '', code_part)
            else:
                # 只有一部分，可能是纯代码
                clean_code = value_str
        else:
            # 假设是纯代码
            clean_code = value_str
        
        # 确保代码只包含数字
        clean_code = re.sub(r'\D', '', clean_code)
        
        # 标准化为6位数字
        if clean_code:
            codes.add(clean_code.zfill(6))
    
    return codes

def get_available_dates():
    """获取可用的数据日期列表"""
    stock_dir = os.path.join('data', 'stock')
    available_dates = []
    
    if os.path.exists(stock_dir):
        for item in os.listdir(stock_dir):
            if os.path.isdir(os.path.join(stock_dir, item)) and '.' in item:
                # 检查是否是年月格式的目录
                try:
                    year, month = item.split('.')
                    if year.isdigit() and month.isdigit():
                        available_dates.append(item)
                except:
                    continue
    
    # 按日期排序，最新的在前面
    available_dates.sort(reverse=True)
    return available_dates

def get_current_date():
    """获取当前日期，格式为 YYYY.MM"""
    now = datetime.now()
    return f"{now.year}.{now.month:02d}"

# 初始化静态字典用于存储股票名称和行业
extract_stock_codes.stock_names = {}
extract_stock_codes.stock_industries = {}

def stock_filter(selected_types=None, sub_types=None, industry_filter=None, selected_date=None, roe_filter=None, dividend_filter=None):
    """股票筛选函数
    
    Args:
        selected_types: 选择的股票类型列表
        sub_types: 每种类型选择的子类型
        industry_filter: 行业筛选条件
        selected_date: 选择的日期，格式为 "YYYY.MM"，如果为None则使用当前日期
        roe_filter: ROE筛选阈值，如8表示筛选ROE大于等于8%的股票
        dividend_filter: 股息率筛选阈值，如3表示筛选股息率大于等于3%的股票
    """
    if selected_types is None:
        selected_types = []
    if sub_types is None:
        sub_types = {}
    if industry_filter is None:
        industry_filter = []
    
    # 如果没有指定日期，使用当前日期
    if selected_date is None:
        selected_date = get_current_date()
    
    # 股票数据类型定义
    stock_data_types = {
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
                '平均股息': '平均 股息'  # 注意这里有空格
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
    
    # 根据数据类型确定数据目录
    data_dir = os.path.join('data', 'stock', selected_date)
    stock_dir = os.path.join('data', 'stock')
    
    # 存储每种类型的股票代码
    stock_sets = {}
    
    # 预先加载股票基本信息
    stock_info = {}
    
    # 存储额外的列数据
    extra_data = {}
    
    # 首先加载所有可能的股票信息文件以获取完整的股票信息
    load_all_stock_info(stock_info, selected_date)
    
    for stock_type in selected_types:
        if stock_type not in stock_data_types:
            continue
            
        type_config = stock_data_types[stock_type]
        sub_type = sub_types.get(stock_type)
        
        # 确定文件路径
        if type_config['sub_types'] is None:
            if type_config['date_dependent']:
                file_path = os.path.join(data_dir, type_config['file'])
            else:
                file_path = os.path.join(stock_dir, type_config['file'])
        else:
            if sub_type is None:
                sub_type = list(type_config['sub_types'].keys())[0]
            
            if sub_type not in type_config['sub_types']:
                continue
                
            sub_type_value = type_config['sub_types'][sub_type]
            
            if stock_type == '基金重仓股':
                file_path = os.path.join(stock_dir, type_config['file_pattern'].format(sub_type_value))
            else:
                file_path = os.path.join(data_dir, type_config['file_pattern'].format(sub_type_value))
        
        # 读取数据
        try:
            if file_path.endswith('.txt'):
                df = pd.read_csv(file_path, sep='\t', encoding='utf-8')
                if '代码' in df.columns:
                    stock_codes = extract_stock_codes(df['代码'])
                    code_column = '代码'
                else:
                    stock_codes = extract_stock_codes(df.iloc[:, 1])
                    code_column = df.columns[1]
            else:
                df = pd.read_csv(file_path, encoding='utf-8')
                code_columns = ['代码', '股票代码', 'code', 'stock_code', '股票', '序']
                stock_codes = set()
                code_column = None
                
                for col in code_columns:
                    if col in df.columns:
                        stock_codes = extract_stock_codes(df[col])
                        code_column = col
                        break
                
                if not stock_codes:
                    stock_codes = extract_stock_codes(df.iloc[:, 0])
                    code_column = df.columns[0]
            
            # 更新股票信息
            update_stock_info(stock_info, df)
            
            # 提取额外列数据
            if 'extra_columns' in type_config:
                # 打印可用的列名，帮助调试
                print(f"文件 {file_path} 中的列名: {list(df.columns)}")
                
                for display_name, source_column in type_config['extra_columns'].items():
                    # 确保额外数据字典已初始化
                    if display_name not in extra_data:
                        extra_data[display_name] = {}
                    
                    # 尝试从数据文件中提取额外列数据
                    # 对于ROE连续超15%的特殊处理
                    if stock_type == 'ROE连续超15%' and display_name == '平均ROE':
                        # 尝试多种可能的ROE列名
                        roe_columns = ['ROE', 'roe', '平均ROE', '平均roe', 'ROE(%)', 'roe(%)', '平均ROE(%)', '平均roe(%)']
                        found_column = None
                        for col in roe_columns:
                            if col in df.columns:
                                found_column = col
                                break
                        
                        if found_column:
                            print(f"在ROE连续超15%文件中找到ROE列: {found_column}")
                            for _, row in df.iterrows():
                                try:
                                    # 提取股票代码
                                    code_val = row[code_column]
                                    code_str = str(code_val).replace("'", "").strip()
                                    
                                    # 处理可能的代码格式
                                    if '.' in code_str:
                                        code_part = code_str.split('.')[0]
                                        clean_code = re.sub(r'^(SH|SZ)', '', code_part)
                                    elif ',' in code_str:
                                        parts = code_str.split(',')
                                        if len(parts) > 1:
                                            clean_code = re.sub(r'^(SH|SZ)', '', parts[1].strip())
                                        else:
                                            clean_code = code_str
                                    else:
                                        clean_code = re.sub(r'^(SH|SZ)', '', code_str)
                                    
                                    # 确保代码只包含数字并标准化为6位
                                    clean_code = re.sub(r'\D', '', clean_code)
                                    if clean_code:
                                        stock_code = clean_code.zfill(6)
                                        
                                        # 保存额外列数据
                                        value = row[found_column]
                                        if pd.notna(value):
                                            extra_data[display_name][stock_code] = value
                                except Exception as e:
                                    print(f"处理股票 {code_column} 的额外数据时出错: {e}")
                        else:
                            print(f"警告: 在ROE连续超15%文件中未找到ROE列")
                            # 如果找不到ROE列，尝试从当前ROE数据中获取
                            for stock_code in stock_codes:
                                if stock_code in stock_info and '当前ROE' in stock_info[stock_code]:
                                    extra_data[display_name][stock_code] = stock_info[stock_code]['当前ROE']
                    # 对于北上持股的特殊处理
                    elif stock_type == 'ROE连续超15%' and display_name == '北上持股':
                        # 首先检查文件中是否已经有北上持股列
                        if '北上持股' in df.columns:
                            print(f"在ROE连续超15%文件中找到北上持股列")
                            for _, row in df.iterrows():
                                try:
                                    # 提取股票代码
                                    code_val = row[code_column]
                                    code_str = str(code_val).replace("'", "").strip()
                                    
                                    # 处理可能的代码格式
                                    if '.' in code_str:
                                        code_part = code_str.split('.')[0]
                                        clean_code = re.sub(r'^(SH|SZ)', '', code_part)
                                    elif ',' in code_str:
                                        parts = code_str.split(',')
                                        if len(parts) > 1:
                                            clean_code = re.sub(r'^(SH|SZ)', '', parts[1].strip())
                                        else:
                                            clean_code = code_str
                                    else:
                                        clean_code = re.sub(r'^(SH|SZ)', '', code_str)
                                    
                                    # 确保代码只包含数字并标准化为6位
                                    clean_code = re.sub(r'\D', '', clean_code)
                                    if clean_code:
                                        stock_code = clean_code.zfill(6)
                                        
                                        # 保存额外列数据
                                        value = row['北上持股']
                                        if pd.notna(value):
                                            extra_data[display_name][stock_code] = value
                                except Exception as e:
                                    print(f"处理股票 {code_column} 的北上持股数据时出错: {e}")
                        # 如果文件中没有北上持股列，则从北上资金持股数据中获取
                        else:
                            print(f"在ROE连续超15%文件中未找到北上持股列，尝试从北上资金持股数据获取")
                            if '北上资金持股' in stock_sets:
                                for stock_code in stock_codes:
                                    if stock_code in stock_sets['北上资金持股']:
                                        extra_data[display_name][stock_code] = '是'
                                    else:
                                        extra_data[display_name][stock_code] = '否'
                    # 常规处理其他列
                    elif source_column in df.columns:
                        for _, row in df.iterrows():
                            try:
                                # 提取股票代码
                                code_val = row[code_column]
                                code_str = str(code_val).replace("'", "").strip()
                                
                                # 处理可能的代码格式
                                if '.' in code_str:
                                    code_part = code_str.split('.')[0]
                                    clean_code = re.sub(r'^(SH|SZ)', '', code_part)
                                elif ',' in code_str:
                                    parts = code_str.split(',')
                                    if len(parts) > 1:
                                        clean_code = re.sub(r'^(SH|SZ)', '', parts[1].strip())
                                    else:
                                        clean_code = code_str
                                else:
                                    clean_code = re.sub(r'^(SH|SZ)', '', code_str)
                                
                                # 确保代码只包含数字并标准化为6位
                                clean_code = re.sub(r'\D', '', clean_code)
                                if clean_code:
                                    stock_code = clean_code.zfill(6)
                                    
                                    # 保存额外列数据
                                    value = row[source_column]
                                    if pd.notna(value):
                                        extra_data[display_name][stock_code] = value
                            except Exception as e:
                                print(f"处理股票 {code_column} 的额外数据时出错: {e}")
                    else:
                        print(f"警告: 在{stock_type}文件中未找到列 '{source_column}'，可用列: {list(df.columns)}")
            
            stock_sets[stock_type] = stock_codes
            
        except Exception as e:
            print(f"读取文件 {file_path} 时出错: {e}")
            stock_sets[stock_type] = set()
    
    # 找出同时满足所有条件的股票
    if not stock_sets:
        return pd.DataFrame()
    
    common_stocks = set.intersection(*stock_sets.values())
    
    if not common_stocks:
        return pd.DataFrame()
    
    # 构建结果数据
    result_data = []
    for stock_code in common_stocks:
        # 基本信息
        row = {'股票代码': stock_code}
        
        # 添加股票名称和行业
        if stock_code in stock_info:
            row['股票名称'] = stock_info[stock_code].get('名称', '')
            row['所属行业'] = stock_info[stock_code].get('行业', '')
        else:
            row['股票名称'] = ''
            row['所属行业'] = ''
        
        # 添加默认显示列
        row['当前ROE'] = stock_info[stock_code].get('当前ROE', '')
        row['扣非PE'] = stock_info[stock_code].get('扣非PE', '')
        row['PB'] = stock_info[stock_code].get('PB', '')
        row['股息'] = stock_info[stock_code].get('股息', '')
        row['今年来'] = stock_info[stock_code].get('今年来', '')
        
        # 添加额外列数据
        for column_name, data_dict in extra_data.items():
            if stock_code in data_dict:
                row[column_name] = data_dict[stock_code]
            else:
                row[column_name] = ''
        
        # 不再添加筛选标记列，因为已经有了对应的额外信息列
        
        # 行业筛选
        skip_row = False
        if industry_filter and row['所属行业'] and row['所属行业'] not in industry_filter:
            skip_row = True
        
        if not skip_row:
            result_data.append(row)
    
    result_df = pd.DataFrame(result_data)
    
    # 应用ROE筛选
    if roe_filter is not None and not result_df.empty:
        filtered_rows = []
        for _, row in result_df.iterrows():
            roe_value = None
            
            # 尝试从不同列获取ROE值
            if '平均ROE' in row and row['平均ROE']:
                try:
                    roe_str = str(row['平均ROE']).replace('%', '')
                    roe_value = float(roe_str) if roe_str and roe_str != '-' else None
                except:
                    pass
            
            if roe_value is None and '当前ROE' in row and row['当前ROE']:
                try:
                    roe_str = str(row['当前ROE']).replace('%', '')
                    roe_value = float(roe_str) if roe_str and roe_str != '-' else None
                except:
                    pass
            
            if roe_value is None and 'ROE' in row and row['ROE']:
                try:
                    roe_str = str(row['ROE']).replace('%', '')
                    roe_value = float(roe_str) if roe_str and roe_str != '-' else None
                except:
                    pass
                    
            # 判断是否符合筛选条件
            if roe_value is not None and roe_value >= roe_filter:
                filtered_rows.append(row)
        
        if filtered_rows:
            result_df = pd.DataFrame(filtered_rows)
        else:
            return pd.DataFrame()  # 如果没有符合条件的行，返回空DataFrame
    
    # 应用股息筛选
    if dividend_filter is not None and not result_df.empty:
        filtered_rows = []
        for _, row in result_df.iterrows():
            dividend_value = None
            
            # 尝试从不同列获取股息值
            if '平均股息' in row and row['平均股息']:
                try:
                    dividend_str = str(row['平均股息']).replace('%', '')
                    dividend_value = float(dividend_str) if dividend_str and dividend_str != '-' else None
                except:
                    pass
            
            if dividend_value is None and '股息' in row and row['股息']:
                try:
                    dividend_str = str(row['股息']).replace('%', '')
                    dividend_value = float(dividend_str) if dividend_str and dividend_str != '-' else None
                except:
                    pass
                    
            # 判断是否符合筛选条件
            if dividend_value is not None and dividend_value >= dividend_filter:
                filtered_rows.append(row)
        
        if filtered_rows:
            result_df = pd.DataFrame(filtered_rows)
        else:
            return pd.DataFrame()  # 如果没有符合条件的行，返回空DataFrame
    
    # 设置列顺序
    base_cols = ['股票代码', '股票名称', '所属行业']
    default_cols = ['当前ROE', '扣非PE', 'PB', '股息', '今年来']
    
    # 添加额外列，但避免重复
    extra_cols = []
    for col in extra_data.keys():
        # 避免重复列 - 特别处理'ROE'和'当前ROE'
        if col not in default_cols and not (col == 'ROE' and '当前ROE' in default_cols):
            extra_cols.append(col)
    
    # 最终列顺序 - 不再包含股票类型列
    cols = base_cols + default_cols + extra_cols
    
    # 确保所有列都在DataFrame中
    valid_cols = [col for col in cols if col in result_df.columns]
    result_df = result_df[valid_cols]
    
    return result_df

def load_all_stock_info(stock_info, selected_date):
    """加载所有股票的基本信息"""
    data_dir = os.path.join('data', 'stock', selected_date)
    
    # 从多个文件中读取股票名称和行业信息
    info_files = [
        'Hot_stocks_in_the_past_day.csv',
        'Hot_stocks_in_the_past_week.csv',
        'Hot_stocks_in_the_past_month.csv',
        'Hot_stocks_in_the_past_year.csv',
        'Hot_stocks_in_the_past_three_days.csv',
        'Hot_stocks_in_the_past_three_months.csv',
        'Hot_stocks_in_the_past_six_months.csv',
        'Hot_stocks_in_the_past_three_years.csv',
        'The_highest_proportion_of_northbound_funds_held.csv',
        'The_cheapest_stocks.csv',
        'Highest_ROE_ranking.csv',
        'Highest_dividend_yield_in_the_past_three_years.csv',
        'Highest_dividend_yield_in_the_past_two_years.csv',
        'Highest_dividend_yield_in_the_past_five_years.csv',
        'The_cheapest_non-bank_stocks.csv',
        'The_cheapest_non-cyclical_stocks.csv',
        'The_cheapest_non-cyclical_non-bank_stocks.csv',
        'PEG_ranking_in_the_past_year.csv',
        'PEG_ranking_in_the_past_three_years.csv',
        'PEG_ranking_in_the_past_five_years.csv',
        'Research_report_recommends_hot_stocks_in_the_past_week.csv',
        'Research_report_recommends_hot_stocks_in_the_past_year.csv',
        'Research_report_recommends_hot_stocks_in_the_past_six_months.csv',
        'Research_report_recommends_hot_stocks_in_the_past_three_weeks.csv',
        'Research_report_recommends_hot_stocks_in_the_past_two_months.csv',
        'ROE_exceeded_15p_three_consecutive_years.csv',
        'ROE_exceeded_15p_five_consecutive_years.csv'
    ]
    
    # 尝试从所有可能的文件中提取信息
    for file_name in info_files:
        file_path = os.path.join(data_dir, file_name)
        if not os.path.exists(file_path):
            continue
        
        try:
            if file_name == 'Hot_stocks_in_the_past_day.csv':
                # 特殊处理热门股票文件，直接解析内容
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # 跳过标题行
                for line in lines[1:]:
                    line = line.strip().replace("'", "")
                    if not line:
                        continue
                    
                    parts = line.split(',')
                    if len(parts) >= 13:  # 确保行有足够的列
                        # 第2列是股票代码和名称，格式如 "SZ002097.山河智能"
                        code_name = parts[1].strip()
                        if '.' in code_name:
                            code_part, name_part = code_name.split('.', 1)
                            clean_code = re.sub(r'^(SH|SZ)', '', code_part)
                            if clean_code.isdigit():
                                code = clean_code.zfill(6)
                                name = name_part.strip()
                                industry = parts[12].strip() if len(parts) > 12 else ""
                                
                                if code not in stock_info:
                                    stock_info[code] = {'名称': name, '行业': industry}
                                else:
                                    if not stock_info[code]['名称']:
                                        stock_info[code]['名称'] = name
                                    if not stock_info[code]['行业'] and industry:
                                        stock_info[code]['行业'] = industry
            else:
                # 常规处理其他文件
                df = pd.read_csv(file_path, encoding='utf-8')
                update_stock_info(stock_info, df)
        except Exception as e:
            print(f"读取文件 {file_name} 时出错: {e}")
    
    # 尝试从基金重仓股文件中提取信息
    fund_holdings_files = [
        'Fund_holdings_ranking_2025Q2.csv',
        'Fund_holdings_ranking_2025Q1.csv',
        'Fund_holdings_ranking_2024Q4.csv',
        'Fund_holdings_ranking_2024Q3.csv',
        'Fund_holdings_ranking_2024Q2.csv'
    ]
    
    stock_dir = os.path.join('data', 'stock')
    for file_name in fund_holdings_files:
        file_path = os.path.join(stock_dir, file_name)
        if not os.path.exists(file_path):
            continue
        
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
            update_stock_info(stock_info, df)
        except Exception as e:
            print(f"读取文件 {file_name} 时出错: {e}")
    
    # 尝试从TXT文件中提取信息
    txt_files = [
        'Strongest_control_top200.txt',
        'The_lowest_shareholders_in_history_top200.txt'
    ]
    
    for file_name in txt_files:
        file_path = os.path.join(data_dir, file_name)
        if not os.path.exists(file_path):
            continue
        
        try:
            df = pd.read_csv(file_path, sep='\t', encoding='utf-8')
            update_stock_info(stock_info, df)
        except Exception as e:
            print(f"读取文件 {file_name} 时出错: {e}")

def update_stock_info(stock_info, df):
    """从数据帧中提取股票信息并更新stock_info字典"""
    # 检查是否有行业列
    has_industry_column = False
    industry_column = None
    for col in ['行业', '所属行业', '申万行业']:
        if col in df.columns:
            has_industry_column = True
            industry_column = col
            break
    
    # 检查是否有默认显示列
    default_columns = {
        '当前ROE': ['当前ROE', 'ROE', 'roe'],
        '扣非PE': ['扣非PE', '扣非pe', 'PE', 'pe'],
        'PB': ['PB', 'pb'],
        '股息': ['股息', '股息率', '股息%'],
        '今年来': ['今年来', '今年涨幅', '年初至今']
    }
    
    # 映射实际列名到标准列名
    column_mapping = {}
    for std_col, possible_cols in default_columns.items():
        for col in possible_cols:
            if col in df.columns:
                column_mapping[col] = std_col
                break
    
    # 尝试提取股票信息
    for _, row in df.iterrows():
        code = ""
        name = ""
        industry = ""
        
        # 首先查找可能包含股票代码的列
        code_columns = ['序', '代码', '股票代码', '股票', '股票代码', '股票代码,股票名称', '序号']
        for col in code_columns:
            if col in df.columns:
                col_data = str(row[col]).replace("'", "").strip()
                if not col_data or col_data == 'nan':
                    continue
                    
                # 处理"代码.名称"格式 (如 "600519.贵州茅台" 或 "SH600519.贵州茅台")
                if '.' in col_data:
                    code_part, extracted_name = col_data.split('.', 1)
                    clean_code = re.sub(r'^(SH|SZ)', '', code_part)
                    clean_code = re.sub(r'\D', '', clean_code)
                    
                    if clean_code:
                        code = clean_code.zfill(6)
                    if extracted_name and extracted_name.strip():
                        name = extracted_name.strip()
                    break
                    
                # 处理逗号分隔格式
                elif ',' in col_data:
                    parts = col_data.split(',')
                    if len(parts) > 1:
                        # 第一部分可能是序号，第二部分可能是代码
                        if parts[0].isdigit() and (parts[1].isdigit() or re.match(r'^(SH|SZ)\d+$', parts[1])):
                            clean_code = re.sub(r'^(SH|SZ)', '', parts[1])
                            clean_code = re.sub(r'\D', '', clean_code)
                            if clean_code:
                                code = clean_code.zfill(6)
                                # 如果有第三部分，可能是名称
                                if len(parts) > 2 and parts[2].strip():
                                    name = parts[2].strip()
                                break
                
                # 处理纯数字代码或带前缀代码
                elif col_data.isdigit() or re.match(r'^(SH|SZ)\d+$', col_data):
                    clean_code = re.sub(r'^(SH|SZ)', '', col_data)
                    clean_code = re.sub(r'\D', '', clean_code)
                    if clean_code:
                        code = clean_code.zfill(6)
                        break
        
        # 如果还没有找到名称，尝试从可能的名称列获取
        if not name:
            name_columns = ['股票名称', '名称', '股票', '股票名称,股票代码', '股票名称,所属行业']
            for col in name_columns:
                if col in df.columns:
                    name_data = str(row[col]).replace("'", "").strip()
                    if name_data and name_data != 'nan':
                        # 处理可能包含代码的格式
                        if '.' in name_data:
                            parts = name_data.split('.')
                            if len(parts) > 1:
                                name = parts[1].strip()
                        elif ',' in name_data:
                            parts = name_data.split(',')
                            name = parts[0].strip()
                        else:
                            name = name_data
                        break
        
        # 获取行业信息
        if has_industry_column:
            industry_data = str(row[industry_column]).strip()
            if industry_data and industry_data != 'nan':
                industry = industry_data
                    
        # 如果有股票名称但没有代码，尝试从名称中提取代码
        if name and not code:
            # 检查名称是否包含代码信息
            code_match = re.search(r'(\d{6})', name)
            if code_match:
                code = code_match.group(1)
        
        # 只有当我们有股票代码时才添加或更新信息
        if code:
            if code not in stock_info:
                stock_info[code] = {'名称': name, '行业': industry}
            else:
                # 如果已有记录，但缺少名称或行业，则补充
                if not stock_info[code]['名称'] and name:
                    stock_info[code]['名称'] = name
                if not stock_info[code]['行业'] and industry:
                    stock_info[code]['行业'] = industry
            
            # 提取默认显示列数据
            for src_col, dst_col in column_mapping.items():
                if src_col in df.columns:
                    try:
                        value = row[src_col]
                        if pd.notna(value):
                            stock_info[code][dst_col] = value
                    except Exception as e:
                        print(f"提取 {code} 的 {src_col} 数据时出错: {e}")

def get_stock_type_options():
    """获取股票类型选项"""
    return [
        '北上资金持股',
        '热门股票', 
        '最便宜股票',
        'ROE排名',
        'ROE连续超15%',
        'PEG排名',
        '股息率排名',
        '控盘度排名',
        '股东数最少排名',
        '基金重仓股',
        '券商研报推荐'
    ]

def get_sub_type_options(stock_type):
    """获取指定股票类型的子类型选项"""
    sub_type_options = {
        '热门股票': ['近1天', '近3天', '近1周', '近1月', '近3月', '近6月', '近1年', '近3年'],
        '最便宜股票': ['全部', '不包括周期性股票', '不包括银行股', '不包括周期性股票和银行股'],
        'ROE连续超15%': ['连续3年', '连续5年'],
        'PEG排名': ['近1年', '近3年', '近5年'],
        '股息率排名': ['近2年', '近3年', '近5年'],
        '基金重仓股': ['2025Q2', '2025Q1', '2024Q4', '2024Q3', '2024Q2'],
        '券商研报推荐': ['近1周', '近3周', '近2月', '近6月', '近1年']
    }
    
    return sub_type_options.get(stock_type, [])

def get_industry_options(selected_date=None):
    """获取所有可用行业选项"""
    industries = set()
    
    try:
        # 如果没有指定日期，使用当前日期
        if selected_date is None:
            selected_date = get_current_date()
            
        # 从多个文件中读取行业信息
        data_dir = os.path.join('data', 'stock', selected_date)
        
        # 定义可能包含行业信息的文件列表
        industry_files = [
            'Hot_stocks_in_the_past_day.csv',
            'Hot_stocks_in_the_past_week.csv',
            'Hot_stocks_in_the_past_month.csv',
            'Hot_stocks_in_the_past_three_months.csv',
            'Hot_stocks_in_the_past_six_months.csv',
            'Hot_stocks_in_the_past_year.csv',
            'Hot_stocks_in_the_past_three_days.csv',
            'Hot_stocks_in_the_past_three_years.csv',
            'The_highest_proportion_of_northbound_funds_held.csv',
            'The_cheapest_stocks.csv',
            'The_cheapest_non-bank_stocks.csv',
            'The_cheapest_non-cyclical_stocks.csv',
            'The_cheapest_non-cyclical_non-bank_stocks.csv',
            'Highest_ROE_ranking.csv',
            'PEG_ranking_in_the_past_year.csv',
            'PEG_ranking_in_the_past_three_years.csv',
            'PEG_ranking_in_the_past_five_years.csv'
        ]
        
        for file in industry_files:
            file_path = os.path.join(data_dir, file)
            if os.path.exists(file_path):
                try:
                    # 特殊处理热门股票文件
                    if file == 'Hot_stocks_in_the_past_day.csv':
                        with open(file_path, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                        
                        # 跳过标题行
                        for line in lines[1:]:
                            line = line.strip().replace("'", "")
                            if not line:
                                continue
                            
                            parts = line.split(',')
                            if len(parts) >= 13:  # 确保行有足够的列
                                industry = parts[12].strip()
                                if industry and industry != 'nan':
                                    industries.add(industry)
                    else:
                        # 常规处理其他文件
                        df = pd.read_csv(file_path, encoding='utf-8')
                        industry_columns = ['行业', '所属行业', '申万行业']
                        for col in industry_columns:
                            if col in df.columns:
                                # 提取所有非空行业
                                curr_industries = [ind for ind in df[col].unique() if pd.notna(ind) and str(ind).strip() and str(ind) != 'nan']
                                industries.update(curr_industries)
                except Exception as e:
                    print(f"读取文件 {file} 的行业信息时出错: {e}")
                    continue
    
    except Exception as e:
        print(f"读取行业信息时出错: {e}")
    
    # 转换为排序列表
    industry_list = sorted(list(industries))
    return industry_list