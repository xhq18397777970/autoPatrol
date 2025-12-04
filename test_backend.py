#!/usr/bin/env python3
"""
后端服务测试脚本
用于诊断Flask API服务器的连接问题
"""

import requests
import json
import sys

def test_backend_connection():
    """测试后端连接"""
    base_url = "http://localhost:5000"
    
    print("🔍 开始测试后端服务...")
    
    # 测试健康检查接口
    try:
        print("\n1. 测试健康检查接口 GET /api/health")
        response = requests.get(f"{base_url}/api/health", timeout=5)
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.text}")
        
        if response.status_code == 200:
            print("   ✅ 健康检查通过")
        else:
            print(f"   ❌ 健康检查失败: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ 连接失败 - 后端服务器可能未启动")
        print("   💡 请运行: python app.py")
        return False
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")
        return False
    
    # 测试分析接口
    try:
        print("\n2. 测试分析接口 POST /api/analyze")
        test_data = {
            "query": "测试查询"
        }
        response = requests.post(
            f"{base_url}/api/analyze", 
            json=test_data,
            timeout=30
        )
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.text[:200]}...")  # 只显示前200个字符
        
        if response.status_code == 200:
            print("   ✅ 分析接口可访问")
        elif response.status_code == 500:
            print("   ⚠️  分析接口返回500错误 - 可能是MCP服务未启动")
        else:
            print(f"   ❌ 分析接口异常: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ 分析接口请求异常: {e}")
    
    return True

def check_mcp_service():
    """检查MCP服务"""
    print("\n3. 检查MCP服务 (127.0.0.1:10027)")
    try:
        response = requests.get("http://127.0.0.1:10027/sse", timeout=5)
        print(f"   状态码: {response.status_code}")
        print("   ✅ MCP服务正常运行")
    except requests.exceptions.ConnectionError:
        print("   ❌ MCP服务连接失败")
        print("   💡 请确保监控服务在127.0.0.1:10027端口运行")
    except Exception as e:
        print(f"   ❌ MCP服务检查异常: {e}")

def main():
    print("=" * 50)
    print("🚀 CPU数据分析系统 - 后端服务诊断")
    print("=" * 50)
    
    # 测试后端连接
    backend_ok = test_backend_connection()
    
    if backend_ok:
        # 检查MCP服务
        check_mcp_service()
    
    print("\n" + "=" * 50)
    print("📋 诊断建议:")
    print("1. 如果健康检查失败，请运行: python app.py")
    print("2. 如果MCP服务失败，请启动监控服务")
    print("3. 如果分析接口500错误，通常是MCP服务问题")
    print("4. 确保所有依赖已安装: pip install -r requirements.txt")
    print("=" * 50)

if __name__ == "__main__":
    main()