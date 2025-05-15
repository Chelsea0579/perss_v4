"""
数据库连接测试脚本
"""
import logging
import os
import sqlite3
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("DB_TEST")

# 数据库路径
ROOT_DIR = Path(__file__).resolve().parent
DATABASE_PATH = ROOT_DIR / "PERSS_DB.sqlite"

def test_db_connection():
    """测试数据库连接并初始化基本表结构"""
    logger.info(f"测试数据库连接: {DATABASE_PATH}")
    
    try:
        # 确保数据库目录存在
        db_dir = os.path.dirname(DATABASE_PATH)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
            logger.info(f"创建数据库目录: {db_dir}")
        
        # 连接数据库
        conn = sqlite3.connect(str(DATABASE_PATH))
        conn.row_factory = sqlite3.Row
        logger.info("数据库连接成功")
        
        # 创建游标
        cursor = conn.cursor()
        
        # 创建测试表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_table (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
        ''')
        logger.info("测试表创建成功")
        
        # 插入测试数据
        cursor.execute('INSERT INTO test_table (name) VALUES (?)', ("测试数据",))
        logger.info("测试数据插入成功")
        
        # 查询测试数据
        cursor.execute('SELECT * FROM test_table')
        rows = cursor.fetchall()
        logger.info(f"查询结果: {len(rows)} 条数据")
        for row in rows:
            logger.info(f"ID: {row['id']}, Name: {row['name']}")
        
        # 提交事务并关闭连接
        conn.commit()
        conn.close()
        logger.info("数据库测试完成")
        
        return True
    except Exception as e:
        logger.error(f"数据库测试失败: {e}")
        return False

if __name__ == "__main__":
    if test_db_connection():
        print("数据库连接测试成功!")
    else:
        print("数据库连接测试失败!") 