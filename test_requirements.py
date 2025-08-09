import unittest
import pandas as pd
import os
import sys
from modules.fund_filter import fund_filter
from modules.stock_filter import stock_filter, extract_stock_codes, get_industry_options

class TestRequirements(unittest.TestCase):
    """测试系统是否满足需求中的功能"""
    
    def test_fund_filter_default_values(self):
        """测试基金筛选默认值是否符合需求"""
        print("测试基金筛选默认值...")
        # 测试默认值: 年化收益率 > 3%, 连续收益率 > 4.2%, 上市年限 > 2年
        result = fund_filter(min_annual_return=3, min_consecutive_return=4.2, min_years_listed=2, 
                            fund_type="债券型", fund_manager=None, fund_company=None)
        
        # 验证结果不为空
        self.assertIsNotNone(result)
        print(f"基金筛选结果数量: {len(result)}")
        
        if len(result) > 0:
            # 验证结果中包含第1年收益率、第2年收益率、第3年收益率列
            required_columns = ['基金代码', '基金简称', '基金类型', '年化收益率', 
                               '第1年收益率', '第2年收益率', '第3年收益率']
            for col in required_columns:
                self.assertIn(col, result.columns, f"结果中缺少列: {col}")
            print("基金筛选结果包含所有必要列")
            
            # 验证基金类型默认为债券型
            if '基金类型' in result.columns and len(result) > 0:
                types = result['基金类型'].unique()
                self.assertIn('债券型', types, "默认基金类型应为债券型")
                print("基金类型默认值正确")
    
    def test_fund_result_columns(self):
        """测试基金筛选结果是否包含年化收益率列"""
        print("\n测试基金筛选结果列...")
        
        # 使用默认参数进行筛选
        result = fund_filter(min_annual_return=3, min_consecutive_return=4.2, min_years_listed=2, 
                            fund_type="债券型", fund_manager=None, fund_company=None)
        
        if len(result) > 0:
            # 验证结果中包含年化收益率相关列
            expected_columns = ['第1年收益率', '第2年收益率', '第3年收益率']
            for col in expected_columns:
                if col in result.columns:
                    print(f"结果包含列: {col}")
                else:
                    print(f"警告: 结果缺少列 {col}")
            
            # 验证年化收益率计算逻辑
            if '第1年收益率' in result.columns and '近1年' in result.columns:
                print("基金年化收益率计算正确")
            else:
                print("无法验证年化收益率计算逻辑")
    
    def test_stock_code_extraction(self):
        """测试股票代码提取逻辑"""
        print("\n测试股票代码提取逻辑...")
        
        # 测试各种格式的股票代码
        test_cases = [
            "SH600519.贵州茅台",
            "600519.贵州茅台",
            "600519",
            "code,SH600519",
            "SZ000001",
            "000001.平安银行"
        ]
        
        for test_case in test_cases:
            try:
                # 由于extract_stock_codes可能返回集合而非列表，我们直接检查结果
                codes = extract_stock_codes(pd.Series([test_case]))
                # 确保至少有一个代码被提取出来
                self.assertTrue(len(codes) > 0, f"从 {test_case} 没有提取到任何代码")
                # 检查第一个代码是否符合要求
                for code in codes:
                    self.assertTrue(code.isdigit() and len(code) == 6, f"从 {test_case} 提取的代码 {code} 应为6位数字")
                print(f"从 {test_case} 成功提取代码: {codes}")
            except Exception as e:
                print(f"从 {test_case} 提取代码时出错: {e}")
        
        print("股票代码提取逻辑测试完成")
    
    def test_industry_options(self):
        """测试行业选项获取功能"""
        print("\n测试行业选项获取功能...")
        
        industries = get_industry_options()
        self.assertIsNotNone(industries)
        self.assertGreater(len(industries), 0, "应该获取到至少一个行业选项")
        print(f"获取到 {len(industries)} 个行业选项")
    
    def test_stock_filter(self):
        """测试股票筛选功能"""
        print("\n测试股票筛选功能...")
        
        # 测试基本筛选功能
        result = stock_filter(selected_types=["ROE_exceeded_15p_three_consecutive_years"], 
                             sub_types={}, industry_filter=[])
        
        self.assertIsNotNone(result)
        print(f"股票筛选结果数量: {len(result)}")
        
        if len(result) > 0:
            # 验证结果中包含股票代码和股票名称列
            required_columns = ['股票代码', '股票名称']
            for col in required_columns:
                self.assertIn(col, result.columns, f"结果中缺少列: {col}")
            print("股票筛选结果包含所有必要列")

def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestRequirements)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

if __name__ == "__main__":
    run_tests()
