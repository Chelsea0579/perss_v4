"""考试相关模型"""
from typing import Dict, List, Any, Optional


class Question:
    """试题模型"""

    def __init__(
            self,
            number: int,
            question: str,
            answer: str
    ):
        self.number = number
        self.question = question
        self.answer = answer

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "number": self.number,
            "question": self.question,
            "answer": self.answer
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Question':
        """从字典创建试题"""
        return cls(
            number=data.get("number", 0),
            question=data.get("question", ""),
            answer=data.get("answer", "")
        )


class Exam:
    """试卷模型"""

    def __init__(
            self,
            id: int,
            content: str,
            questions: List[Question]
    ):
        self.id = id
        self.content = content
        self.questions = questions

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "exam_id": self.id,
            "content": self.content,
            "questions": [q.to_dict() for q in self.questions]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Exam':
        """从字典创建试卷"""
        questions = []
        if "questions" in data:
            for q_data in data["questions"]:
                questions.append(Question.from_dict(q_data))

        return cls(
            id=data.get("exam_id", 0),
            content=data.get("content", ""),
            questions=questions
        )

    @classmethod
    def from_db_record(cls, record: Dict[str, Any]) -> 'Exam':
        """从数据库记录创建试卷"""
        questions = []
        for i in range(1, 6):  # 假设每套试卷有5道题
            question_key = f"t{i}"
            answer_key = f"a{i}"

            if question_key in record and answer_key in record:
                questions.append(Question(
                    number=i,
                    question=record[question_key],
                    answer=record[answer_key]
                ))

        return cls(
            id=record.get("id", 0),
            content=record.get("content", ""),
            questions=questions
        )


class ExamResult:
    """考试结果模型"""

    def __init__(
            self,
            user_name: str,
            exam_id: int,
            score: int,
            wrong_questions: List[str]
    ):
        self.user_name = user_name
        self.exam_id = exam_id
        self.score = score
        self.wrong_questions = wrong_questions

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "user_name": self.user_name,
            "exam_id": self.exam_id,
            "score": self.score,
            "wrong_questions": self.wrong_questions
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExamResult':
        """从字典创建考试结果"""
        return cls(
            user_name=data.get("user_name", ""),
            exam_id=data.get("exam_id", 0),
            score=data.get("score", 0),
            wrong_questions=data.get("wrong_questions", [])
        )