"""用户相关模型"""
from typing import Optional, Dict, Any, List
from datetime import datetime


class UserProfile:
    """用户画像模型"""

    def __init__(
            self,
            name: str,
            grade: Optional[str] = None,
            major: Optional[str] = None,
            gender: Optional[str] = None,
            cet4_taken: Optional[str] = None,
            cet4_score: Optional[str] = None,
            cet4_reading_score: Optional[str] = None,
            cet6_taken: Optional[str] = None,
            cet6_score: Optional[str] = None,
            cet6_reading_score: Optional[str] = None,
            other_scores: Optional[str] = None,
            exam_name: Optional[str] = None,
            total_score: Optional[str] = None,
            reading_score: Optional[str] = None,
            post_score: Optional[str] = None,
            false_id: Optional[str] = None,
            post_strategies_score: Optional[str] = None,
            after_strategies_score: Optional[str] = None,
            after_score: Optional[str] = None,
    ):
        self.name = name
        self.grade = grade
        self.major = major
        self.gender = gender
        self.cet4_taken = cet4_taken
        self.cet4_score = cet4_score
        self.cet4_reading_score = cet4_reading_score
        self.cet6_taken = cet6_taken
        self.cet6_score = cet6_score
        self.cet6_reading_score = cet6_reading_score
        self.other_scores = other_scores
        self.exam_name = exam_name
        self.total_score = total_score
        self.reading_score = reading_score
        self.post_score = post_score
        self.false_id = false_id
        self.post_strategies_score = post_strategies_score
        self.after_strategies_score = after_strategies_score
        self.after_score = after_score
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "grade": self.grade,
            "major": self.major,
            "gender": self.gender,
            "Have you taken the CET-4 exam:": self.cet4_taken,
            "CET-4 score": self.cet4_score,
            "CET-4 reading score": self.cet4_reading_score,
            "Have you taken the CET-6 exam": self.cet6_taken,
            "CET-6 score": self.cet6_score,
            "CET-6 reading score": self.cet6_reading_score,
            "Other English scores for reference": self.other_scores,
            "Exam name": self.exam_name,
            "Total score": self.total_score,
            "Reading score": self.reading_score,
            "post_score": self.post_score,
            "false_id": self.false_id,
            "post_strategies_score": self.post_strategies_score,
            "after_strategies_score": self.after_strategies_score,
            "after_score": self.after_score
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserProfile':
        """从字典创建用户画像"""
        return cls(
            name=data.get("name"),
            grade=data.get("grade"),
            major=data.get("major"),
            gender=data.get("gender"),
            cet4_taken=data.get("Have you taken the CET-4 exam:"),
            cet4_score=data.get("CET-4 score"),
            cet4_reading_score=data.get("CET-4 reading score"),
            cet6_taken=data.get("Have you taken the CET-6 exam"),
            cet6_score=data.get("CET-6 score"),
            cet6_reading_score=data.get("CET-6 reading score"),
            other_scores=data.get("Other English scores for reference"),
            exam_name=data.get("Exam name"),
            total_score=data.get("Total score"),
            reading_score=data.get("Reading score"),
            post_score=data.get("post_score"),
            false_id=data.get("false_id"),
            post_strategies_score=data.get("post_strategies_score"),
            after_strategies_score=data.get("after_strategies_score"),
            after_score=data.get("after_score")
        )

    def get_reading_level(self) -> str:
        """获取用户阅读水平"""
        try:
            # 使用后测分数，如果没有则使用前测分数
            score = int(self.after_score) if self.after_score else int(self.post_score) if self.post_score else 0

            if score < 60:
                return "初级"
            elif score < 80:
                return "中级"
            else:
                return "高级"
        except (ValueError, TypeError):
            return "未知"

    def get_strategy_level(self) -> str:
        """获取用户策略水平"""
        try:
            # 使用后测分数，如果没有则使用前测分数
            score = int(self.after_strategies_score) if self.after_strategies_score else int(
                self.post_strategies_score) if self.post_strategies_score else 0

            if score <= 25:
                return "初级"
            elif score <= 50:
                return "中级"
            else:
                return "高级"
        except (ValueError, TypeError):
            return "未知"

    def get_improvement(self) -> Dict[str, float]:
        """计算提高百分比"""
        reading_improvement = 0
        strategy_improvement = 0

        try:
            pre_score = int(self.post_score) if self.post_score else 0
            post_score = int(self.after_score) if self.after_score else 0

            if pre_score > 0:
                reading_improvement = ((post_score - pre_score) / pre_score) * 100
        except (ValueError, TypeError):
            pass

        try:
            pre_strategy = int(self.post_strategies_score) if self.post_strategies_score else 0
            post_strategy = int(self.after_strategies_score) if self.after_strategies_score else 0

            if pre_strategy > 0:
                strategy_improvement = ((post_strategy - pre_strategy) / pre_strategy) * 100
        except (ValueError, TypeError):
            pass

        return {
            "reading": reading_improvement,
            "strategy": strategy_improvement
        }


class ChatMessage:
    """聊天消息模型"""

    def __init__(
            self,
            user_name: str,
            content: str,
            role: str = "user",
            timestamp: Optional[datetime] = None
    ):
        self.user_name = user_name
        self.content = content
        self.role = role  # "user" 或 "assistant"
        self.timestamp = timestamp or datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "user_name": self.user_name,
            "content": self.content,
            "role": self.role,
            "timestamp": self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatMessage':
        """从字典创建聊天消息"""
        timestamp = None
        if "timestamp" in data:
            try:
                timestamp = datetime.fromisoformat(data["timestamp"])
            except (ValueError, TypeError):
                pass

        return cls(
            user_name=data.get("user_name", ""),
            content=data.get("content", ""),
            role=data.get("role", "user"),
            timestamp=timestamp
        )