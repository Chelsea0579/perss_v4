"""策略相关模型"""
from typing import Dict, List, Any, Optional

class Strategy:
    """阅读策略模型"""
    def __init__(
        self,
        id: int,
        content: str,
        detail: Optional[str] = None
    ):
        self.id = id
        self.content = content
        self.detail = detail

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "content": self.content,
            "detail": self.detail
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Strategy':
        """从字典创建策略"""
        return cls(
            id=data.get("id", 0),
            content=data.get("content", ""),
            detail=data.get("detail")
        )

class StrategyQuestion:
    """策略问卷题目模型"""
    def __init__(
        self,
        id: int,
        content: str,
        options: List[str] = None
    ):
        self.id = id
        self.content = content
        self.options = options or []

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "content": self.content,
            "options": self.options
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StrategyQuestion':
        """从字典创建策略问卷题目"""
        options = data.get("options", [])
        if not options and data.get("content"):
            options = [
                "1.I have never heard of this strategy before.",
                "2.I have heard of this strategy,but I don't know what it means.",
                "3.I have heard of this strategy,and I think I know what it means.",
                "4.I know this strategy,and I can explain how and when to use it.",
                "5.I know this strategy quite well,and I often use it when Iread."
            ]

        return cls(
            id=data.get("id", 0),
            content=data.get("content", ""),
            options=options
        )

    @classmethod
    def from_db_record(cls, record: Dict[str, Any]) -> 'StrategyQuestion':
        """从数据库记录创建策略问卷题目"""
        options = []
        for i in range(1, 6):
            option_key = f"{i}.I have never heard of this strategy before." if i == 1 else \
                         f"{i}.I have heard of this strategy,but I don't know what it means." if i == 2 else \
                         f"{i}.I have heard of this strategy,and I think I know what it means." if i == 3 else \
                         f"{i}.I know this strategy,and I can explain how and when to use it." if i == 4 else \
                         f"{i}.I know this strategy quite well,and I often use it when Iread."

            if option_key in record:
                options.append(option_key)

        return cls(
            id=record.get("id", 0),
            content=record.get("content", ""),
            options=options
        )

class StrategyResult:
    """策略问卷结果模型"""
    def __init__(
        self,
        user_name: str,
        score: int,
        is_pre_test: bool = True
    ):
        self.user_name = user_name
        self.score = score
        self.is_pre_test = is_pre_test

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "user_name": self.user_name,
            "score": self.score,
            "is_pre_test": self.is_pre_test
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StrategyResult':
        """从字典创建策略问卷结果"""
        return cls(
            user_name=data.get("user_name", ""),
            score=data.get("score", 0),
            is_pre_test=data.get("is_pre_test", True)
        )

    def get_level(self) -> str:
        """获取策略水平"""
        if self.score <= 25:
            return "初级"
        elif self.score <= 50:
            return "中级"
        else:
            return "高级"