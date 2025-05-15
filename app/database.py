"""数据库访问模块"""
import logging
import sqlite3
import os
from typing import List, Dict, Any, Union, Optional, Tuple

from app.config import DATABASE_PATH, DEBUG

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

_DB_INITIALIZED_THIS_RUN = False

def get_db_connection():
    """获取数据库连接"""
    global _DB_INITIALIZED_THIS_RUN
    try:
        # 确保数据库目录存在
        db_dir = os.path.dirname(DATABASE_PATH)
        os.makedirs(db_dir, exist_ok=True)
            
        db_exists = os.path.exists(DATABASE_PATH)
        
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row  # 返回字典形式的结果
        
        # 如果数据库未在此次运行中初始化过，并且（数据库文件不存在 或 DEBUG模式为True）
        if not _DB_INITIALIZED_THIS_RUN and (not db_exists or DEBUG):
            logger.info(f"数据库初始化条件满足：_DB_INITIALIZED_THIS_RUN={_DB_INITIALIZED_THIS_RUN}, db_exists={db_exists}, DEBUG={DEBUG}")
            _initialize_database(conn)
            _DB_INITIALIZED_THIS_RUN = True
            logger.info("数据库已在此次运行中初始化。_DB_INITIALIZED_THIS_RUN 设置为 True。")
        elif _DB_INITIALIZED_THIS_RUN:
            logger.debug("数据库已在此次运行中初始化过，跳过。")
        elif db_exists and not DEBUG:
            logger.debug("数据库已存在且非 DEBUG 模式，跳过初始化。")
            
        return conn
    except sqlite3.Error as e:
        logger.error(f"数据库连接错误: {e}")
        raise


def _initialize_database(conn):
    """初始化数据库表"""
    try:
        cursor = conn.cursor()
        
        # 强制删除并重建introduction表
        try:
            cursor.execute('DROP TABLE IF EXISTS introduction')
            logger.info("删除旧的introduction表")
        except sqlite3.Error as e:
            logger.warning(f"删除introduction表失败: {e}")
        
        # 创建系统介绍表 - 确保列名为 content
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS introduction (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL
        )
        ''')
        
        # 检查是否有数据，没有则插入默认数据
        cursor.execute('SELECT COUNT(*) FROM introduction')
        if cursor.fetchone()[0] == 0:
            default_intro = "同学你好！欢迎使用英语阅读个性化学习支持系统。这个系统旨在帮助你提升英语阅读能力，尤其是阅读策略这方面。该系统的设计基于自我调节学习理论，该理论强调学习者在学习过程中通过计划、执行和反馈的循环，不断调整自己的学习策略，提升学习效果。系统按照计划-执行-反馈的三个阶段设计一系列活动，帮助你在阅读过程中不断优化自己的阅读策略。"
            cursor.execute('INSERT INTO introduction (content) VALUES (?)', (default_intro,))
            logger.info("已插入默认系统介绍")
        
        # 创建自评量表 - 确保列名为 content
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS self_rate (
            id INTEGER PRIMARY KEY,
            content TEXT NOT NULL
        )
        ''')
        
        # 检查是否有数据，没有则插入默认数据
        cursor.execute('SELECT COUNT(*) FROM self_rate')
        if cursor.fetchone()[0] == 0:
            default_items = [
                "我能借助图片读懂语言简单的短小故事，理解基本信息，如人物、时间、地点等。",
                "我能读懂简单的材料，如儿歌、童谣等，辨认常见词。",
                "我能读懂语言简单、话题熟悉的简短材料，获取具体信息、理解主要内容。",
                "我能在读含有生词的小短文时，能借助插图或其他手段理解短文内容。",
                "我能读懂简单的应用文，如书信、通知、告示等，提取关键信息。",
                "我能读懂语言简单、话题熟悉的简短材料，理解隐含意义，归纳要点。",
                "我能在读语言简单、话题熟悉的议论文时，能借助衔接词等理解信息之间的关系。",
                "我能读懂语言简单、不同类型的材料，如简短故事、书信等，提取细节信息，概括主旨要义。",
                "我能读懂语言简单、题材广泛的记叙文和议论文，区分事实和观点，进行简单推断。",
                "我能通过分析句子和篇章结构读懂语言较复杂的材料，理解意义之间的关系。",
                "我能在读语言较复杂、话题丰富，如有关教育、科技、文化等的材料时，能理解主题思想，分析语言特点，领会文化内涵。",
                "我能读懂语言较复杂的论述性材料，如社会时评、书评等，分辨不同观点。",
                "我能读懂语言较复杂、相关专业领域的不同类型材料，如文学作品、新闻报道、商务公文等时，能把握重要相关信息，并对语言和内容进行简单的评析。",
                "我能读懂语言较复杂的文学作品、新闻报道等材料，推断作者的情感态度。",
                "我能通过浏览专业文献的索引，准确检索目标信息。",
                "我能在读语言复杂、专业性较强的不同类型材料，如文学原著、科技文章、社会时评等时，能整合相关内容，分析作者观点立场。",
                "我能在读语言较复杂、有关文化的作品时，能批判性分析不同的文化现象。",
                "我能在读语言复杂、专业性较强的材料时，能通过研读多篇同题材的材料，深刻理解隐含信息。",
                "我能读懂语言复杂、题材广泛的材料，综合鉴赏材料的语言艺术及社会价值等。",
                "我能读懂语言复杂、熟悉领域的学术性材料时，能通过分析文本，对语言和思想内容进行深度的思辨性评析。",
                "能读懂语言复杂、跨专业的材料，从多视角综合分析文本内容。",
                "能读懂语言复杂、内容深奥的相关专业性材料，对材料进行综合鉴赏和批判性评价。"
            ] # 你提供的22条文本
            for i, item_text in enumerate(default_items, 1):
                cursor.execute('INSERT INTO self_rate (id, content) VALUES (?, ?)', (i, item_text))
        
        # 创建策略量表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Strategies (
            id INTEGER PRIMARY KEY,
            content TEXT NOT NULL
        )
        ''')
        
        # 检查是否有数据，没有则插入默认数据
        cursor.execute('SELECT COUNT(*) FROM Strategies')
        if cursor.fetchone()[0] == 0:
            default_items = [
                "I preview the reading material before I begin to read.",
                "Before I begin reading, I think about the topic to see what I already know about it.",
                "I try to predict what the material is about when I read.",
                "While I am reading, I periodically check if the material is making sense to me.",
                "I adjust my reading speed according to what I'm reading."
            ]
            for i, item in enumerate(default_items, 1):
                cursor.execute('INSERT INTO Strategies (id, content) VALUES (?, ?)', (i, item))
        
        # 强制删除并重建User_Profile表
        try:
            cursor.execute('DROP TABLE IF EXISTS User_Profile')
            logger.info("删除旧的User_Profile表")
        except sqlite3.Error as e:
            logger.warning(f"删除User_Profile表失败: {e}")

        # 创建用户画像表（使用User_Profile代替空格命名）
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS User_Profile (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE,
            grade TEXT,
            major TEXT,
            gender TEXT,
            post_score TEXT,
            after_score TEXT,
            false_id TEXT,
            post_strategies_score TEXT,
            after_strategies_score TEXT,
            exam1_score TEXT,
            exam2_score TEXT,
            exam3_score TEXT,
            exam4_score TEXT,
            "Have you taken the CET-4 exam:" TEXT,
            "CET-4 score" TEXT,
            "CET-4 reading score" TEXT,
            "Have you taken the CET-6 exam" TEXT,
            "CET-6 score" TEXT,
            "CET-6 reading score" TEXT,
            "Other English scores for reference" TEXT,
            "Exam name" TEXT,
            "Total score" TEXT,
            "Reading score" TEXT
        )
        ''')
        
        # 提交更改
        conn.commit()
        logger.info("数据库初始化成功")
    except sqlite3.Error as e:
        conn.rollback()
        logger.error(f"数据库初始化错误: {e}")
        raise


def get_introduction() -> str:
    """获取系统介绍内容"""
    logger.info("获取系统介绍")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT content FROM introduction LIMIT 1') # 确保查询的是 content 列
        result = cursor.fetchone()
        conn.close()
        
        if result and result["content"]: # 如果 row_factory 是 sqlite3.Row，可以通过列名访问
            return result["content"]
        elif result and result[0]: # 备用访问方式
            return result[0]
        
        logger.warning("数据库中未找到系统介绍内容，返回默认介绍。")
        return "同学你好！欢迎使用英语阅读个性化学习支持系统。"
    except sqlite3.Error as e:
        logger.error(f"获取系统介绍错误: {e}", exc_info=True)
        return "同学你好！欢迎使用英语阅读个性化学习支持系统（数据库错误）。"


def get_self_rate_items() -> List[Dict[str, Any]]:
    """获取自评量表项目"""
    logger.info("获取自评量表")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, content FROM self_rate ORDER BY id')
        rows = cursor.fetchall()
        conn.close()
        
        result = []
        for row in rows:
            item = {"id": row["id"], "content": row["content"]}
            result.append(item)
        
        if not result:
            logger.warning("从数据库获取的 self_rate_items 为空列表")
        else:
            logger.info(f"第一个获取到的 self_rate item: {result[0]}") 
            
        return result
    except sqlite3.Error as e:
        logger.error(f"获取自评量表错误: {e}", exc_info=True)
        return []


def get_strategy_items() -> List[Dict[str, Any]]:
    """获取策略量表项目"""
    logger.info("获取策略量表")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, content FROM Strategies ORDER BY id')
        rows = cursor.fetchall()
        conn.close()
        
        # 将sqlite3.Row转换为字典
        result = []
        for row in rows:
            item = {"id": row["id"], "content": row["content"]}
            result.append(item)
        return result
    except sqlite3.Error as e:
        logger.error(f"获取策略量表错误: {e}")
        return []


def get_cognitive_strategies() -> List[Dict[str, Any]]:
    """获取认知策略项目"""
    logger.info("获取认知策略")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM CognitiveStrategies')
        rows = cursor.fetchall()
        conn.close()
        
        # 将sqlite3.Row转换为字典
        result = []
        for row in rows:
            item = {}
            for key in row.keys():
                item[key] = row[key]
            result.append(item)
        return result
    except sqlite3.Error as e:
        logger.error(f"获取认知策略错误: {e}")
        return []


def get_exam_by_id(exam_id: int) -> Dict[str, Any]:
    """根据ID获取试卷"""
    logger.info(f"获取试卷: {exam_id}")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM exam WHERE id = ?', (exam_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            logger.warning(f"试卷不存在: {exam_id}")
            return {}
        
        # 将sqlite3.Row转换为字典
        result = {}
        for key in row.keys():
            result[key] = row[key]
        return result
    except sqlite3.Error as e:
        logger.error(f"获取试卷错误: {e}")
        return {}


def create_user_profile(user_data: Dict[str, Any]) -> bool:
    """创建用户画像"""
    logger.info(f"创建用户画像: {user_data.get('name', '未知用户')}")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查用户名是否为空
        name = user_data.get("name")
        if not name:
            logger.warning("用户名不能为空")
            conn.close()
            return False
        
        # 构建列和值
        columns = []
        values = []
        placeholders = []
        
        for key, value in user_data.items():
            columns.append(f'"{key}"')
            values.append(value)
            placeholders.append('?')
        
        # 执行插入
        query = f'INSERT INTO User_Profile ({", ".join(columns)}) VALUES ({", ".join(placeholders)})'
        cursor.execute(query, values)
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        logger.error(f"创建用户画像错误: {e}")
        return False


def update_user_profile(user_data: Dict[str, Any]) -> bool:
    """更新用户画像"""
    logger.info(f"更新用户画像: {user_data.get('name', '未知用户')}")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查用户名是否为空
        name = user_data.get("name")
        if not name:
            logger.warning("用户名不能为空")
            conn.close()
            return False
        
        # 检查用户是否存在
        cursor.execute('SELECT * FROM User_Profile WHERE name = ?', (name,))
        user = cursor.fetchone()
        
        if not user:
            # 用户不存在，创建新用户
            conn.close()
            return create_user_profile(user_data)
        
        # 用户存在，更新用户数据
        set_clause = []
        values = []
        
        for key, value in user_data.items():
            if key != "name":  # 不更新name字段
                set_clause.append(f'"{key}" = ?')
                values.append(value)
        
        # 添加WHERE条件
        values.append(name)
        
        # 执行更新
        query = f'UPDATE User_Profile SET {", ".join(set_clause)} WHERE name = ?'
        cursor.execute(query, values)
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        logger.error(f"更新用户画像错误: {e}")
        return False


def get_user_profile(name: str) -> Dict[str, Any]:
    """获取用户画像"""
    logger.info(f"获取用户画像: {name}")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM User_Profile WHERE name = ?', (name,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            logger.warning(f"用户不存在: {name}")
            return {}
        
        # 将sqlite3.Row转换为字典
        result = {}
        for key in row.keys():
            result[key] = row[key]
        return result
    except sqlite3.Error as e:
        logger.error(f"获取用户画像错误: {e}")
        return {}