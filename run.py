"""
PERSS系统启动脚本
启动FastAPI后端和Vue.js前端
"""
import os
import subprocess
import threading
import time
import webbrowser
import sys
import logging
import sqlite3
from pathlib import Path
import shutil

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("PERSS")

# 项目根目录
ROOT_DIR = Path(__file__).resolve().parent
BACKEND_PORT = 8000
FRONTEND_PORT = 8091
DATABASE_PATH = ROOT_DIR / "PERSS_DB.sqlite"

def check_npm_installed():
    """检查npm是否安装"""
    try:
        # 尝试执行npm --version命令
        npm_path = shutil.which("npm")
        if npm_path:
            logger.info(f"找到npm: {npm_path}")
            return True
        else:
            logger.warning("未找到npm命令，将只启动后端服务")
            return False
    except Exception as e:
        logger.warning(f"检查npm失败: {e}")
        return False

def initialize_database():
    """初始化数据库，确保基本表结构存在"""
    logger.info("检查数据库状态...")
    
    # 检查数据库文件是否存在
    db_exists = os.path.exists(DATABASE_PATH)
    if not db_exists:
        logger.info(f"数据库文件不存在，将在 {DATABASE_PATH} 创建")
    
    # 导入数据库初始化函数，避免循环导入
    from app.database import get_db_connection
    try:
        # 获取连接会触发数据库初始化
        conn = get_db_connection()
        conn.close()
        logger.info("数据库初始化完成")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        return False
    
    return True

def run_backend():
    """运行FastAPI后端"""
    logger.info("正在启动后端服务...")
    os.chdir(ROOT_DIR)
    
    try:
        # 使用uvicorn启动FastAPI应用
        backend_cmd = [
            sys.executable, "-m", "uvicorn", 
            "app.main:app", "--host", "0.0.0.0", 
            "--port", str(BACKEND_PORT), "--reload"
        ]
        
        backend_process = subprocess.Popen(
            backend_cmd, 
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        
        # 实时输出后端日志
        for line in backend_process.stdout:
            logger.info(f"[后端] {line.strip()}")
            
        backend_process.wait()
    except Exception as e:
        logger.error(f"后端启动失败: {e}")
        raise

def run_frontend():
    """运行Vue.js前端"""
    logger.info("正在启动前端服务...")
    
    # 检查前端目录是否存在
    frontend_dir = ROOT_DIR / "frontend"
    if not os.path.exists(frontend_dir):
        logger.error(f"前端目录不存在: {frontend_dir}")
        return
    
    os.chdir(frontend_dir)
    
    try:
        # 检查是否有node_modules目录，如果没有提示需要安装依赖
        if not os.path.exists(frontend_dir / "node_modules"):
            logger.warning("未检测到node_modules目录，可能需要先执行 'npm install'")
        
        # 检查npm是否可用
        if not shutil.which("npm"):
            logger.error("未找到npm命令，无法启动前端服务。请确保安装了Node.js和npm。")
            return
        
        # 使用npm运行Vue开发服务器
        frontend_cmd = [
            "npm", "run", "serve", "--", 
            "--port", str(FRONTEND_PORT)
        ]
        
        frontend_process = subprocess.Popen(
            frontend_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        
        # 实时输出前端日志
        for line in frontend_process.stdout:
            logger.info(f"[前端] {line.strip()}")
            
        frontend_process.wait()
    except Exception as e:
        logger.error(f"前端启动失败: {e}")
        # 不抛出异常，让程序继续运行，只是前端无法启动

def open_api_docs():
    """打开API文档页面"""
    time.sleep(3)  # 等待服务启动
    url = f"http://localhost:{BACKEND_PORT}/docs"
    logger.info(f"正在打开API文档: {url}")
    try:
        webbrowser.open(url)
    except Exception as e:
        logger.error(f"打开浏览器失败: {e}")

def open_browser():
    """打开浏览器，访问前端页面"""
    time.sleep(5)  # 等待服务启动
    
    # 检查npm是否安装，决定打开哪个URL
    if check_npm_installed():
        url = f"http://localhost:{FRONTEND_PORT}"
        logger.info(f"正在打开前端页面: {url}")
    else:
        url = f"http://localhost:{BACKEND_PORT}/docs"
        logger.info(f"前端不可用，正在打开API文档: {url}")
    
    try:
        webbrowser.open(url)
    except Exception as e:
        logger.error(f"打开浏览器失败: {e}")

def main():
    """主函数，启动所有服务"""
    try:
        # 初始化数据库
        if not initialize_database():
            logger.error("无法初始化数据库，系统启动失败")
            return
            
        logger.info("系统初始化完成，开始启动服务...")
        
        # 创建并启动后端线程
        backend_thread = threading.Thread(target=run_backend)
        backend_thread.daemon = True
        backend_thread.start()
        
        # 等待后端启动完成
        time.sleep(2)
        
        # 检查npm是否安装
        npm_available = check_npm_installed()
        
        if npm_available:
            # 创建并启动前端线程
            frontend_thread = threading.Thread(target=run_frontend)
            frontend_thread.daemon = True
            frontend_thread.start()
        else:
            # 如果npm不可用，只打开API文档
            api_docs_thread = threading.Thread(target=open_api_docs)
            api_docs_thread.daemon = True
            api_docs_thread.start()
        
        # 打开浏览器
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # 等待后端线程结束
        backend_thread.join()
        
    except KeyboardInterrupt:
        logger.info("接收到中断信号，正在关闭服务...")
    except Exception as e:
        logger.error(f"启动服务时出错: {e}")
    finally:
        logger.info("服务已关闭")

if __name__ == "__main__":
    main()