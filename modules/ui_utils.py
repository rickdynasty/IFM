"""
UI工具模块
提供UI相关的工具函数，如表格显示、格式化等
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Optional, Any, Union
from modules.config import TABLE_CONFIG, COLUMN_WIDTH, EXTERNAL_LINKS, FORMAT_CONFIG


def format_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    格式化DataFrame，处理数值格式等
    
    Args:
        df: 原始DataFrame
        
    Returns:
        pd.DataFrame: 格式化后的DataFrame
    """
    # 创建一个副本以避免修改原始数据
    result = df.copy()
    
    # 清理数据中的单引号
    for col in result.columns:
        if isinstance(result[col].dtype, object):  # 只处理字符串类型的列
            result[col] = result[col].apply(lambda x: str(x).replace("'", "") if isinstance(x, str) else x)
    
    # 格式化百分比列
    for col in FORMAT_CONFIG["percent_columns"]:
        if col in result.columns:
            result[col] = result[col].apply(format_percent)
    
    # 格式化金额列
    for col in FORMAT_CONFIG["money_columns"]:
        if col in result.columns:
            result[col] = result[col].apply(format_money)
    
    # 格式化浮点数列
    for col in FORMAT_CONFIG["float_columns"]:
        if col in result.columns:
            result[col] = result[col].apply(format_float)
    
    # 格式化整数列
    for col in FORMAT_CONFIG["int_columns"]:
        if col in result.columns:
            result[col] = result[col].apply(format_int)
    
    return result


def format_percent(value: Any) -> str:
    """格式化为百分比"""
    try:
        if pd.isna(value) or value == '' or value == '-':
            return "-"
        
        # 如果已经是百分比格式
        if isinstance(value, str) and '%' in value:
            return value
        
        # 转换为百分比
        return f"{float(value):.2f}%"
    except:
        return str(value)


def format_money(value: Any) -> str:
    """格式化为金额"""
    try:
        if pd.isna(value) or value == '' or value == '-':
            return "-"
        
        # 如果已经包含"亿"
        if isinstance(value, str) and '亿' in value:
            return value
        
        # 转换为金额
        return f"{float(value):.2f}亿"
    except:
        return str(value)


def format_float(value: Any) -> str:
    """格式化为浮点数"""
    try:
        if pd.isna(value) or value == '' or value == '-':
            return "-"
        
        return f"{float(value):.2f}"
    except:
        return str(value)


def format_int(value: Any) -> str:
    """格式化为整数"""
    try:
        if pd.isna(value) or value == '' or value == '-':
            return "-"
        
        return f"{int(float(value))}"
    except:
        return str(value)


def add_stock_links(df: pd.DataFrame) -> pd.DataFrame:
    """
    为股票代码和名称添加链接
    
    Args:
        df: 原始DataFrame
        
    Returns:
        pd.DataFrame: 添加链接后的DataFrame
    """
    if '股票代码' not in df.columns or '股票名称' not in df.columns:
        return df
    
    result = df.copy()
    
    # 为股票代码添加链接
    result['股票代码'] = result['股票代码'].apply(
        lambda x: f'<a href="{EXTERNAL_LINKS["stock"]["同花顺"].format(code=str(x).zfill(6))}" target="_blank">{x}</a>'
    )
    
    # 为股票名称添加链接
    for idx, row in result.iterrows():
        code = str(row['股票代码']).split('>')[1].split('<')[0].zfill(6)  # 提取代码文本
        prefix = "SH" if str(code).startswith(('6', '9')) else "SZ"
        result.at[idx, '股票名称'] = f'<a href="{EXTERNAL_LINKS["stock"]["雪球"].format(exchange=prefix, code=code)}" target="_blank">{row["股票名称"]}</a>'
    
    return result


def add_fund_links(df: pd.DataFrame) -> pd.DataFrame:
    """
    为基金代码和名称添加链接
    
    Args:
        df: 原始DataFrame
        
    Returns:
        pd.DataFrame: 添加链接后的DataFrame
    """
    if '基金代码' not in df.columns or '基金简称' not in df.columns:
        return df
    
    result = df.copy()
    
    # 为基金代码添加链接
    result['基金代码'] = result['基金代码'].apply(
        lambda x: f'<a href="{EXTERNAL_LINKS["fund"]["同花顺"].format(code=str(x).zfill(6))}" target="_blank">{x}</a>'
    )
    
    # 为基金简称添加链接
    for idx, row in result.iterrows():
        code = str(row['基金代码']).split('>')[1].split('<')[0].zfill(6)  # 提取代码文本
        result.at[idx, '基金简称'] = f'<a href="{EXTERNAL_LINKS["fund"]["东方财富"].format(code=code)}" target="_blank">{row["基金简称"]}</a>'
    
    return result


def apply_color_style(df: pd.DataFrame) -> pd.DataFrame:
    """
    应用颜色样式，如正负值颜色
    
    Args:
        df: 原始DataFrame
        
    Returns:
        pd.DataFrame: 应用样式后的DataFrame
    """
    # 定义样式函数
    def color_values(val, col_name):
        try:
            # 处理百分比格式
            if isinstance(val, str) and '%' in val:
                val_num = float(val.replace('%', '').strip())
                if val_num < 0:
                    return f'color: {TABLE_CONFIG["negative_color"]}'
                elif col_name == '今年来' and val_num > 0:
                    return f'color: {TABLE_CONFIG["positive_color"]}'
            # 处理普通数字
            elif isinstance(val, (int, float)):
                if val < 0:
                    return f'color: {TABLE_CONFIG["negative_color"]}'
                elif col_name == '今年来' and val > 0:
                    return f'color: {TABLE_CONFIG["positive_color"]}'
            # 处理可能是数字的字符串
            elif isinstance(val, str):
                try:
                    val_num = float(val)
                    if val_num < 0:
                        return f'color: {TABLE_CONFIG["negative_color"]}'
                    elif col_name == '今年来' and val_num > 0:
                        return f'color: {TABLE_CONFIG["positive_color"]}'
                except:
                    pass
        except:
            pass
        return ''
    
    # 创建样式函数
    def apply_styles(df_or_series):
        if isinstance(df_or_series, pd.Series):
            # 处理Series对象（单列）
            col_name = df_or_series.name
            return pd.Series([color_values(x, col_name) for x in df_or_series], index=df_or_series.index)
        else:
            # 处理DataFrame对象（多列）
            styles = pd.DataFrame('', index=df_or_series.index, columns=df_or_series.columns)
            for col in df_or_series.columns:
                styles[col] = df_or_series[col].apply(lambda x: color_values(x, col))
            return styles
    
    # 应用样式
    return df.style.apply(apply_styles)


def display_table(df: pd.DataFrame, data_type: str = 'stock') -> None:
    """
    显示带有固定表头的表格
    
    Args:
        df: 要显示的DataFrame
        data_type: 数据类型，'stock'或'fund'
    """
    if df.empty:
        st.warning("没有找到符合条件的数据，请调整筛选条件。")
        return
    
    # 格式化数据
    formatted_df = format_dataframe(df)
    
    # 精简基金表格列，解决列太多的问题
    if data_type == 'fund':
        # 定义要保留的列
        essential_columns = [
            '序号', '基金代码', '基金简称', '基金类型', '年化收益率', '第1年收益率', 
            '第2年收益率', '第3年收益率', '今年来', '近1年', '近3年', '上市年限'
        ]
        
        # 如果有基金经理和基金公司列，也保留
        if '基金经理' in formatted_df.columns:
            essential_columns.append('基金经理')
        if '基金公司' in formatted_df.columns:
            essential_columns.append('基金公司')
            
        # 只保留必要的列
        available_columns = [col for col in essential_columns if col in formatted_df.columns]
        display_df = formatted_df[available_columns].copy()
    else:
        # 股票表格保持原样
        display_df = formatted_df.copy()
    
    # 添加CSS样式
    st.markdown(f"""
    <style>
    .fixed-table {{
        width: auto !important;
        min-width: 100%;  /* 最小宽度100%，确保至少填满容器 */
        border-collapse: collapse;
        table-layout: fixed;
        font-size: 13px;  /* 减小字体大小 */
    }}
    .fixed-table-container {{
        max-height: {TABLE_CONFIG['height']}px;
        overflow-x: auto;
        overflow-y: auto;
        width: 100%;  /* 确保容器宽度占满 */
    }}
    .fixed-table thead {{
        position: sticky;
        top: 0;
        background-color: {TABLE_CONFIG['header_bg_color']};
        z-index: 100;
    }}
    .fixed-table th {{
        padding: 6px 4px;  /* 减小内边距 */
        text-align: center;
        font-weight: bold;
        border-bottom: 2px solid {TABLE_CONFIG['border_color']};
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        font-size: 13px;  /* 表头字体大小 */
    }}
    .fixed-table td {{
        padding: 4px;  /* 减小单元格内边距 */
        border-bottom: 1px solid {TABLE_CONFIG['border_color']};
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        text-align: center;  /* 居中对齐 */
    }}
    .fixed-table a {{
        color: {TABLE_CONFIG['link_color']};
        text-decoration: none;
    }}
    .fixed-table a:hover {{
        text-decoration: underline;
    }}
    .positive-value {{
        color: {TABLE_CONFIG['positive_color']};
    }}
    .negative-value {{
        color: {TABLE_CONFIG['negative_color']};
    }}
    /* 设置特定列的宽度 */
    .col-序号 {{ width: 40px; }}
    
    /* 基金表格列宽 */
    .col-基金代码 {{ width: 70px; }}
    .col-基金简称 {{ width: 110px; }}
    .col-基金类型 {{ width: 70px; }}
    .col-年化收益率 {{ width: 80px; }}
    .col-第1年收益率, .col-第2年收益率, .col-第3年收益率 {{ width: 80px; }}
    .col-今年来, .col-近1年, .col-近3年 {{ width: 60px; }}
    .col-上市年限 {{ width: 60px; }}
    .col-基金经理, .col-基金公司 {{ width: 90px; }}
    
    /* 股票表格列宽 */
    .col-股票代码 {{ width: 80px; }}
    .col-股票名称 {{ width: 80px; }}
    .col-股息率 {{ width: 50px; }}
    .col-北上持股 {{ width: 90px; }}
    .col-当前ROE {{ width: 60px; }}
    .col-平均ROE {{ width: 60px; }}
    .col-PE.扣非 {{ width: 60px; }}
    .col-今年来 {{ width: 60px; }}
    .col-行业 {{ width: 70px; }}
    </style>
    """, unsafe_allow_html=True)
    
    # 手动构建HTML表格
    html_parts = ['<div class="fixed-table-container"><table class="fixed-table">']
    
    # 添加表头
    html_parts.append('<thead>')
    html_parts.append('<tr>')
    for col in display_df.columns:
        # 为每列添加特定的CSS类，强制应用列宽
        html_parts.append(f'<th class="col-{col}" style="width: var(--col-width, auto) !important;">{col}</th>')
    html_parts.append('</tr>')
    html_parts.append('</thead>')
    
    # 添加表格内容
    html_parts.append('<tbody>')
    
    # 遍历数据行
    for idx, row in display_df.iterrows():
        html_parts.append('<tr>')
        
        # 遍历每一列
        for col_idx, col_name in enumerate(display_df.columns):
            value = row[col_name]
            
            # 特殊处理股票代码和名称列，添加链接
            if data_type == 'stock':
                if col_name == '股票代码':
                    code = str(value).zfill(6)
                    value = f'<a href="{EXTERNAL_LINKS["stock"]["同花顺"].format(code=code)}" target="_blank">{value}</a>'
                elif col_name == '股票名称':
                    code = str(row['股票代码']).zfill(6)
                    prefix = "SH" if str(code).startswith(('6', '9')) else "SZ"
                    value = f'<a href="{EXTERNAL_LINKS["stock"]["雪球"].format(exchange=prefix, code=code)}" target="_blank">{value}</a>'
            elif data_type == 'fund':
                if col_name == '基金代码':
                    code = str(value).zfill(6)
                    value = f'<a href="{EXTERNAL_LINKS["fund"]["同花顺"].format(code=code)}" target="_blank">{value}</a>'
                elif col_name == '基金简称':
                    code = str(row['基金代码']).zfill(6)
                    value = f'<a href="{EXTERNAL_LINKS["fund"]["东方财富"].format(code=code)}" target="_blank">{value}</a>'
            
            # 添加颜色样式
            css_class = f' class="col-{col_name}'
            if isinstance(value, str):
                if '%' in value:
                    try:
                        num_value = float(value.replace('%', ''))
                        if num_value < 0:
                            css_class += ' negative-value'
                        elif (col_name == '今年来' or '收益率' in col_name) and num_value > 0:
                            css_class += ' positive-value'
                    except:
                        pass
            css_class += '"'
            
            # 添加单元格，并强制应用列宽样式
            html_parts.append(f'<td{css_class} style="width: var(--col-width, auto) !important;">{value}</td>')
        
        html_parts.append('</tr>')
    
    html_parts.append('</tbody>')
    html_parts.append('</table></div>')
    
    # 显示表格
    st.markdown(''.join(html_parts), unsafe_allow_html=True)


def display_statistics(df: pd.DataFrame, data_type: str = 'stock') -> None:
    """
    显示统计信息
    
    Args:
        df: 要统计的DataFrame
        data_type: 数据类型，'stock'或'fund'
    """
    if df.empty:
        return
    
    st.markdown("<h3 style='margin-top:0rem; padding-top:0rem; margin-bottom:0rem;'>📊 筛选结果统计</h3>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("符合条件的数量", len(df))
    
    if data_type == 'fund':
        with col2:
            try:
                avg_return = df['年化收益率'].str.replace('%', '').astype(float).mean()
                st.metric("平均年化收益率", f"{avg_return:.2f}%")
            except:
                st.metric("平均年化收益率", "---")
        
        with col3:
            try:
                max_return = df['年化收益率'].str.replace('%', '').astype(float).max()
                st.metric("最高年化收益率", f"{max_return:.2f}%")
            except:
                st.metric("最高年化收益率", "---")
        
        with col4:
            try:
                min_return = df['年化收益率'].str.replace('%', '').astype(float).min()
                st.metric("最低年化收益率", f"{min_return:.2f}%")
            except:
                st.metric("最低年化收益率", "---")
    
    elif data_type == 'stock':
        with col2:
            if '行业' in df.columns:
                industry_count = df['行业'].nunique()
                st.metric("行业数量", industry_count)
            else:
                st.metric("行业数量", "---")
        
        with col3:
            if '今年来' in df.columns:
                try:
                    avg_ytd = df['今年来'].str.replace('%', '').astype(float).mean()
                    st.metric("平均今年来涨幅", f"{avg_ytd:.2f}%")
                except:
                    st.metric("平均今年来涨幅", "---")
            else:
                st.metric("平均今年来涨幅", "---")
        
        with col4:
            if '当前ROE' in df.columns:
                try:
                    avg_roe = df['当前ROE'].str.replace('%', '').astype(float).mean()
                    st.metric("平均ROE", f"{avg_roe:.2f}%")
                except:
                    st.metric("平均ROE", "---")
            elif 'ROE' in df.columns:
                try:
                    avg_roe = df['ROE'].str.replace('%', '').astype(float).mean()
                    st.metric("平均ROE", f"{avg_roe:.2f}%")
                except:
                    st.metric("平均ROE", "---")
            else:
                st.metric("平均ROE", "---")
