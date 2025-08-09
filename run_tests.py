#!/usr/bin/env python3
"""
综合测试脚本 - 验证系统是否满足所有需求

此脚本将运行功能测试和提供UI测试指导，以验证系统是否满足所有需求。
"""

import os
import sys
import subprocess
import time
from test_requirements import run_tests

def print_header(text):
    """打印带格式的标题"""
    print("\n" + "=" * 80)
    print(f" {text} ".center(80, "="))
    print("=" * 80 + "\n")

def run_functional_tests():
    """运行功能测试"""
    print_header("运行功能测试")
    run_tests()

def guide_ui_tests():
    """提供UI测试指导"""
    print_header("UI测试指导")
    print("要验证UI需求，请运行以下命令：")
    print("\nstreamlit run test_ui_requirements.py\n")
    print("这将启动一个交互式UI测试工具，帮助您验证所有UI相关需求。")

def run_app():
    """运行主应用程序"""
    print_header("启动主应用程序")
    print("正在启动主应用程序，请在浏览器中验证功能...")
    
    try:
        # 启动应用程序
        process = subprocess.Popen(["streamlit", "run", "app_clean.py"])
        
        # 等待几秒钟让应用程序启动
        time.sleep(3)
        
        # 提示用户验证
        print("\n应用程序已启动，请在浏览器中验证以下功能：")
        print("\n1. 顶部导航栏功能是否正常")
        print("2. 基金筛选功能是否符合需求")
        print("3. 股票筛选功能是否符合需求")
        print("4. 首页布局是否符合需求")
        
        print("\n完成验证后，按 Ctrl+C 停止应用程序")
        
        # 等待用户手动停止
        process.wait()
    except KeyboardInterrupt:
        # 用户按下Ctrl+C
        process.terminate()
        print("\n应用程序已停止")
    except Exception as e:
        print(f"\n启动应用程序时出错: {e}")

def main():
    """主函数"""
    print_header("投资理财筛选系统 - 需求验证")
    
    print("此脚本将验证系统是否满足所有需求，包括：")
    print("1. 功能测试 - 验证基金筛选、股票筛选等核心功能")
    print("2. UI测试指导 - 提供UI验证工具的使用方法")
    print("3. 应用程序验证 - 启动主应用程序进行手动验证\n")
    
    while True:
        print("\n请选择要执行的操作：")
        print("1. 运行功能测试")
        print("2. 查看UI测试指导")
        print("3. 启动主应用程序进行验证")
        print("4. 退出")
        
        choice = input("\n请输入选项 (1-4): ")
        
        if choice == "1":
            run_functional_tests()
        elif choice == "2":
            guide_ui_tests()
        elif choice == "3":
            run_app()
        elif choice == "4":
            print("\n感谢使用测试工具！")
            break
        else:
            print("\n无效的选项，请重新输入")

if __name__ == "__main__":
    main()
