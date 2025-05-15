import logging
import re
from datetime import datetime
from typing import Dict, List, Any, Optional

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def validate_email(email: str) -> bool:
    """验证邮箱格式"""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))


def calculate_exam_score(user_answers: List[str], correct_answers: List[str]) -> Dict[str, Any]:
    """计算考试得分，返回分数和错题ID列表"""
    if len(user_answers) != len(correct_answers):
        logger.warning(f"答案数量不匹配: 用户答案 {len(user_answers)}, 正确答案 {len(correct_answers)}")
        return {"score": 0, "wrong_questions": []}

    score = 0
    question_score = 100 // len(correct_answers)  # 平均分配分数
    wrong_questions = []

    for i, (user_ans, correct_ans) in enumerate(zip(user_answers, correct_answers)):
        # 去除空格和大小写差异
        user_ans = user_ans.strip().lower() if user_ans else ""
        correct_ans = correct_ans.strip().lower() if correct_ans else ""

        if user_ans == correct_ans:
            score += question_score
        else:
            # 记录错题，格式: 试卷ID-题号
            wrong_questions.append(f"{i + 1}")

    return {
        "score": score,
        "wrong_questions": wrong_questions
    }


def calculate_strategy_score(answers: List[int]) -> int:
    """计算阅读策略得分"""
    if not answers:
        return 0

    # 直接求和，每个答案是1-5分
    return sum(answers)


def format_timestamp(timestamp: Optional[datetime] = None) -> str:
    """格式化时间戳"""
    if timestamp is None:
        timestamp = datetime.now()

    return timestamp.strftime("%Y-%m-%d %H:%M:%S")


def format_markdown(text: str) -> str:
    """格式化Markdown文本为HTML"""
    # 简单的Markdown格式化
    # 标题
    text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)

    # 粗体和斜体
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)

    # 列表
    text = re.sub(r'^- (.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)
    text = re.sub(r'(<li>.+</li>\n?)+', r'<ul>\g<0></ul>', text, flags=re.DOTALL)

    # 段落
    text = re.sub(r'^([^<].+)$', r'<p>\1</p>', text, flags=re.MULTILINE)

    return text


def get_reading_level(score: int) -> str:
    """根据阅读分数获取水平描述"""
    if score < 60:
        return "初级"
    elif score < 80:
        return "中级"
    else:
        return "高级"


def get_strategy_level(score: int) -> str:
    """根据策略分数获取水平描述"""
    if score <= 25:
        return "初级"
    elif score <= 50:
        return "中级"
    else:
        return "高级"