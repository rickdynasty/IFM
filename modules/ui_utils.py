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


def display_table(df: pd.DataFrame, data_type: str = 'stock', show_title: bool = False) -> None:
    """
    显示带有固定表头的表格，支持通过下拉菜单排序
    
    Args:
        df: 要显示的DataFrame
        data_type: 数据类型，'stock'或'fund'
        show_title: 是否显示标题和下载按钮，默认为False
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

    # 为每个表格类型创建固定的会话状态键
    # 使用数据类型区分不同表格，避免使用时间戳
    sort_state_key = f"sort_col_state_{data_type}"
    sort_dir_state_key = f"sort_dir_state_{data_type}"

    # 初始化会话状态以跟踪排序
    if sort_state_key not in st.session_state:
        st.session_state[sort_state_key] = None
        st.session_state[sort_dir_state_key] = True

    # 创建标题行，包含排序控件（移除标签，优化布局）
    if show_title:
        # 如果需要显示标题，则创建标题行 - 减小标题边距
        st.markdown("""
        <h3 style="margin-top:0rem; padding-top:0rem; margin-bottom:0rem;">📋 筛选结果</h3>
        """, unsafe_allow_html=True)

    # 创建排序控件行 - 使用更紧凑的布局
    col1, col2, col3, col4 = st.columns([1, 2, 2, 1])

    # 获取当前排序状态
    current_sort_col = st.session_state[sort_state_key]
    current_sort_asc = st.session_state[sort_dir_state_key]

    # 排序列选择
    sortable_columns = [col for col in display_df.columns if col != '序号']

    with col1:
        # 创建固定的widget key，使用数据类型区分
        widget_key = f"select_{data_type}"

        # 确定初始索引
        if current_sort_col is None:
            initial_index = 0
        else:
            try:
                initial_index = sortable_columns.index(current_sort_col) + 1
            except ValueError:
                initial_index = 0

        # 排序列选择（移除标签）
        sort_column = st.selectbox(
            label="排序列",  # 提供标签但隐藏
            options=["不排序"] + sortable_columns,
            index=initial_index,
            key=widget_key,
            label_visibility="collapsed"  # 完全隐藏标签
        )

    # 排序方向选择
    with col2:
        # 创建固定的widget key，使用数据类型区分
        direction_key = f"radio_{data_type}"

        # 排序方向选择（移除标签）
        sort_direction = st.radio(
            label="排序方向",  # 提供标签但隐藏
            options=["升序", "降序"],
            index=0 if current_sort_asc else 1,
            horizontal=True,
            key=direction_key,
            disabled=(sort_column == "不排序"),
            label_visibility="collapsed"  # 完全隐藏标签
        )

    # 更新排序状态
    if sort_column == "不排序":
        st.session_state[sort_state_key] = None
    else:
        st.session_state[sort_state_key] = sort_column

    # 更新排序方向
    st.session_state[sort_dir_state_key] = (sort_direction == "升序")

    # 定义列宽配置
    column_widths = {
        '序号': 40,
        '股票代码': 80,
        '基金代码': 80,
        '股票名称': 80,
        '基金简称': 110,
        '股息率': 50,
        '北上持股': 90,
        '当前ROE': 60,
        '平均ROE': 60,
        'PE.扣非': 60,
        '今年来': 60,
        '行业': 70
    }

    # 为未明确定义宽度的列设置默认宽度
    for col in display_df.columns:
        if col not in column_widths:
            column_widths[col] = 70  # 默认宽度

    # 应用排序 - 简化逻辑，增强健壮性
    if sort_column != "不排序" and sort_column in display_df.columns:
        # 使用当前选择的排序列和方向
        col = sort_column
        asc = (sort_direction == "升序")

        # 更新会话状态
        st.session_state[sort_state_key] = col
        st.session_state[sort_dir_state_key] = asc

        # 尝试将列转换为数值进行排序
        try:
            # 检查是否为百分比值 - 更健壮的方式
            has_percent = False
            if display_df[col].dtype == object:
                try:
                    has_percent = display_df[col].astype(str).str.contains('%').any()
                except:
                    has_percent = False

            if has_percent:
                # 处理百分比值
                temp_col = col + '_sort'
                display_df[temp_col] = display_df[col].str.replace('%', '').astype(float)
                display_df = display_df.sort_values(by=temp_col, ascending=asc)
                display_df = display_df.drop(columns=[temp_col])
            else:
                # 尝试直接排序
                display_df = display_df.sort_values(by=col, ascending=asc)
        except Exception as e:
            # 如果转换失败，按字符串排序
            try:
                display_df = display_df.sort_values(by=col, ascending=asc)
            except:
                # 如果排序完全失败，记录错误但不中断程序
                pass

    # 只有在需要显示标题时才显示下载按钮
    # if True:
    # # 添加下载按钮到第四列
    with col4:
        # 将DataFrame转换为CSV
        csv = display_df.to_csv(index=False)

        # 生成更有意义的文件名
        from datetime import datetime
        current_time = datetime.now().strftime('%Y%m%d_%H%M')

        if data_type == 'stock':
            file_name = f"股票筛选结果_{current_time}.csv"
        else:
            file_name = f"基金筛选结果_{current_time}.csv"

        # 添加下载按钮 - 使用固定的key
        download_key = f"dl_{data_type}"
        st.download_button(
            label="⬇ 下载筛选结果",
            data=csv.encode('utf-8-sig'),  # 使用UTF-8 with BOM，确保Excel正确显示中文
            file_name=file_name,
            mime="text/csv",
            key=download_key,
            use_container_width=True  # 使按钮填满容器宽度
        )

    # 添加CSS样式
    st.markdown(f"""
    <style>
    /* 移除页面底部留白 */
    .main .block-container {{
        padding-bottom: 100rem;
        max-width: 85%;
    }}
    
    /* 确保表格容器填充可用空间 */
    .stApp {{
        height: 100vh;
    }}
    
    .fixed-table {{
        width: 100%;
        border-collapse: collapse;
        table-layout: fixed;
        font-size: 16px;  /* 减小字体大小 */
    }}
    .fixed-table-container {{
        height: calc(100vh - 200px); /* 动态计算高度，留出页面其他元素的空间 */
        min-height: {TABLE_CONFIG['height']}px; /* 最小高度保证 */
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
        font-size: 16px;  /* 表头字体大小 */
    }}
    .fixed-table td {{
        padding: 3px 4px;  /* 进一步减小单元格内边距 */
        border-bottom: 1px solid {TABLE_CONFIG['border_color']};
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        text-align: center;  /* 居中对齐 */
        height: 28px;  /* 固定行高，使表格更紧凑 */
        max-height: 32px;
    }}
    
    /* 优化排序控件的布局 */
    .stSelectbox, .stRadio {{
        margin-bottom: 0rem;
    }}
    
    /* 减少Streamlit组件的默认间距 */
    .element-container {{
        margin-bottom: 0rem;
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
    </style>
    """, unsafe_allow_html=True)

    # 手动构建HTML表格，包含原始表头
    html_parts = ['<div class="fixed-table-container"><table class="fixed-table">']

    # 添加表头
    html_parts.append('<thead>')
    html_parts.append('<tr>')
    for col in display_df.columns:
        # 为每列添加特定的CSS类，强制应用列宽
        # 添加当前排序列的标记
        if sort_column != "不排序" and sort_column == col:
            sort_icon = " ↑" if (sort_direction == "升序") else " ↓"
            html_parts.append(
                f'<th class="col-{col}" style="width: {column_widths.get(col, 70)}px;">{col}{sort_icon}</th>')
        else:
            html_parts.append(f'<th class="col-{col}" style="width: {column_widths.get(col, 70)}px;">{col}</th>')
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

            # 添加单元格，应用列宽样式
            html_parts.append(f'<td{css_class} style="width: {column_widths.get(col_name, 70)}px;">{value}</td>')

        html_parts.append('</tr>')

    html_parts.append('</tbody>')
    html_parts.append('</table></div>')

    # 不再需要JavaScript排序代码

    # 显示表格
    st.markdown(''.join(html_parts), unsafe_allow_html=True)


def display_statistics(df: pd.DataFrame, data_type: str = 'stock') -> None:
    """
    显示统计信息 - 当前已禁用，减少高度占用
    
    Args:
        df: 要统计的DataFrame
        data_type: 数据类型，'stock'或'fund'
    """
    # 移除筛选结果统计部分，减少高度占用
    pass
