"""考试相关请求/响应模式"""
from pydantic import BaseModel
from typing import List, Optional

class QuestionResponse(BaseModel):
    """试题响应"""
    number: int
    question: str
    answer: Optional[str] = None  # 对用户隐藏答案

class ExamResponse(BaseModel):
    """试卷响应"""
    exam_id: int
    content: str
    questions: List[QuestionResponse]

class ExamResult(BaseModel):
    """考试结果请求"""
    name: str
    exam_id: int
    score: int
    wrong_questions: List[str]

class ExamResultResponse(BaseModel):
    """考试结果响应"""
    success: bool
    message: str