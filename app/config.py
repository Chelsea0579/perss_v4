"""配置文件"""
import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# API 配置
DEEPSEEK_API_KEY = "put your API here"
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# 数据库配置
# 使用Path对象确保跨平台路径兼容性
DATABASE_PATH = str(BASE_DIR / "PERSS_DB.sqlite")

# 如果数据库目录不存在，则创建
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

# CORS 设置
CORS_ORIGINS = [
    "http://localhost:8080",  # Vue开发服务器默认端口
    "http://localhost:8091",  # 自定义Vue端口
    "http://127.0.0.1:8080",
    "http://127.0.0.1:8091",
]

# API前缀
API_PREFIX = "/api"

# 调试模式
DEBUG = False
