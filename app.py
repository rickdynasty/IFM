import streamlit as st
from datetime import datetime
import pandas as pd
import plotly.express as px
import os
import sys

# 确保可以导入模块
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# 导入自定义模块
from modules.fund_filter import fund_filter, get_fund_managers, get_fund_companies
from modules.stock_filter_new import stock_filter, get_stock_type_options, get_sub_type_options, get_industry_options
from modules.utils import load_css, format_number, user_auth, save_user_preferences
from modules.config import APP_TITLE, APP_ICON, APP_VERSION, DATA_PATH

# 设置页面配置 - 移动菜单到底部
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded", 
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': f"{APP_TITLE} v{APP_VERSION}"
    }
)

# 隐藏默认菜单和部署按钮，优化页面留白
hide_menu_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
    header {visibility: hidden;}
    
    /* 减少顶部和底部留白 */
    .block-container {
        padding-top: 10px !important;
        padding-bottom: 10px !important;
    }
    
    /* 减少标题和元素间距 */
    h1, h2, h3 {
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* 减少筛选结果统计与表格的间距 */
    .stMetric {
        padding-top: 1.5rem !important;
        padding-bottom: 0.5rem !important;
    }
    
    /* 优化表格容器 */
    [data-testid="stDataFrame"] > div {
        padding-top: 0.5rem !important;
    }
    
    /* 优化按钮样式 */
    .stDownloadButton button {
        padding: 0.25rem 1rem !important;
    }
    
    /* 减少各组件之间的垂直间距 */
    .element-container {
        margin-top: 0.2rem !important;
        margin-bottom: 0.2rem !important;
    }
    </style>
"""
st.markdown(hide_menu_style, unsafe_allow_html=True)

# 添加自定义按钮和标题样式
custom_styles = """
<style>
/* 自定义按钮样式 - 增大字体 */
button[data-testid="baseButton-primary"] {
    font-size: 1.5rem !important;
    padding-top: 1px !important;
    padding-bottom: 1px !important;
}

/* 减小功能标题字体大小 */
.main h3 {
    font-size: 1.2rem !important;
}
</style>
"""
st.markdown(custom_styles, unsafe_allow_html=True)

# 加载CSS样式
load_css()

# 初始化 session_state
if 'current_page' not in st.session_state:
    st.session_state.current_page = "🏠 首页"
if 'user_logged_in' not in st.session_state:
    st.session_state.user_logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'user_preferences' not in st.session_state:
    st.session_state.user_preferences = {}
if 'show_market_cycle' not in st.session_state:
    st.session_state.show_market_cycle = False

# 侧边栏导航
st.sidebar.markdown(f"## 📊 {APP_TITLE} v{APP_VERSION}")

# 用户登录区域
with st.sidebar.expander("👤 用户中心", expanded=False):
    if not st.session_state.user_logged_in:
        username = st.text_input("用户名")
        password = st.text_input("密码", type="password")
        if st.button("登录"):
            if user_auth(username, password):
                st.session_state.user_logged_in = True
                st.session_state.user_id = username
                st.success(f"欢迎回来，{username}!")
                st.rerun()
            else:
                st.error("用户名或密码错误")
    else:
        st.write(f"当前用户: {st.session_state.user_id}")
        if st.button("退出登录"):
            st.session_state.user_logged_in = False
            st.session_state.user_id = None
            st.rerun()

# 主页面选择
page_options = ["🏠 首页", "📈 基金筛选", "📊 股票筛选"]
if st.session_state.user_logged_in:
    page_options.extend(["📉 经济周期监测", "💰 投资组合分析", "⚙️ 个人设置"])

# 确保当前页面在选项中
current_index = 0
if st.session_state.current_page in page_options:
    current_index = page_options.index(st.session_state.current_page)

page = st.sidebar.selectbox(
    "选择功能模块",
    page_options,
    index=current_index
)

# 更新当前页面
st.session_state.current_page = page

# 页面内容
if st.session_state.current_page == "🏠 首页":
    # 首页内容
    st.title(f"🎯 {APP_TITLE}")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 按钮放在标题上方，宽度控制为1/4左右
        button_col, space_col = st.columns([1, 3])
        with button_col:
            if st.button("🚀 开始筛选基金", key="fund_button"):
                st.session_state.current_page = "📈 基金筛选"
                st.rerun()
            
        st.markdown("### 📈 基金筛选功能")
                
        st.markdown("""
        - **基金类型筛选**（股票型、混合型、债券型、指数型）
        - **智能年化收益率计算**
        - **多维度筛选条件**
        - **上市年限智能判断**
        - **连续收益率分析**
        - **数据导出功能**
        """)
    
    with col2:
        # 按钮放在标题上方，宽度控制为1/4左右
        button_col, space_col = st.columns([1, 3])
        with button_col:
            if st.button("🚀 开始筛选股票", key="stock_button"):
                st.session_state.current_page = "📊 股票筛选"
                st.rerun()
            
        st.markdown("### 📊 股票筛选功能")
                
        st.markdown("""
        - **多类型股票数据**
        - **行业维度筛选**
        - **热门股票分析**
        - **ROE、PEG等指标**
        - **综合过滤功能**
        """)
    
    st.markdown("---")
    
    # 高级功能介绍
    if st.session_state.user_logged_in:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 📉 经济周期监测")
            st.markdown("""
            - **宏观经济指标监控**
            - **市场情绪指数分析**
            - **行业轮动研判**
            - **风险预警系统**
            """)
            if st.button("🔍 查看经济周期", use_container_width=True):
                st.session_state.current_page = "📉 经济周期监测"
                st.rerun()
        
        with col2:
            st.markdown("### 💰 投资组合分析")
            st.markdown("""
            - **多资产配置建议**
            - **风险收益特征分析**
            - **组合回测与优化**
            - **个性化投资方案**
            """)
            if st.button("📊 分析投资组合", use_container_width=True):
                st.session_state.current_page = "💰 投资组合分析"
                st.rerun()
    else:
        st.info("👋 登录后可使用更多高级功能，包括经济周期监测和投资组合分析")
    
    st.markdown("---")
    st.markdown("### 📋 系统说明")
    st.markdown(f"""
    本系统基于本地基金和股票数据进行智能筛选分析，支持：
    - 基金年化收益率计算和筛选
    - 股票多维度综合过滤
    - 数据导出和统计分析
    - 经济周期监控和资产配置推荐(会员功能)
    
    当前版本: v{APP_VERSION}
    """)

elif st.session_state.current_page == "📈 基金筛选":
    # 基金筛选条件 - 移到最上面
    st.sidebar.markdown("### 🔍 筛选条件")
    
    # 数据日期选择
    try:
        from modules.fund_filter import get_available_fund_dates
        available_dates = get_available_fund_dates()
        if available_dates:
            selected_date = st.sidebar.selectbox(
                "数据日期",
                available_dates,
                index=0,  # 默认选择最新日期
                help="选择基金数据的日期，不同日期可能包含不同的基金信息"
            )
        else:
            selected_date = "2025.08"  # 默认日期
            st.sidebar.warning("未找到可用数据日期，使用默认日期")
    except Exception as e:
        selected_date = "2025.08"  # 默认日期
        st.sidebar.warning(f"加载日期列表失败: {e}")
    
    # 基金类型选择 - 默认选择债券型
    fund_type = st.sidebar.selectbox(
        "基金类型",
        ["全部", "股票型", "混合型", "债券型", "指数型"],
        index=3,  # 默认选择债券型(索引3)
        help="选择特定类型的基金进行筛选"
    )
    
    # 垂直排列筛选条件，并设置合适的默认值
    min_annual_return = st.sidebar.selectbox("年化收益率 > (%)", [3, 4.2, 5, 8, 10, 15], index=0)  # 默认3%
    min_consecutive_return = st.sidebar.selectbox("连续收益率 > (%)", [3, 4.2, 5, 8, 10, 15], index=1)  # 默认4.2%
    min_years_listed = st.sidebar.selectbox("上市年限 > (年)", [1, 2, 3, 4, 5], index=1)  # 默认2年
    
    # 基金经理和基金公司筛选(高级筛选)
    with st.sidebar.expander("🔍 高级筛选", expanded=False):
        try:
            fund_managers = ["不限"] + get_fund_managers(selected_date)
            fund_companies = ["不限"] + get_fund_companies(selected_date)
            
            selected_manager = st.selectbox("基金经理", fund_managers)
            selected_company = st.selectbox("基金公司", fund_companies)
            
            fund_manager = None if selected_manager == "不限" else selected_manager
            fund_company = None if selected_company == "不限" else selected_company
        except:
            fund_manager = None
            fund_company = None
            st.warning("无法加载基金经理和公司信息")
    
    # 执行筛选
    with st.spinner("正在筛选基金数据..."):
        result = fund_filter(
            min_annual_return, 
            min_consecutive_return, 
            min_years_listed, 
            fund_type,
            fund_manager,
            fund_company,
            selected_date
        )
    
    # 主内容区域 - 使用更紧凑的标题样式
    st.markdown("<h2 style='margin-top:0rem; padding-top:0rem; margin-bottom:0rem;'>📈 基金筛选系统</h2>", unsafe_allow_html=True)
    
    # 重新排列页面组件
    if len(result) > 0:
        # 先显示筛选结果统计
        st.markdown("<h3 style='margin-top:0rem; padding-top:0rem; margin-bottom:0rem;'>📊 筛选结果统计</h3>", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("符合条件的基金数量", len(result))
        
        with col2:
            try:
                avg_return = result['年化收益率'].str.replace('%', '').astype(float).mean()
                st.metric("平均年化收益率", f"{avg_return:.2f}%")
            except:
                st.metric("平均年化收益率", "---")
        
        with col3:
            try:
                max_return = result['年化收益率'].str.replace('%', '').astype(float).max()
                st.metric("最高年化收益率", f"{max_return:.2f}%")
            except:
                st.metric("最高年化收益率", "---")
        
        with col4:
            try:
                min_return = result['年化收益率'].str.replace('%', '').astype(float).min()
                st.metric("最低年化收益率", f"{min_return:.2f}%")
            except:
                st.metric("最低年化收益率", "---")
        
        # 然后显示筛选结果标题和下载按钮
        result_col1, result_col2 = st.columns([3, 1])
        
        with result_col1:
            st.markdown("<h3 style='margin-top:0; padding-top:0; margin-bottom:0;'>📋 筛选结果</h3>", unsafe_allow_html=True)
        
        # 导出功能
        with result_col2:
            csv = result.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 下载筛选结果 (CSV)",
                data=csv,
                file_name=f"基金筛选结果_{fund_type}_{selected_date}_{min_annual_return}%_{min_years_listed}年_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        # 定义颜色函数
        def color_returns(val):
            try:
                if pd.isna(val) or val == "---":
                    return "color: black"
                # 提取数值
                num_val = float(str(val).replace('%', ''))
                if num_val > 0:
                    return "color: red; font-weight: bold"
                elif num_val < 0:
                    return "color: green; font-weight: bold"
                else:
                    return "color: black"
            except:
                return "color: black"
        
        # 添加基金代码和基金简称的链接生成函数
        def make_clickable_fund(val, is_code=False):
            """将基金代码或基金简称转换为可点击的链接"""
            if is_code:
                # 基金代码补零至6位
                code = str(val).zfill(6)
                return f'<a href="https://fund.10jqka.com.cn/{code}" target="_blank">{val}</a>'
            else:
                # 基金简称直接链接
                # 需要找到对应行的基金代码
                code = str(result.loc[result['基金简称'] == val, '基金代码'].values[0]).zfill(6)
                return f'<a href="https://fund.eastmoney.com/{code}.html" target="_blank">{val}</a>'
        
        # 不需要添加序号列，只需在HTML表格中修改表头
        
        # 应用样式，包括各年收益率
        styled_df = result.style.map(color_returns, subset=['年化收益率', '第1年收益率', '第2年收益率', '第3年收益率', 
                                                      '近1年', '近2年', '近3年', '今年来', '成立来'])
        
        # 为基金代码和基金简称添加可点击链接
        styled_df = styled_df.format({'基金代码': lambda x: make_clickable_fund(x, True),
                                     '基金简称': lambda x: make_clickable_fund(x, False)})
        
        # 构建列配置 - 添加各年收益率列
        column_config = {
            "基金代码": st.column_config.TextColumn("基金代码", width=80),
            "基金简称": st.column_config.TextColumn("基金简称", width=150),
            "基金类型": st.column_config.TextColumn("基金类型", width=80),  # 改为TextColumn，不再隐藏类型
            "年化收益率": st.column_config.TextColumn("年化收益率", width=100),
            "上市年限": st.column_config.TextColumn("上市年限", width=80),
            "第1年收益率": st.column_config.TextColumn("第1年收益", width=90),
            "第2年收益率": st.column_config.TextColumn("第2年收益", width=90),
            "第3年收益率": st.column_config.TextColumn("第3年收益", width=90),
            "近1年": st.column_config.TextColumn("近1年", width=80),
            "近2年": st.column_config.TextColumn("近2年", width=80),
            "近3年": st.column_config.TextColumn("近3年", width=80),
            "今年来": st.column_config.TextColumn("今年来", width=80),
            "成立来": st.column_config.TextColumn("成立来", width=80)
        }
        
        # 添加额外列配置
        if '基金经理' in result.columns:
            column_config["基金经理"] = st.column_config.TextColumn("基金经理", width=120)
        if '基金公司' in result.columns:
            column_config["基金公司"] = st.column_config.TextColumn("基金公司", width=150)
        
        # 增加表格高度，充分利用节省出来的页面空间
        # Streamlit的dataframe不支持unsafe_allow_html参数，需要使用st.write来显示HTML链接
        st.write(
            styled_df.to_html(escape=False),
            unsafe_allow_html=True
        )
        
        # 已在上方显示统计信息，这里不再需要
    else:
        st.warning("⚠️ 没有找到符合条件的基金，请调整筛选条件。")

elif st.session_state.current_page == "📊 股票筛选":
    # 股票筛选条件
    st.sidebar.markdown("### 🔍 筛选条件")
    
    # 日期选择
    from modules.stock_filter_new import get_available_dates, get_current_date
    
    available_dates = get_available_dates()
    current_date = get_current_date()
    
    # 如果当前日期不在可用日期列表中，添加到列表开头
    if current_date not in available_dates:
        available_dates.insert(0, current_date)
    
    selected_date = st.sidebar.selectbox(
        "选择数据日期",
        available_dates,
        index=0,
        help="选择要筛选的数据日期，基金重仓股数据不受日期影响"
    )
    
    # 获取所有股票类型选项
    all_stock_types = get_stock_type_options()
    
    # 多类型选择 - 默认选择"ROE连续超15%"
    selected_types = st.sidebar.multiselect(
        "选择股票类型（可多选）",
        all_stock_types,
        default=["ROE连续超15%"],
        help="选择多个类型，系统将找出同时满足所有条件的股票"
    )
    
    # 子类型选择
    sub_types = {}
    if selected_types:
        st.sidebar.markdown("#### 📋 子类型设置")
        for stock_type in selected_types:
            sub_options = get_sub_type_options(stock_type)
            if sub_options:
                # 为"ROE连续超15%"设置默认子类型为"连续3年"
                default_index = 0
                if stock_type == "ROE连续超15%" and "连续3年" in sub_options:
                    default_index = sub_options.index("连续3年")
                
                sub_type = st.sidebar.selectbox(
                    f"{stock_type}子类型",
                    sub_options,
                    index=default_index,
                    key=f"sub_{stock_type}"
                )
                sub_types[stock_type] = sub_type
        
    # 新增ROE和股息筛选
    st.sidebar.markdown("#### 📊 指标筛选")
    
    # 股息筛选
    show_dividend_filter = st.sidebar.checkbox("启用股息筛选", False)
    dividend_filter = None
    if show_dividend_filter:
        dividend_filter = st.sidebar.selectbox(
            "股息 > (%)",
            [1, 3, 5, 8],
            index=1,  # 默认3%
            help="筛选股息率大于等于选定值的股票"
        )

    # ROE筛选
    show_roe_filter = st.sidebar.checkbox("启用ROE筛选", False)
    roe_filter = None
    if show_roe_filter:
        roe_filter = st.sidebar.selectbox(
            "ROE > (%)",
            [8, 10, 12, 15],
            index=2,  # 默认12%, 12%是通过ROE来判断一个公司好坏的分水岭指标
            help="筛选ROE大于等于选定值的股票"
        )

    # 行业筛选
    st.sidebar.markdown("#### 🏭 行业筛选")
    show_industry_filter = st.sidebar.checkbox("启用行业筛选", False)
    industry_filter = []

    if show_industry_filter:
        all_industries = get_industry_options(selected_date)
        industry_filter = st.sidebar.multiselect(
            "选择行业（可多选）",
            all_industries,
            default=[],
            help="选择行业进行筛选，不选择则显示全部行业"
        )
    
    # 执行筛选
    with st.spinner("正在筛选股票数据..."):
        result = stock_filter(selected_types, sub_types, industry_filter, selected_date, roe_filter, dividend_filter)
    
    # 主内容区域 - 使用更紧凑的标题样式
    st.markdown("<h2 style='margin-top:0rem; padding-top:0rem; margin-bottom:0rem;'>📊 股票筛选系统</h2>", unsafe_allow_html=True)
    
    if len(result) > 0:
        # 先显示筛选结果统计
        st.markdown("<h3 style='margin-top:0rem; padding-top:0rem; margin-bottom:0rem;'>📊 筛选结果统计</h3>", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("符合条件的股票数量", len(result))
        
        with col2:
            st.metric("筛选类型数量", len(selected_types))
            
        with col3:
            if industry_filter:
                st.metric("筛选行业数量", len(industry_filter))
            else:
                st.metric("筛选行业数量", 0)
        
        with col4:
            st.metric("数据日期", selected_date)
        
        # 然后显示筛选结果标题和下载按钮
        result_col1, result_col2 = st.columns([3, 1])
        
        with result_col1:
            st.markdown("<h3 style='margin-top:0; padding-top:0; margin-bottom:0;'>📋 筛选结果</h3>", unsafe_allow_html=True)
        
        # 导出功能
        with result_col2:
            csv = result.to_csv(index=False, encoding='utf-8-sig')
            
            # 生成文件名
            file_name = f"股票筛选结果_{len(selected_types)}种类型"
            if industry_filter:
                file_name += f"_{len(industry_filter)}个行业"
            file_name += f"_{selected_date}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
            
            st.download_button(
                label="📥 下载筛选结果 (CSV)",
                data=csv,
                file_name=file_name,
                mime="text/csv",
                use_container_width=True
            )
        # 添加股票代码和股票名称的链接生成函数
        def make_clickable_stock(val, is_code=False):
            """将股票代码或股票名称转换为可点击的链接"""
            if is_code:
                # 股票代码补零至6位
                code = str(val).zfill(6)
                return f'<a href="https://stockpage.10jqka.com.cn/{code}" target="_blank">{val}</a>'
            else:
                # 股票名称直接链接
                # 需要找到对应行的股票代码
                try:
                    code = str(result.loc[result['股票名称'] == val, '股票代码'].values[0]).zfill(6)
                    # 判断交易所并添加前缀
                    if code.startswith(('6', '9')):
                        exchange_prefix = "SH"  # 沪市（主板/科创板）
                    else:
                        exchange_prefix = "SZ"  # 深市（主板/创业板）

                    return f'<a href="https://xueqiu.com/S/{exchange_prefix}{code}" target="_blank">{val}</a>'
                except:
                    return val  # 如果找不到对应的股票代码，则返回原值
        
        # 不需要添加序号列，只需在HTML表格中修改表头
        
        # 为股票代码和股票名称添加可点击链接
        format_dict = {
            '股票代码': lambda x: make_clickable_stock(x, True),
            '股票名称': lambda x: make_clickable_stock(x, False)
        }
        
        # 为数值列添加格式化
        numeric_columns = ['当前ROE', '扣非PE', 'PB', '股息', '今年来', 'ROE', 'PEG', '持有市值', '持股比', 
                          '关注度', '便宜指数', '最新股息', '平均股息', '控盘度', '股东数', '占总股本', '推荐数',
                          '平均ROE', '北上持股']
        
        # 清理数据中的单引号
        for col in result.columns:
            if col in result.columns:
                try:
                    # 尝试清理字符串中的单引号
                    result[col] = result[col].apply(lambda x: str(x).replace("'", "") if isinstance(x, str) else x)
                except:
                    pass
        
        # 简化格式化逻辑 - 如果数据类型不对就直接显示原始数据
        for col in numeric_columns:
            if col in result.columns:
                # 定义一个安全的格式化函数
                def safe_format(x, format_type):
                    try:
                        if pd.isna(x) or x == '' or x == '-':
                            return x
                        
                        # 移除字符串中的单引号
                        if isinstance(x, str):
                            x = x.replace("'", "")
                        
                        if format_type == 'percent':
                            # 如果已经包含百分号，直接返回
                            if isinstance(x, str) and '%' in x:
                                return x
                            # 尝试转换为百分比
                            return f"{float(x)}%"
                        elif format_type == 'money':
                            # 如果已经包含"亿"，直接返回
                            if isinstance(x, str) and '亿' in x:
                                return x
                            # 尝试转换为金额
                            return f"{float(x)}亿"
                        elif format_type == 'float':
                            # 尝试转换为两位小数
                            return f"{float(x):.2f}"
                        elif format_type == 'int':
                            # 尝试转换为整数
                            return f"{int(float(x))}"
                        else:
                            # 默认返回原值
                            return x
                    except:
                        # 如果转换失败，返回原始值
                        return x
                
                # 根据列名应用不同的格式化
                if col in ['当前ROE', 'ROE', '股息', '最新股息', '平均股息', '今年来', '持股比', '平均ROE']:
                    format_dict[col] = lambda x: safe_format(x, 'percent')
                elif col in ['持有市值']:
                    format_dict[col] = lambda x: safe_format(x, 'money')
                elif col in ['扣非PE', 'PB', 'PEG', '便宜指数']:
                    format_dict[col] = lambda x: safe_format(x, 'float')
                elif col in ['股东数', '控盘度', '推荐数']:
                    format_dict[col] = lambda x: safe_format(x, 'int')
                else:
                    # 其他列保持原样
                    format_dict[col] = lambda x: x
        
        # 为负值添加绿色字体样式，为今年来的正值添加红色字体样式
        def color_values(val, col_name):
            try:
                # 处理百分比格式
                if isinstance(val, str) and '%' in val:
                    val_num = float(val.replace('%', '').strip())
                    if val_num < 0:
                        return 'color: green'
                    elif col_name == '今年来' and val_num > 0:
                        return 'color: red'
                # 处理普通数字
                elif isinstance(val, (int, float)):
                    if val < 0:
                        return 'color: green'
                    elif col_name == '今年来' and val > 0:
                        return 'color: red'
                # 处理可能是数字的字符串
                elif isinstance(val, str):
                    try:
                        val_num = float(val)
                        if val_num < 0:
                            return 'color: green'
                        elif col_name == '今年来' and val_num > 0:
                            return 'color: red'
                    except:
                        pass
            except:
                pass
            return ''
            
        # 创建样式函数 - 处理Series和DataFrame两种情况
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
        
        # 应用样式和格式
        styled_df = result.style.format(format_dict).apply(apply_styles)
        
        # 显示表格数据 - 使用st.write来显示HTML链接
        st.write(
            styled_df.to_html(escape=False),
            unsafe_allow_html=True
        )
        
        # 已在上方显示统计信息，这里不再需要
        
        # 为登录用户提供收藏功能
        if st.session_state.user_logged_in:
            with st.expander("💾 收藏筛选结果", expanded=False):
                save_name = st.text_input("保存名称", value=f"股票筛选_{datetime.now().strftime('%Y%m%d')}")
                if st.button("保存筛选条件"):
                    save_data = {
                        "selected_types": selected_types,
                        "sub_types": sub_types,
                        "industry_filter": industry_filter,
                        "selected_date": selected_date,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    save_user_preferences(st.session_state.user_id, "stock_filters", save_name, save_data)
                    st.success(f"已保存筛选条件: {save_name}")
    else:
        if selected_types:
            st.warning("⚠️ 没有找到同时满足所有条件的股票，请调整筛选条件。")
        else:
            st.info("ℹ️ 请选择至少一种股票类型进行筛选。")

# 经济周期监测页面 - 仅登录用户可见
elif st.session_state.current_page == "📉 经济周期监测" and st.session_state.user_logged_in:
    st.markdown("## 📉 经济周期监测")
    st.info("🚧 此功能正在开发中，敬请期待！")
    
    # 占位内容
    st.markdown("""
    ### 即将推出的功能
    
    1. **宏观经济指标监控**
       - GDP增长率、CPI、PPI等关键指标追踪
       - 央行货币政策分析
       - 流动性指标监测
    
    2. **市场情绪指标**
       - 市场恐慌指数
       - 投资者情绪分析
       - 市场交易量监测
    
    3. **行业轮动模型**
       - 经济周期不同阶段的行业表现
       - 行业景气度指标
       - 行业间资金流向分析
    
    4. **资产配置建议**
       - 基于经济周期的大类资产配置比例
       - 风险提示与规避策略
    """)

# 投资组合分析页面 - 仅登录用户可见
elif st.session_state.current_page == "💰 投资组合分析" and st.session_state.user_logged_in:
    st.markdown("## 💰 投资组合分析")
    st.info("🚧 此功能正在开发中，敬请期待！")
    
    # 占位内容
    st.markdown("""
    ### 即将推出的功能
    
    1. **投资组合构建**
       - 多资产类别配置
       - 风险收益特征设定
       - 个性化投资目标设置
    
    2. **风险分析**
       - 风险收益比评估
       - 最大回撤分析
       - 风险分散度评估
    
    3. **绩效评估**
       - 历史回测分析
       - 基准对比
       - 业绩归因分析
    
    4. **优化建议**
       - 基于经济周期的动态调整
       - 税收优化策略
       - 再平衡提示
    """)

# 个人设置页面 - 仅登录用户可见
elif st.session_state.current_page == "⚙️ 个人设置" and st.session_state.user_logged_in:
    st.markdown("## ⚙️ 个人设置")
    
    # 基本设置
    st.markdown("### 基本设置")
    col1, col2 = st.columns(2)
    
    with col1:
        st.checkbox("启用数据自动刷新", value=True)
        st.checkbox("显示高级分析图表", value=True)
    
    with col2:
        st.selectbox("默认起始页", ["首页", "基金筛选", "股票筛选"])
        st.selectbox("数据导出格式", ["CSV", "Excel"])
    
    # 通知设置
    st.markdown("### 通知设置")
    st.checkbox("接收市场异常波动提醒", value=True)
    st.checkbox("接收持仓股票/基金重大事件提醒", value=True)
    st.checkbox("接收系统更新通知", value=True)
    
    # 账户安全
    st.markdown("### 账户安全")
    with st.expander("修改密码", expanded=False):
        st.text_input("当前密码", type="password")
        st.text_input("新密码", type="password")
        st.text_input("确认新密码", type="password")
        st.button("确认修改")

# 未登录用户尝试访问需要登录的页面
elif st.session_state.current_page in ["📉 经济周期监测", "💰 投资组合分析", "⚙️ 个人设置"]:
    st.warning("⚠️ 请先登录以访问此功能")
    st.session_state.current_page = "🏠 首页"
    st.rerun()