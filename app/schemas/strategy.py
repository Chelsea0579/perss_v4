"""策略相关请求/响应模式"""
from pydantic import BaseModel, Field
from typing import List, Optional, Union, Annotated
import json
from pydantic.functional_validators import AfterValidator

def convert_to_bool(v):
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        return v.lower() in ('true', 't', '1', 'yes', 'y')
    if isinstance(v, int):
        return bool(v)
    return bool(v)

class StrategyItem(BaseModel):
    """策略项响应"""
    id: int
    content: str
    detail: Optional[str] = None

class StrategyOptionItem(BaseModel):
    """策略选项响应"""
    value: int
    label: str

class StrategyQuestion(BaseModel):
    """策略问题响应"""
    id: int
    content: str
    options: List[StrategyOptionItem]

class StrategyResult(BaseModel):
    """策略结果请求"""
    name: str
    score: int
    is_pre_test: Annotated[bool, AfterValidator(convert_to_bool)] = True

class StrategyResultResponse(BaseModel):
    """策略结果响应"""
    success: bool
    message: str

class StrategySuggestion(BaseModel):
    """策略建议响应"""
    strategy_id: int
    content: str
    detail: str
    explanation: str
    examples: List[str]

class StrategySuggestionResponse(BaseModel):
    """策略建议列表响应"""
    success: bool
    suggestions: List[StrategySuggestion]