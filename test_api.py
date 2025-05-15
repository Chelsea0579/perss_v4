"""
API测试脚本
"""
import requests
import json

# 后端API地址
BASE_URL = "http://localhost:8000/api"

def test_get_introduction():
    """测试获取系统介绍"""
    url = f"{BASE_URL}/introduction"
    print(f"请求: GET {url}")
    try:
        response = requests.get(url)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"响应内容: {response.json()}")
            return True
        else:
            print(f"错误响应: {response.text}")
            return False
    except Exception as e:
        print(f"请求异常: {e}")
        return False

def test_get_self_rate():
    """测试获取自评量表"""
    url = f"{BASE_URL}/self-rate"
    print(f"请求: GET {url}")
    try:
        response = requests.get(url)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            print(f"响应内容: {response.json()}")
            return True
        else:
            print(f"错误响应: {response.text}")
            return False
    except Exception as e:
        print(f"请求异常: {e}")
        return False

def test_create_user_profile():
    """测试创建用户画像"""
    url = f"{BASE_URL}/user-profile"
    print(f"请求: POST {url}")
    
    # 测试数据
    data = {
        "name": "测试用户",
        "grade": "大三",
        "major": "计算机科学",
        "gender": "男",
        "cet4_taken": "是",
        "cet4_score": "500",
        "cet4_reading_score": "150",
        "cet6_taken": "否",
        "cet6_score": "",
        "cet6_reading_score": "",
        "other_scores": "托福: 90",
        "exam_name": "四级",
        "total_score": "500",
        "reading_score": "150"
    }
    
    print(f"请求数据: {json.dumps(data, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=data)
        print(f"状态码: {response.status_code}")
        print(f"请求URL: {response.request.url}")
        print(f"请求头: {response.request.headers}")
        print(f"请求体: {response.request.body.decode('utf-8')}")
        
        if response.status_code == 200:
            print(f"响应内容: {response.json()}")
            return True
        else:
            print(f"错误响应: {response.text}")
            return False
    except Exception as e:
        print(f"请求异常: {e}")
        return False

def list_all_routes():
    """列出所有可用的路由"""
    try:
        response = requests.get("http://localhost:8000/openapi.json")
        if response.status_code == 200:
            api_schema = response.json()
            print("\n可用的API路由:")
            for path, methods in api_schema.get("paths", {}).items():
                for method, details in methods.items():
                    print(f"{method.upper()} {path}: {details.get('summary', '无描述')}")
        else:
            print("无法获取API路由列表")
    except Exception as e:
        print(f"获取API路由列表失败: {e}")

if __name__ == "__main__":
    print("===== API测试开始 =====")
    
    print("\n测试获取系统介绍:")
    test_get_introduction()
    
    print("\n测试获取自评量表:")
    test_get_self_rate()
    
    print("\n测试创建用户画像:")
    test_create_user_profile()
    
    # 列出所有路由
    list_all_routes()
    
    print("\n===== API测试结束 =====") 