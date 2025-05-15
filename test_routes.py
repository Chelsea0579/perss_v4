"""
测试FastAPI路由注册
"""
from fastapi import FastAPI
from fastapi.routing import APIRouter
import importlib
import inspect
import json

# 导入路由模块
try:
    from app.routers import planning, execution, feedback
    from app.config import API_PREFIX
    
    print("=== 成功导入路由模块 ===")
    print(f"API前缀: {API_PREFIX}")
    
    # 检查planning路由
    print("\n=== Planning路由 ===")
    for route in planning.router.routes:
        print(f"路径: {route.path}, 方法: {route.methods}, 名称: {route.name}")
    
    # 检查user-profile路由
    print("\n=== 查找user-profile路由 ===")
    found = False
    for route in planning.router.routes:
        if "user-profile" in route.path:
            found = True
            print(f"找到user-profile路由: {route.path}, 方法: {route.methods}")
    
    if not found:
        print("未找到user-profile路由!")
    
    # 尝试直接调用create_profile函数
    print("\n=== 测试create_profile函数 ===")
    try:
        from app.schemas.user import UserProfileCreate
        
        # 创建一个测试用户数据
        test_user = UserProfileCreate(
            name="测试用户",
            grade="大三",
            major="计算机科学",
            gender="男"
        )
        
        # 打印用户数据
        print(f"测试用户数据: {test_user.dict()}")
        
        # 查看函数声明
        create_profile_func = getattr(planning, "create_profile", None)
        if create_profile_func:
            sig = inspect.signature(create_profile_func)
            print(f"函数签名: {sig}")
            
            # 检查函数是否是异步函数
            if inspect.iscoroutinefunction(create_profile_func):
                print("create_profile是异步函数")
            else:
                print("create_profile不是异步函数")
        else:
            print("未找到create_profile函数")
            
    except Exception as e:
        print(f"测试create_profile函数时出错: {e}")
        import traceback
        traceback.print_exc()
        
except Exception as e:
    print(f"导入路由模块出错: {e}")
    import traceback
    traceback.print_exc()
    
print("\n=== 路由测试完成 ===") 