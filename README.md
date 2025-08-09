# 投资理财-股票基金筛选系统

## 简介
本系统是一个用于投资决策支持的综合平台，集成了基金筛选、股票筛选、经济周期监测、投资组合分析等功能，支持多维度数据过滤和可视化，帮助投资者做出更明智的投资决策。

## 系统架构
系统采用模块化设计，主要包含以下组件：
- **数据层**：负责数据读取、处理和存储
- **业务层**：实现各类筛选、分析算法
- **展示层**：用户界面和交互
- **用户系统**：用户认证、权限管理
- **配置系统**：全局配置和参数管理

## 功能特点

### 基金筛选
- 支持按基金类型、年化收益率、上市年限等多维度筛选
- 智能计算年化收益率和连续收益能力
- 支持基金经理、基金公司维度的高级筛选
- 收益率可视化和分析

### 股票筛选
- 多种类型股票复合筛选（热门股票、ROE、PEG、股息率等）
- 行业维度过滤
- 支持各类型的子类型精确筛选
- 数据可视化展示

### 会员专享功能
- 经济周期监测与预测
- 投资组合构建与分析
- 个性化筛选条件保存
- 数据导出和报告生成

## 技术栈
- **后端**：Python + Pandas + NumPy
- **前端**：Streamlit
- **数据可视化**：Plotly + Matplotlib
- **数据存储**：文件系统 (CSV/TXT)

## 安装与使用

### 环境要求
- Python 3.8+
- 依赖库：见requirements.txt

### 安装步骤
1. 克隆代码仓库
   ```
   git clone https://github.com/your-username/investment-filter-system.git
   cd investment-filter-system
   ```

2. 创建并激活虚拟环境
   ```
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. 安装依赖
   ```
   pip install -r requirements.txt
   ```

4. 运行应用
   ```
   streamlit run app_v2.py
   ```

## 使用方法
1. 启动应用后，通过浏览器访问 http://localhost:8501
2. 在侧边栏选择功能模块：基金筛选、股票筛选等
3. 设置筛选条件，系统将自动执行筛选并展示结果
4. 可以下载筛选结果或保存筛选条件（会员功能）

## 目录结构
```
├── app_v2.py                # 主程序入口
├── modules/                 # 功能模块
│   ├── __init__.py          # 包初始化
│   ├── config.py            # 全局配置
│   ├── utils.py             # 工具函数
│   ├── fund_filter_v2.py    # 基金筛选模块
│   └── stock_filter_v2.py   # 股票筛选模块
├── data/                    # 数据目录
│   ├── fund/                # 基金数据
│   └── stock/               # 股票数据
├── user_data/               # 用户数据（会员设置等）
├── requirements.txt         # 依赖库
└── README_v2.md             # 项目说明
```

## 数据说明
- 基金数据(txt格式)：包含基金代码、简称、收益率等信息
- 股票数据(csv/txt格式)：包含不同类型的股票筛选数据，如热门股票、ROE排名等

## 未来规划
- 添加机器学习模型预测股票表现
- 集成更多外部数据源
- 开发移动端应用
- 增强用户社区和互动功能

## 贡献指南
欢迎提交Issue或Pull Request来帮助改进系统。

## 许可证
MIT
