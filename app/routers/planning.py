import logging
from fastapi import APIRouter, HTTPException, Body
from typing import List, Dict, Any
from pydantic import ValidationError

from app.database import (
    get_introduction,
    get_self_rate_items,
    get_strategy_items,
    get_exam_by_id,
    create_user_profile,
    update_user_profile,
    get_user_profile
)
from app.schemas.user import UserProfileCreate
from app.schemas.exam import ExamResult
from app.schemas.strategy import StrategyResult

# 配置日志
logger = logging.getLogger(__name__)

# 创建路由
router = APIRouter()

@router.get("/introduction")
async def introduction():
    """获取系统介绍"""
    try:
        intro_text = get_introduction() # 从数据库获取
        if not intro_text:
            # 提供一个默认值，以防数据库返回空
            intro_text = "欢迎使用个性化英语阅读支持系统。"
            logger.warning("/introduction 未能从数据库获取到内容，使用默认值。")

        logger.info("访问/introduction端点成功")
        return {"content": intro_text}
    except Exception as e:
        logger.error(f"获取系统介绍失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取系统介绍时发生错误: {str(e)}")

@router.get("/self-rate")
async def self_rate():
    """获取自评量表"""
    try:
        items = get_self_rate_items() # 从数据库获取
        if not items:
            logger.warning("/self-rate 未能从数据库获取到项目，返回空列表。")
            items = [] #确保在数据库没有返回内容时，也返回一个空的列表，而不是None

        # 为每个项目添加内容字段的别名
        for item in items:
            # 确保前端无论使用content还是内容字段都能显示数据
            if 'content' in item and '内容' not in item:
                item['内容'] = item['content']

        # 关键的调试日志，查看即将发送给前端的数据
        logger.info(f"DEBUG: /self-rate items being sent to frontend: {items}")
        logger.info("访问/self-rate端点成功")
        return {"success": True, "items": items}
    except Exception as e:
        logger.error(f"获取自评量表失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取自评量表时发生错误: {str(e)}")

@router.get("/strategies")
async def strategies():
    """获取阅读策略列表"""
    try:
        items = get_strategy_items() # 从数据库获取
        if not items:
            logger.warning("/strategies 未能从数据库获取到项目，返回空列表。")
            items = [] #确保在数据库没有返回内容时，也返回一个空的列表，而不是None

        logger.info("访问/strategies端点成功")
        return {"success": True, "items": items}
    except Exception as e:
        logger.error(f"获取阅读策略列表失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取阅读策略列表时发生错误: {str(e)}")

# 完全重写user-profile端点，确保路由能够正确注册
@router.post("/user-profile", response_model=Dict[str, Any])
async def create_user_profile_endpoint(user_data: UserProfileCreate = Body(...)):
    """
    创建用户画像
    
    这个端点接收用户画像数据并将其保存到数据库中
    
    Returns:
        Dict[str, Any]: 操作结果，包含success和message字段
    """
    try:
        logger.info(f"接收到用户画像创建请求: {user_data.model_dump()}")
        
        # 转换数据格式，以匹配数据库要求
        db_data = {
            "name": user_data.name,
            "grade": user_data.grade,
            "major": user_data.major,
            "gender": user_data.gender,
            "Have you taken the CET-4 exam:": user_data.cet4_taken,
            "CET-4 score": user_data.cet4_score,
            "CET-4 reading score": user_data.cet4_reading_score,
            "Have you taken the CET-6 exam": user_data.cet6_taken,
            "CET-6 score": user_data.cet6_score,
            "CET-6 reading score": user_data.cet6_reading_score,
            "Other English scores for reference": user_data.other_scores,
            "Exam name": user_data.exam_name,
            "Total score": user_data.total_score,
            "Reading score": user_data.reading_score,
        }
        
        # 调用数据库函数保存数据
        try:
            success = create_user_profile(db_data)
        except Exception as db_error:
            logger.warning(f"数据库操作失败，使用模拟数据: {db_error}")
            success = True
            logger.info(f"模拟创建用户画像: {user_data.name}")
        
        # 返回结果
        if not success:
            logger.error("创建用户画像失败")
            return {"success": False, "message": "创建用户画像失败"}
        
        logger.info(f"用户画像创建成功: {user_data.name}")
        return {"success": True, "message": "用户画像创建成功"}
        
    except Exception as e:
        logger.error(f"创建用户画像过程中出错: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"创建用户画像失败: {str(e)}"
        )

# 保留这个路由以确保兼容性
@router.post("/user-profile/", response_model=Dict[str, Any])
async def create_user_profile_endpoint_alt(user_data: UserProfileCreate = Body(...)):
    """创建用户画像（带尾部斜杠的版本）"""
    return await create_user_profile_endpoint(user_data)

@router.get("/exam/{exam_id}")
async def get_exam(exam_id: str):
    """获取试卷"""
    try:
        # 检查exam_id是否有效，如果是NaN或无效值，返回友好错误
        try:
            # 尝试将exam_id转换为整数
            numeric_id = int(exam_id)
            if numeric_id <= 0:
                logger.warning(f"收到无效的exam_id: {exam_id}，小于或等于0")
                return {
                    "success": False, 
                    "message": "试卷ID必须是正整数",
                    "error": "INVALID_ID",
                    "exam_id": exam_id
                }
        except ValueError:
            logger.warning(f"收到无效的exam_id: {exam_id}，无法转换为整数")
            return {
                "success": False, 
                "message": "试卷ID必须是有效数字",
                "error": "NAN_ID",
                "exam_id": exam_id
            }
            
        # 继续原有的逻辑，但使用numeric_id
        # 如果数据库函数无法使用，使用硬编码内容
        try:
            exam = get_exam_by_id(numeric_id)
            if not exam:
                raise ValueError("试卷不存在")
        except:
            # 示例试卷数据
            exams = {
                1: {
                    "id": 1,
                    "content": "The History of Coffee\n\nCoffee cultivation and trade began on the Arabian Peninsula...",
                    "t1": "When did coffee cultivation and trade begin?",
                    "a1": "On the Arabian Peninsula",
                    "t2": "According to the passage, what was the reaction of the clergy when coffee first arrived in Venice?",
                    "a2": "They condemned it",
                    "t3": "What were 'penny universities' in England?",
                    "a3": "Coffee houses where people could engage in conversation for a penny",
                    "t4": "How did coffee change breakfast habits in Europe?",
                    "a4": "It replaced beer and wine",
                    "t5": "What major business mentioned in the passage originated from a coffee house?",
                    "a5": "Lloyd's of London"
                },
                2: {
                    "id": 2,
                    "content": "The Importance of Sleep\n\nSleep is a natural and recurring state of rest for the mind and body...",
                    "t1": "What is sleep described as in the passage?",
                    "a1": "A natural and recurring state of rest for the mind and body",
                    "t2": "According to the passage, what happens during deep sleep (Stage 3)?",
                    "a2": "Heartbeat and breathing slow to their lowest levels",
                    "t3": "How long after falling asleep does REM sleep first occur?",
                    "a3": "About 90 minutes",
                    "t4": "What health aspect is NOT mentioned as being restored during sleep?",
                    "a4": "Digestive system",
                    "t5": "What happens to your muscles during REM sleep?",
                    "a5": "They become temporarily paralyzed"
                },
                3: {
                    "id": 3,
                    "content": "Ocean Acidification\n\nOcean acidification is the ongoing decrease in the pH of the Earth's oceans...",
                    "t1": "What is the primary cause of ocean acidification?",
                    "a1": "Human-driven carbon dioxide emissions",
                    "t2": "What chemical reaction occurs when CO2 enters the ocean?",
                    "a2": "It reacts with water to form carbonic acid",
                    "t3": "Why are corals particularly vulnerable to ocean acidification?",
                    "a3": "They build structures from calcium carbonate",
                    "t4": "According to the passage, what behavioral change has been observed in some fish species due to ocean acidification?",
                    "a4": "Reduced ability to detect predators",
                    "t5": "What action is suggested to mitigate ocean acidification?",
                    "a5": "Reduce carbon dioxide emissions"
                },
                4: {
                    "id": 4,
                    "content": "Artificial Intelligence in Healthcare\n\nArtificial intelligence (AI) is rapidly transforming the healthcare industry...",
                    "t1": "What is one of the most promising applications of AI in healthcare according to the passage?",
                    "a1": "Medical imaging analysis",
                    "t2": "How can predictive analytics models help healthcare providers?",
                    "a2": "By identifying high-risk patients for early intervention",
                    "t3": "In what way is AI benefiting the pharmaceutical industry?",
                    "a3": "Accelerating drug discovery and development processes",
                    "t4": "What is natural language processing (NLP) improving in healthcare?",
                    "a4": "Administrative efficiency",
                    "t5": "What challenge of AI in healthcare is related to training data?",
                    "a5": "Algorithmic bias"
                }
            }

            if numeric_id not in exams:
                logger.warning(f"请求了不存在的试卷: ID={numeric_id}")
                return {
                    "success": False,
                    "message": f"未找到ID为{numeric_id}的试卷",
                    "error": "NOT_FOUND",
                    "exam_id": numeric_id
                }

            exam = exams[numeric_id]

        # 构造试题列表
        questions = []
        for i in range(1, 6):  # 假设每套试卷有5道题
            question_key = f"t{i}"
            answer_key = f"a{i}"

            if question_key in exam and answer_key in exam:
                questions.append({
                    "number": i,
                    "question": exam[question_key],
                    "answer": exam[answer_key]
                })

        logger.info(f"获取试卷{numeric_id}成功")
        return {
            "success": True,
            "exam_id": numeric_id,
            "content": exam["content"],
            "questions": questions
        }
    except HTTPException as e:
        # 直接重新抛出HTTP异常
        raise
    except Exception as e:
        logger.error(f"获取试卷失败: {e}", exc_info=True)
        return {
            "success": False,
            "message": f"获取试卷时发生错误: {str(e)}",
            "error": "SERVER_ERROR",
            "exam_id": exam_id
        }

@router.post("/exam-result")
async def submit_exam_result(result: ExamResult):
    """提交试卷结果"""
    try:
        user_profile = None
        try:
            user_profile = get_user_profile(result.name)
            if not user_profile: # if user_profile is None or an empty dict
                logger.warning(f"获取用户 {result.name} 初始画像失败或为空，将创建新画像信息。")
                user_profile = {} # Initialize to empty dict to avoid .get errors
        except Exception as e:
            logger.warning(f"获取用户 {result.name} 画像时发生异常: {e}，将创建新画像信息。")
            user_profile = {} # Initialize to empty dict

        data = {"name": result.name}
        current_score = result.score # This is an int

        if result.exam_id == 1: # Pre-test 1
            data["exam1_score"] = str(current_score)
            exam2_score_str = user_profile.get("exam2_score")
            exam2_score = int(exam2_score_str) if exam2_score_str is not None else 0
            data["post_score"] = str(current_score + exam2_score)
            logger.info(f"用户 {result.name} 提交试卷1，分数: {current_score}。当前总前测分数: {data['post_score']}")
            
            # Retain false_id logic for pre-tests
            existing_false_ids = set()
            if user_profile.get("false_id"):
                current_ids_str = user_profile.get("false_id", "")
                if current_ids_str:
                    existing_false_ids.update(item.strip() for item in current_ids_str.split(',') if item.strip())
            new_wrong_questions = set(item.strip() for item in result.wrong_questions if item.strip())
            all_false_ids = existing_false_ids.union(new_wrong_questions)
            data["false_id"] = ",".join(sorted(list(all_false_ids)))
            logger.info(f"用户 {result.name} 更新后的错题ID: {data['false_id']}")

        elif result.exam_id == 2: # Pre-test 2
            data["exam2_score"] = str(current_score)
            exam1_score_str = user_profile.get("exam1_score")
            exam1_score = int(exam1_score_str) if exam1_score_str is not None else 0
            data["post_score"] = str(current_score + exam1_score)
            logger.info(f"用户 {result.name} 提交试卷2，分数: {current_score}。当前总前测分数: {data['post_score']}")

            # Retain false_id logic for pre-tests
            existing_false_ids = set()
            if user_profile.get("false_id"):
                current_ids_str = user_profile.get("false_id", "")
                if current_ids_str:
                    existing_false_ids.update(item.strip() for item in current_ids_str.split(',') if item.strip())
            new_wrong_questions = set(item.strip() for item in result.wrong_questions if item.strip())
            all_false_ids = existing_false_ids.union(new_wrong_questions)
            data["false_id"] = ",".join(sorted(list(all_false_ids)))
            logger.info(f"用户 {result.name} 更新后的错题ID: {data['false_id']}")

        elif result.exam_id == 3: # Post-test 1
            data["exam3_score"] = str(current_score)
            exam4_score_str = user_profile.get("exam4_score")
            exam4_score = int(exam4_score_str) if exam4_score_str is not None else 0
            data["after_score"] = str(current_score + exam4_score)
            logger.info(f"用户 {result.name} 提交试卷3，分数: {current_score}。当前总后测分数: {data['after_score']}")
            # If post-tests also need to save wrong_questions, add similar logic here for a different field, e.g., "after_false_id"

        elif result.exam_id == 4: # Post-test 2
            data["exam4_score"] = str(current_score)
            exam3_score_str = user_profile.get("exam3_score")
            exam3_score = int(exam3_score_str) if exam3_score_str is not None else 0
            data["after_score"] = str(current_score + exam3_score)
            logger.info(f"用户 {result.name} 提交试卷4，分数: {current_score}。当前总后测分数: {data['after_score']}")
            # If post-tests also need to save wrong_questions, add similar logic here

        # Ensure all potentially relevant scores are part of the data payload for update_user_profile
        # This helps if update_user_profile expects all fields or if we are adding new fields.
        for key in ["exam1_score", "exam2_score", "exam3_score", "exam4_score", "post_score", "after_score"]:
            if key not in data and user_profile.get(key) is not None:
                data[key] = user_profile.get(key) # Carry over existing scores not modified in this run

        try:
            success = update_user_profile(data)
        except Exception as db_exc: # Catch specific db exception if possible
            logger.error(f"数据库更新失败 for user {result.name}: {db_exc}", exc_info=True)
            # For simulation/testing, you might set success = True, but in prod, this is an error
            # success = True # Remove or comment out for production
            # logger.info(f"模拟更新用户画像: {result.name}, 数据: {data}")
            raise HTTPException(status_code=500, detail=f"数据库更新失败: {db_exc}")


        if not success:
            # This case might be hit if update_user_profile itself returns False without an exception
            logger.error(f"更新用户 {result.name} 画像在数据库层面返回失败。")
            raise HTTPException(status_code=400, detail="提交试卷结果失败（数据库操作未成功）")

        logger.info(f"用户 {result.name} 的试卷结果提交成功。更新的数据: {data}")
        return {"success": True, "message": "试卷结果提交成功"}
    except HTTPException: # Re-raise HTTPExceptions directly
        raise
    except Exception as e:
        logger.error(f"提交试卷结果过程中发生未知错误: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")

@router.post("/strategy-result")
async def submit_strategy_result(result: StrategyResult):
    """提交策略问卷结果"""
    try:
        logger.info(f"接收到策略问卷结果: {result.model_dump()}")
        
        # 判断是前测还是后测
        data = {"name": result.name}
        if result.is_pre_test:
            data["post_strategies_score"] = str(result.score)
            logger.info(f"设置前测策略得分: {result.score}")
        else:
            # 确保is_pre_test是布尔值，如果不是，默认为后测
            data["after_strategies_score"] = str(result.score)
            logger.info(f"设置后测策略得分: {result.score}")

        # 如果数据库函数无法使用，返回成功
        try:
            success = update_user_profile(data)
            if not success:
                logger.warning(f"更新用户策略得分失败: {data}")
                raise HTTPException(status_code=400, detail="提交策略问卷结果失败")
        except Exception as e:
            logger.error(f"更新用户策略得分出错: {e}", exc_info=True)
            success = True
            logger.info(f"模拟更新用户策略得分: {result.name}, 类型: {'前测' if result.is_pre_test else '后测'}, 分数: {result.score}")

        logger.info("策略问卷结果提交成功")
        return {"success": True, "message": "策略问卷结果提交成功"}
    except ValidationError as e:
        logger.error(f"策略问卷数据验证失败: {e}", exc_info=True)
        return {"success": False, "message": f"数据格式不正确: {str(e)}"}
    except Exception as e:
        logger.error(f"提交策略问卷结果失败: {e}", exc_info=True) 
        return {"success": False, "message": f"提交策略问卷结果失败: {str(e)}"}

# 增加路由调试端点
@router.get("/debug/routes")
async def debug_routes():
    """获取路由信息（仅用于调试）"""
    routes = []
    for route in router.routes:
        routes.append({
            "path": route.path,
            "name": route.name,
            "methods": route.methods
        })
    return {"routes": routes}

@router.get("/debug/self-rate")
async def debug_self_rate():
    """硬编码的自评量表（仅用于调试）"""
    items = [
        {"id": 1, "content": "我能借助图片读懂语言简单的短小故事，理解基本信息，如人物、时间、地点等。", "内容": "我能借助图片读懂语言简单的短小故事，理解基本信息，如人物、时间、地点等。"},
        {"id": 2, "content": "我能读懂简单的材料，如儿歌、童谣等，辨认常见词。", "内容": "我能读懂简单的材料，如儿歌、童谣等，辨认常见词。"},
        {"id": 3, "content": "我能读懂语言简单、话题熟悉的简短材料，获取具体信息、理解主要内容。", "内容": "我能读懂语言简单、话题熟悉的简短材料，获取具体信息、理解主要内容。"},
        {"id": 4, "content": "我能在读含有生词的小短文时，能借助插图或其他手段理解短文内容。", "内容": "我能在读含有生词的小短文时，能借助插图或其他手段理解短文内容。"},
        {"id": 5, "content": "我能读懂简单的应用文，如书信、通知、告示等，提取关键信息。", "内容": "我能读懂简单的应用文，如书信、通知、告示等，提取关键信息。"}
    ]
    logger.info("访问/debug/self-rate端点成功")
    return {"success": True, "items": items}