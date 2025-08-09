"""
工具函数模块
"""

import os
import json
import streamlit as st
import pandas as pd
from datetime import datetime
import hashlib
from modules.config import USER_DATA_PATH

def load_css():
    """加载自定义CSS样式"""
    st.markdown("""
    <style>
        .sidebar .sidebar-content {
            background-color: #f8f9fa;
        }
        .sidebar .sidebar-content .block-container {
            padding: 1rem;
        }
        .nav-section {
            background-color: white;
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .nav-title {
            font-size: 1.2rem;
            font-weight: bold;
            color: #1f2937;
            margin-bottom: 1rem;
            text-align: center;
        }
        .nav-item {
            display: block;
            padding: 0.75rem 1rem;
            margin: 0.25rem 0;
            background-color: #f3f4f6;
            border-radius: 0.375rem;
            text-decoration: none;
            color: #374151;
            transition: all 0.3s ease;
            border: 1px solid #e5e7eb;
        }
        .nav-item:hover {
            background-color: #3b82f6;
            color: white;
            transform: translateX(5px);
        }
        .nav-item.active {
            background-color: #3b82f6;
            color: white;
            font-weight: bold;
        }
        .user-section {
            background-color: #e0f2fe;
            padding: 1rem;
            border-radius: 0.5rem;
            margin-top: 2rem;
            border: 1px solid #0288d1;
        }
        .user-status {
            text-align: center;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        .metric-card {
            background-color: white;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border-left: 4px solid #3b82f6;
        }
        .data-table {
            font-size: 0.9rem;
        }
        .positive {
            color: #10b981 !important;
            font-weight: bold;
        }
        .negative {
            color: #ef4444 !important;
            font-weight: bold;
        }
    </style>
    """, unsafe_allow_html=True)

def format_number(number, is_percentage=False, decimal_places=2):
    """格式化数字显示"""
    if pd.isna(number):
        return "---"
    
    try:
        number = float(number)
        if is_percentage:
            return f"{number:.{decimal_places}f}%"
        else:
            return f"{number:,.{decimal_places}f}"
    except (ValueError, TypeError):
        return str(number)

def user_auth(username, password):
    """
    简单的用户认证
    注意：这只是一个演示用的简单实现，实际应用中应使用更安全的方式
    """
    # 简单的哈希处理密码，实际应用中应使用更安全的方式
    hashed = hashlib.sha256(password.encode()).hexdigest()
    
    # 检查用户目录
    user_file = os.path.join(USER_DATA_PATH, "users.json")
    
    # 创建示例用户数据（如果文件不存在）
    if not os.path.exists(user_file):
        default_users = {
            "admin": {
                "password": hashlib.sha256("admin123".encode()).hexdigest(),
                "role": "admin",
                "created_at": datetime.now().isoformat()
            },
            "user": {
                "password": hashlib.sha256("user123".encode()).hexdigest(),
                "role": "user",
                "created_at": datetime.now().isoformat()
            }
        }
        
        os.makedirs(os.path.dirname(user_file), exist_ok=True)
        with open(user_file, "w") as f:
            json.dump(default_users, f, indent=2)
    
    # 读取用户数据
    try:
        with open(user_file, "r") as f:
            users = json.load(f)
            
        if username in users and users[username]["password"] == hashed:
            return True
    except Exception as e:
        st.error(f"认证错误: {e}")
    
    return False

def save_user_preferences(user_id, category, name, data):
    """
    保存用户偏好设置
    
    Args:
        user_id: 用户ID
        category: 设置类别（如 'stock_filters', 'fund_filters'）
        name: 设置名称
        data: 要保存的数据
    """
    if not user_id:
        return False
    
    # 用户配置文件路径
    user_prefs_dir = os.path.join(USER_DATA_PATH, "preferences")
    user_file = os.path.join(user_prefs_dir, f"{user_id}.json")
    
    # 创建目录（如果不存在）
    os.makedirs(user_prefs_dir, exist_ok=True)
    
    # 读取现有配置（如果有）
    prefs = {}
    if os.path.exists(user_file):
        try:
            with open(user_file, "r") as f:
                prefs = json.load(f)
        except:
            prefs = {}
    
    # 确保类别存在
    if category not in prefs:
        prefs[category] = {}
    
    # 保存数据
    prefs[category][name] = data
    
    # 写回文件
    try:
        with open(user_file, "w") as f:
            json.dump(prefs, f, indent=2)
        return True
    except Exception as e:
        st.error(f"保存设置失败: {e}")
        return False

def get_user_preferences(user_id, category=None):
    """
    获取用户偏好设置
    
    Args:
        user_id: 用户ID
        category: 设置类别（如果不提供则返回所有类别）
    
    Returns:
        dict: 用户偏好设置
    """
    if not user_id:
        return {}
    
    # 用户配置文件路径
    user_file = os.path.join(USER_DATA_PATH, "preferences", f"{user_id}.json")
    
    # 如果文件不存在，返回空字典
    if not os.path.exists(user_file):
        return {}
    
    # 读取配置
    try:
        with open(user_file, "r") as f:
            prefs = json.load(f)
        
        # 如果指定了类别，只返回该类别的设置
        if category and category in prefs:
            return prefs[category]
        elif category:
            return {}
        
        return prefs
    except Exception as e:
        st.error(f"读取设置失败: {e}")
        return {}
