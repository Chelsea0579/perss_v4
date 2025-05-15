"""AI服务模块，用于与Deepseek API交互"""
import logging
import json
import httpx
from typing import Dict, Any, List, Optional
import asyncio

from app.config import DEEPSEEK_API_KEY, DEEPSEEK_API_URL

# 配置日志
logger = logging.getLogger(__name__)

# 请求头
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
}


async def call_deepseek_api(messages: List[Dict[str, str]]) -> Dict[str, Any]:
    """调用DeepseekAPI"""
    try:
        payload = {
            "model": "deepseek-chat",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        async with httpx.AsyncClient(timeout=120.0) as client: # 增加超时到120秒
            logger.info(f"向 DeepSeek API 发送请求: {DEEPSEEK_API_URL}，模型: {payload['model']}")
            try:
                response = await client.post(
                    DEEPSEEK_API_URL,
                    headers=HEADERS,
                    json=payload
                )
                logger.info(f"DeepSeek API 响应状态码: {response.status_code}")
                
                # 尝试解析 JSON，无论状态码如何，以便记录内容
                try:
                    result = response.json()
                    logger.info(f"DeepSeek API 响应内容 (部分): {str(result)[:500]}") # 只记录前500字符
                except json.JSONDecodeError as json_err:
                    logger.error(f"DeepSeek API 响应 JSON 解析失败: {json_err}")
                    logger.error(f"DeepSeek API 原始响应文本 (部分): {response.text[:500]}")
                    return {
                        "success": False,
                        "error": f"API响应JSON解析失败: {json_err}",
                        "status_code": response.status_code,
                        "raw_response": response.text[:500] 
                    }

                response.raise_for_status() # 如果状态码是 4xx 或 5xx，则抛出 HTTPError
                
                if "choices" in result and len(result["choices"]) > 0 and \
                "message" in result["choices"][0] and "content" in result["choices"][0]["message"]:
                    return {
                        "success": True,
                        "content": result["choices"][0]["message"]["content"]
                    }
                else:
                    logger.error(f"DeepSeek API 响应格式不符合预期: {result}")
                    return {
                        "success": False,
                        "error": "API响应格式不符合预期",
                        "details": result
                    }
            except httpx.TimeoutException as e:
                logger.error(f"DeepSeek API 请求超时: {e}")
                return {
                    "success": False,
                    "error": f"API请求超时: {e}",
                    "fallback_content": "很抱歉，AI服务暂时无法响应，请稍后再试。"
                }
    except httpx.HTTPStatusError as e:
        logger.error(f"DeepSeek API 请求失败 (HTTPStatusError): {e}")
        logger.error(f"请求详情: {e.request}")
        if e.response:
            logger.error(f"响应状态码: {e.response.status_code}")
            logger.error(f"响应内容 (部分): {e.response.text[:500]}")
        return {
            "success": False, 
            "error": f"API请求失败: {e}", 
            "status_code": e.response.status_code if e.response else None,
            "response_text": e.response.text[:500] if e.response else None,
            "fallback_content": "很抱歉，AI服务暂时返回了错误，请稍后再试。"
        }
    except httpx.RequestError as e:
        logger.error(f"DeepSeek API 请求发生错误 (RequestError): {e}")
        logger.error(f"请求详情: {e.request}")
        return {
            "success": False, 
            "error": f"API请求发生错误: {e}",
            "fallback_content": "很抱歉，与AI服务的连接出现问题，请稍后再试。"
        }
    except Exception as e:
        logger.error(f"调用 DeepSeek API 时发生未知错误: {e}", exc_info=True) # exc_info=True 会记录堆栈跟踪
        return {
            "success": False, 
            "error": f"调用API时发生未知错误: {type(e).__name__} - {e}",
            "fallback_content": "很抱歉，AI服务出现了未知错误，请稍后再试。"
        }


async def analyze_user_profile(user_profile: Dict[str, Any]) -> Dict[str, Any]:
    """分析用户画像"""
    logger.info(f"分析用户画像: {user_profile.get('name', '未知用户')}")
    
    # 构建系统提示和用户消息
    system_prompt = """你是一个专业的英语阅读教育顾问。请根据学生的个人信息和测试成绩，分析他们的英语阅读能力水平，识别主要困难，并提供针对性的学习策略建议。你的分析应该包括：当前水平评估、主要困难、策略建议和学习计划建议。使用markdown格式，确保分析客观、专业且有建设性。"""
    
    # 提取关键信息
    post_score = user_profile.get("post_score", "N/A")
    post_strategies_score = user_profile.get("post_strategies_score", "N/A")
    false_ids = user_profile.get("false_id", "")
    
    # 构建用户消息
    user_message = f"""
    学生信息：
    - 姓名: {user_profile.get('name', 'N/A')}
    - 年级: {user_profile.get('grade', 'N/A')}
    - 专业: {user_profile.get('major', 'N/A')}
    - 性别: {user_profile.get('gender', 'N/A')}
    - 英语成绩:
      - 四级: {user_profile.get('CET-4 score', 'N/A')} (阅读: {user_profile.get('CET-4 reading score', 'N/A')})
      - 六级: {user_profile.get('CET-6 score', 'N/A')} (阅读: {user_profile.get('CET-6 reading score', 'N/A')})
      - 其他: {user_profile.get('Other English scores for reference', 'N/A')}
    - 前测成绩: {post_score}
    - 阅读策略前测分数: {post_strategies_score}
    - 错题ID: {false_ids}
    
    请根据以上信息分析学生的英语阅读能力，识别他的主要困难，并提供针对性的学习策略建议。
    """
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]
    
    # 调用API
    response = await call_deepseek_api(messages)
    
    if response["success"]:
        return {
            "success": True,
            "analysis": response["content"]
        }
    else:
        logger.error(f"分析用户画像失败: {response.get('error', '未知错误')}")
        return {
            "success": False,
            "analysis": "抱歉，分析过程中出现错误，请稍后再试。"
        }


async def analyze_wrong_answers(user_profile: Dict[str, Any], exam_ids: list) -> Dict[str, Any]:
    """分析错题"""
    logger.info(f"分析错题: {user_profile.get('name', '未知用户')}, 试卷ID: {exam_ids}")
    
    # 获取错题列表
    false_ids = user_profile.get("false_id", "")
    if not false_ids:
        logger.warning(f"用户没有错题记录: {user_profile.get('name', '未知用户')}")
        return {
            "success": True,
            "analysis": "没有发现错题记录，无需分析。"
        }
    
    logger.info(f"原始错题ID: {false_ids}")
    
    # 解析错题ID格式，支持多种格式
    # 1. "1:2,1:4" 表示试卷1的第2题和第4题错误
    # 2. "1-2,1-3" 表示试卷1的第2题和第3题错误
    # 3. "1,2,3" 表示第1题、第2题和第3题错误(默认为试卷1)
    wrong_answers = []
    try:
        for item in false_ids.split(","):
            item = item.strip()
            if ":" in item:  # 格式1
                exam_id, question_num = item.split(":")
                wrong_answers.append({"exam_id": int(exam_id), "question_num": int(question_num)})
            elif "-" in item:  # 格式2
                exam_id, question_num = item.split("-")
                wrong_answers.append({"exam_id": int(exam_id), "question_num": int(question_num)})
            else:  # 格式3
                try:
                    question_num = int(item)
                    # 默认使用试卷1
                    wrong_answers.append({"exam_id": exam_ids[0] if exam_ids else 1, "question_num": question_num})
                except ValueError:
                    logger.warning(f"无法解析错题ID: {item}")
    except Exception as e:
        logger.error(f"解析错题ID失败: {e}")
    
    if not wrong_answers:
        logger.warning(f"无法解析的错题格式，原始数据: {false_ids}")
        return {
            "success": True,
            "analysis": f"""
# 错题分析

## 解析结果

无法解析您的错题记录格式。原始数据为: {false_ids}

## 一般阅读建议

尽管无法针对您的具体错题提供分析，但以下是提高英语阅读能力的一般建议：

1. **预览阅读**：阅读前先浏览标题、首尾段和图表，建立框架
2. **主动提问**：阅读时提出问题，增强记忆和理解
3. **上下文推断**：遇到生词时利用上下文线索进行推断
4. **精读与泛读结合**：针对不同阅读目的选择适当的阅读方式
5. **定期复习**：建立错题本，定期回顾和反思

建议您下次做题时保存具体的错题信息，以便系统提供更有针对性的分析。
"""
        }
    
    logger.info(f"解析后的错题: {wrong_answers}")
    
    # 构建系统提示和用户消息
    system_prompt = """你是一个专业的英语阅读教育专家。请分析学生的阅读理解错题，找出错误原因，并提供针对性的改进建议。你的分析应包括：题目考察的能力、错误可能的原因、以及提高这类题目答题能力的策略建议。使用markdown格式，确保分析专业、清晰且有针对性。"""
    
    # 构建错题信息
    wrong_questions_info = []
    from app.database import get_exam_by_id
    
    for wrong_answer in wrong_answers:
        exam_id = wrong_answer["exam_id"]
        question_num = wrong_answer["question_num"]
        
        try:
            exam = get_exam_by_id(exam_id)
            if not exam:
                logger.warning(f"找不到试卷: {exam_id}")
                continue
                
            # 题目和答案的键名格式为"t1"和"a1"
            question_key = f"t{question_num}"
            answer_key = f"a{question_num}"
            
            if question_key in exam and answer_key in exam:
                wrong_questions_info.append({
                    "exam_id": exam_id,
                    "question_num": question_num,
                    "content": exam.get("content", ""),
                    "question": exam.get(question_key, ""),
                    "answer": exam.get(answer_key, "")
                })
            else:
                logger.warning(f"找不到题目或答案: 试卷{exam_id}，题号{question_num}，键{question_key}/{answer_key}")
        except Exception as e:
            logger.error(f"获取试卷错题信息失败: {e}", exc_info=True)
    
    if not wrong_questions_info:
        logger.warning("无法获取任何错题信息")
        return {
            "success": True,
            "analysis": f"""
# 错题分析

尽管系统识别到您有错题记录（{false_ids}），但无法获取这些题目的详细信息。这可能是因为：

1. 题目编号与题库不匹配
2. 试卷ID不存在或格式异常

## 一般阅读建议

以下是提高英语阅读能力的一般建议：

1. **精准定位信息**：训练快速查找关键词和主题句的能力
2. **推理能力提升**：练习根据文本信息进行合理推断
3. **句法分析**：学习理解复杂句式结构，特别是长句
4. **词汇理解策略**：通过上下文推测词义，而不仅仅依赖单词记忆

建议您记录具体的错题内容，以便获得更有针对性的分析和建议。
"""
        }
    
    # 构建用户消息
    user_message = f"""
    学生信息：
    - 姓名: {user_profile.get('name', 'N/A')}
    - 年级: {user_profile.get('grade', 'N/A')}
    - 专业: {user_profile.get('major', 'N/A')}
    - 英语成绩:
      - 四级: {user_profile.get('CET-4 score', 'N/A')} (阅读: {user_profile.get('CET-4 reading score', 'N/A')})
      - 六级: {user_profile.get('CET-6 score', 'N/A')} (阅读: {user_profile.get('CET-6 reading score', 'N/A')})
    
    错题信息:
    """
    
    for i, info in enumerate(wrong_questions_info, 1):
        user_message += f"""
    错题{i}:
    - 试卷ID: {info['exam_id']}
    - 题号: {info['question_num']}
    - 原文: {info['content'][:500]}...（截取部分内容）
    - 题目: {info['question']}
    - 正确答案: {info['answer']}
    """
    
    user_message += """
    请分析每道错题，找出可能的错误原因，并提供针对性的改进建议。
    """
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]
    
    # 调用API
    try:
        logger.info("调用DeepSeek API分析错题")
        response = await call_deepseek_api(messages)
        
        if response["success"]:
            return {
                "success": True,
                "analysis": response["content"]
            }
        else:
            logger.error(f"分析错题失败: {response.get('error', '未知错误')}")
            return {
                "success": True,  # 返回true以避免前端错误，但提供说明信息
                "analysis": """
# 错题分析

很抱歉，AI分析服务暂时无法处理您的错题。

## 建议采取的措施

1. **自我分析**：回顾您做错的题目，思考错误原因
2. **检查理解**：重新阅读相关文章，确保您理解了文章的主旨和细节
3. **策略运用**：尝试应用不同的阅读策略，如预览、提问、推断等
4. **稍后重试**：稍后再次尝试获取AI分析

如需更多帮助，可以使用系统的聊天功能与AI助手交流，讨论您在阅读理解中遇到的具体困难。
"""
            }
    except Exception as e:
        logger.error(f"调用AI服务分析错题时发生异常: {e}", exc_info=True)
        return {
            "success": True,  # 返回true以避免前端错误，但提供说明信息
            "analysis": """
# 错题分析

很抱歉，在分析您的错题时遇到了技术问题。

## 建议采取的措施

1. **自我分析**：回顾您做错的题目，思考错误原因
2. **检查理解**：重新阅读相关文章，确保您理解了文章的主旨和细节
3. **策略运用**：尝试应用不同的阅读策略，如预览、提问、推断等
4. **稍后重试**：稍后再次尝试获取AI分析

如需更多帮助，可以使用系统的聊天功能与AI助手交流，讨论您在阅读理解中遇到的具体困难。
"""
        }


async def suggest_reading_strategies(user_profile: Dict[str, Any]) -> Dict[str, Any]:
    """推荐阅读策略"""
    logger.info(f"推荐阅读策略: {user_profile.get('name', '未知用户')}")
    
    # 获取用户的阅读策略评分
    strategies_score = user_profile.get("post_strategies_score", "0")
    try:
        score = int(strategies_score)
    except ValueError:
        score = 0
    
    # 构建系统提示和用户消息
    system_prompt = """你是一个专业的英语阅读教育专家。请根据学生的英语水平和阅读策略评分，推荐3-5个最适合该学生的阅读策略，帮助他们提高阅读理解能力。对于每个策略，详细解释其定义、应用方法和练习建议。使用markdown格式，确保建议专业、实用且具体。"""
    
    # 解析用户阅读策略水平
    strategy_level = "初级"
    if score > 60:
        strategy_level = "高级"
    elif score > 45:
        strategy_level = "中级"
    
    # 构建用户消息
    user_message = f"""
    学生信息：
    - 姓名: {user_profile.get('name', 'N/A')}
    - 年级: {user_profile.get('grade', 'N/A')}
    - 专业: {user_profile.get('major', 'N/A')}
    - 英语成绩:
      - 四级: {user_profile.get('CET-4 score', 'N/A')}
      - 六级: {user_profile.get('CET-6 score', 'N/A')}
    - 阅读策略评分: {strategies_score}/75 (水平: {strategy_level})
    
    请根据学生的信息，推荐3-5个最适合该学生的阅读策略，帮助提高英语阅读理解能力。对于每个策略，详细解释其定义、应用方法和具体的练习建议。
    """
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]
    
    # 调用API
    response = await call_deepseek_api(messages)
    
    if response["success"]:
        return {
            "success": True,
            "suggestions": response["content"]
        }
    else:
        logger.error(f"推荐阅读策略失败: {response.get('error', '未知错误')}")
        return {
            "success": False,
            "suggestions": "抱歉，推荐过程中出现错误，请稍后再试。"
        }


async def generate_final_summary(user_profile: Dict[str, Any]) -> Dict[str, Any]:
    """生成学习总结"""
    logger.info(f"生成学习总结: {user_profile.get('name', '未知用户')}")
    
    # 获取用户的前后测成绩
    post_score = user_profile.get("post_score", "0")
    post_strategies_score = user_profile.get("post_strategies_score", "0")
    after_score = user_profile.get("after_score", "0")
    after_strategies_score = user_profile.get("after_strategies_score", "0")
    
    try:
        post_score_num = float(post_score)
        post_strategies_score_num = float(post_strategies_score)
        after_score_num = float(after_score)
        after_strategies_score_num = float(after_strategies_score)
        
        score_improvement = (after_score_num - post_score_num) / post_score_num * 100 if post_score_num > 0 else 0
        strategies_improvement = (after_strategies_score_num - post_strategies_score_num) / post_strategies_score_num * 100 if post_strategies_score_num > 0 else 0
    except ValueError:
        score_improvement = 0
        strategies_improvement = 0
    
    # 构建系统提示和用户消息
    system_prompt = """你是一个专业的英语阅读教育专家。请根据学生的前后测成绩和阅读策略评分，生成一份全面的学习总结报告。报告应包括：成就与进步、前后测对比分析、当前水平评估、策略建议和未来学习计划。使用markdown格式，确保报告专业、积极且有针对性。"""
    
    # 构建用户消息
    user_message = f"""
    学生信息：
    - 姓名: {user_profile.get('name', 'N/A')}
    - 年级: {user_profile.get('grade', 'N/A')}
    - 专业: {user_profile.get('major', 'N/A')}
    - 性别: {user_profile.get('gender', 'N/A')}
    
    测试成绩:
    - 前测成绩: {post_score}/100
    - 后测成绩: {after_score}/100
    - 成绩提升: {score_improvement:.1f}%
    
    阅读策略评分:
    - 前测评分: {post_strategies_score}/75
    - 后测评分: {after_strategies_score}/75
    - 评分提升: {strategies_improvement:.1f}%
    
    请根据以上信息生成一份全面的学习总结报告，包括成就与进步、前后测对比分析、当前水平评估、策略建议和未来学习计划。
    """
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]
    
    # 调用API
    response = await call_deepseek_api(messages)
    
    if response["success"]:
        return {
            "success": True,
            "summary": response["content"]
        }
    else:
        logger.error(f"生成学习总结失败: {response.get('error', '未知错误')}")
        return {
            "success": False,
            "summary": "抱歉，生成总结过程中出现错误，请稍后再试。"
        }


async def process_user_message(user_profile: Dict[str, Any], message: str) -> Dict[str, Any]:
    """处理用户消息"""
    logger.info(f"处理用户消息: {user_profile.get('name', '未知用户')}, 消息: {message}")
    
    # 构建系统提示和历史消息
    system_prompt = """你是一个专业的英语阅读教育助手，专注于帮助学生提高英语阅读能力。请根据学生的消息，提供专业、有针对性的回答。你的回答应该简洁明了，具有实用性和教育价值。如果学生提问不清晰，请礼貌地引导他们提出更具体的问题。"""
    
    # 构建用户背景信息
    user_background = f"""
    学生信息：
    - 姓名: {user_profile.get('name', 'N/A')}
    - 年级: {user_profile.get('grade', 'N/A')}
    - 专业: {user_profile.get('major', 'N/A')}
    - 英语水平: 四级分数{user_profile.get('CET-4 score', 'N/A')}, 六级分数{user_profile.get('CET-6 score', 'N/A')}
    - 前测成绩: {user_profile.get('post_score', 'N/A')}/100
    - 阅读策略评分: {user_profile.get('post_strategies_score', 'N/A')}/75
    """
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"{user_background}\n\n学生消息: {message}"}
    ]
    
    # 调用API
    response = await call_deepseek_api(messages)
    
    if response["success"]:
        return {
            "success": True,
            "response": response["content"]
        }
    else:
        logger.error(f"处理用户消息失败: {response.get('error', '未知错误')}")
        return {
            "success": False,
            "response": "抱歉，处理消息过程中出现错误，请稍后再试。"
        }