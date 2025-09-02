"""
测试股票查询功能
"""

from modules.stock_filter import search_stock
from modules.utils import get_current_date

def main():
    """主函数"""
    # 查询测试股票
    print("开始测试股票查询功能")
    print("\n====== 测试1: 查询索菲亚 ======")
    result = search_stock("索菲亚")
    
    # 输出结果
    if result['stock_info']:
        print(f"股票信息: {result['stock_info']['股票名称']} ({result['stock_info']['股票代码']})")
        print("所属分类:")
        for category in result['categories']:
            print(f"- {category}")
        print(f"总计: {len(result['categories'])}个分类")
    else:
        print("未找到股票信息")
    
    print("\n====== 测试2: 查询贵州茅台 ======")
    result = search_stock("贵州茅台")
    
    # 输出结果
    if result['stock_info']:
        print(f"股票信息: {result['stock_info']['股票名称']} ({result['stock_info']['股票代码']})")
        print("所属分类:")
        for category in result['categories']:
            print(f"- {category}")
        print(f"总计: {len(result['categories'])}个分类")
    else:
        print("未找到股票信息")
    
    print("\n请查看search_debug.txt文件以获取详细的调试信息")

if __name__ == "__main__":
    main()
