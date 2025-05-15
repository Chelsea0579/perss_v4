"""用户相关请求/响应模式"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class UserProfileCreate(BaseModel):
    """创建用户画像请求"""
    name: str
    grade: Optional[str] = None
    major: Optional[str] = None
    gender: Optional[str] = None
    cet4_taken: Optional[str] = Field(None, alias="Have you taken the CET-4 exam:")
    cet4_score: Optional[str] = Field(None, alias="CET-4 score")
    cet4_reading_score: Optional[str] = Field(None, alias="CET-4 reading score")
    cet6_taken: Optional[str] = Field(None, alias="Have you taken the CET-6 exam")
    cet6_score: Optional[str] = Field(None, alias="CET-6 score")
    cet6_reading_score: Optional[str] = Field(None, alias="CET-6 reading score")
    other_scores: Optional[str] = Field(None, alias="Other English scores for reference")
    exam_name: Optional[str] = Field(None, alias="Exam name")
    total_score: Optional[str] = Field(None, alias="Total score")
    reading_score: Optional[str] = Field(None, alias="Reading score")

    class Config:
        # 允许通过原始字段名和别名访问字段
        populate_by_name = True
        # 不要尝试验证字段名中的下划线等特殊字符
        validate_assignment = False
        # 允许额外字段
        extra = "ignore"

class UserProfileResponse(BaseModel):
    """用户画像响应"""
    name: str
    grade: Optional[str] = None
    major: Optional[str] = None
    gender: Optional[str] = None
    post_score: Optional[str] = None
    false_id: Optional[str] = None
    post_strategies_score: Optional[str] = None
    after_strategies_score: Optional[str] = None
    after_score: Optional[str] = None

class UserMessage(BaseModel):
    """用户消息"""
    name: str
    message: str

class ChatMessageCreate(BaseModel):
    """创建聊天消息请求"""
    user_name: str
    content: str
    role: str = "user"

class ChatMessageResponse(BaseModel):
    """聊天消息响应"""
    user_name: str
    content: str
    role: str
    timestamp: str