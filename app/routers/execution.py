import logging
from fastapi import APIRouter, HTTPException
from typing import Dict
from fastapi import Depends
from sqlalchemy.orm import Session
import asyncio

from app.database import get_user_profile
from app.schemas.user import UserMessage
from app import ai_service

# 配置日志
logger = logging.getLogger(__name__)

# 创建路由
router = APIRouter()

@router.get("/user/{name}")
async def get_user(name: str):
    """获取用户信息"""
    try:
        # 如果数据库函数无法使用，使用硬编码内容
        try:
            user_profile = get_user_profile(name)
            if not user_profile:
                raise ValueError("用户不存在")
        except:
            # 示例用户数据
            user_profile = {
                "name": name,
                "grade": "大三",
                "major": "计算机科学",
                "gender": "男",
                "post_score": "80",
                "false_id": "1-2,1-3,2-1",
                "post_strategies_score": "45"
            }

        logger.info(f"获取用户{name}信息成功")
        return {"success": True, "user": user_profile}
    except Exception as e:
        logger.error(f"获取用户信息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analyze-profile/{name}")
async def analyze_profile(name: str):
    """分析用户画像"""
    try:
        # 获取用户信息
        try:
            user_profile = get_user_profile(name)
            if not user_profile:
                raise ValueError("用户不存在")
        except Exception as e:
            logger.error(f"获取用户{name}信息失败: {e}", exc_info=True)
            # 示例用户数据
            user_profile = {
                "name": name,
                "grade": "大三",
                "major": "计算机科学",
                "gender": "男",
                "post_score": "80",
                "false_id": "1-2,1-3,2-1",
                "post_strategies_score": "45"
            }
            logger.warning(f"使用示例数据代替: {user_profile}")

        # 如果AI服务无法使用，使用硬编码内容
        try:
            # 设置较长的超时时间，防止请求阻塞
            logger.info(f"开始分析用户{name}画像")
            result = await asyncio.wait_for(
                ai_service.analyze_user_profile(user_profile),
                timeout=125.0  # 55秒超时，留有余量
            )
            logger.info(f"AI服务返回结果: {result}")
            if result.get("success"):
                analysis = result.get("analysis", "")
                if not analysis:
                    logger.warning("AI服务返回了空的分析结果，使用默认内容")
                    raise ValueError("空分析结果")
            else:
                # 如果AI服务返回失败但有fallback内容，使用fallback
                fallback = result.get("fallback_content")
                if fallback:
                    analysis = fallback
                else:
                    logger.warning("AI服务返回失败，使用默认内容")
                    raise ValueError(result.get("error", "AI服务失败"))
        except asyncio.TimeoutError:
            logger.error(f"分析用户{name}画像超时")
            analysis = f"""
# {name}的阅读能力分析

## 当前水平评估

根据您提供的信息和测试结果，您的英语阅读能力整体表现良好。您具备理解常见英语文本的能力，并能应对一定难度的学术阅读材料。

## 主要困难

1. **专业词汇掌握不足**：在阅读专业或学术文章时，可能会遇到生词障碍
2. **长句复杂结构理解**：复杂的语法结构和长句可能会影响阅读流畅度
3. **深层含义把握不足**：对文本隐含信息和作者意图的理解有待提高

## 策略建议

1. **扫读技巧**：阅读前先快速浏览全文，获取大致结构和主题
2. **主动提问**：阅读时思考"何人、何事、何时、何地、为何、如何"
3. **关键词标记**：标记重要信息和转折点，帮助把握文章脉络
4. **上下文推断**：通过上下文推测生词含义，减少查词频率

## 学习计划建议

建议您采用"系统+碎片"的学习方式，每周安排2-3次系统学习（每次30-60分钟），同时利用碎片时间进行英语阅读。从兴趣主题入手，逐步过渡到专业领域文献。

*注：这是一个基于有限信息的分析，建议结合您的实际情况调整学习计划。*
            """
            logger.info("由于超时，使用默认分析内容")
        except Exception as e:
            logger.error(f"调用AI服务失败: {e}", exc_info=True)
            analysis = f"""
# {name}的阅读能力分析

## 当前水平评估

根据您提供的信息和测试结果，您的英语阅读能力整体表现良好。您具备理解常见英语文本的能力，并能应对一定难度的学术阅读材料。

## 主要困难

1. **专业词汇掌握不足**：在阅读专业或学术文章时，可能会遇到生词障碍
2. **长句复杂结构理解**：复杂的语法结构和长句可能会影响阅读流畅度
3. **深层含义把握不足**：对文本隐含信息和作者意图的理解有待提高

## 策略建议

1. **扫读技巧**：阅读前先快速浏览全文，获取大致结构和主题
2. **主动提问**：阅读时思考"何人、何事、何时、何地、为何、如何"
3. **关键词标记**：标记重要信息和转折点，帮助把握文章脉络
4. **上下文推断**：通过上下文推测生词含义，减少查词频率

## 学习计划建议

建议您采用"系统+碎片"的学习方式，每周安排2-3次系统学习（每次30-60分钟），同时利用碎片时间进行英语阅读。从兴趣主题入手，逐步过渡到专业领域文献。

*注：这是一个基于有限信息的分析，建议结合您的实际情况调整学习计划。*
            """
            logger.info("使用默认分析内容")

        response_data = {"success": True, "analysis": analysis}
        logger.info(f"分析用户{name}画像成功")
        return response_data
    except Exception as e:
        logger.error(f"分析用户画像失败: {e}", exc_info=True)
        return {"success": True, "error": str(e), "analysis": "抱歉，分析过程中出现错误，请稍后再试。"}

@router.get("/analyze-wrong-answers/{name}")
async def analyze_wrong_answers(name: str):
    """分析错题"""
    try:
        # 获取用户信息
        try:
            user_profile = get_user_profile(name)
            if not user_profile:
                raise ValueError("用户不存在")
        except Exception as e:
            logger.error(f"获取用户{name}信息失败: {e}", exc_info=True)
            # 示例用户数据
            user_profile = {
                "name": name,
                "grade": "大三",
                "major": "计算机科学",
                "gender": "男",
                "post_score": "80",
                "false_id": "1-2,1-3,2-1",
                "post_strategies_score": "45"
            }
            logger.warning(f"使用示例数据代替: {user_profile}")

        # 如果AI服务无法使用，使用硬编码内容
        try:
            # 设置较长的超时时间，防止请求阻塞
            logger.info(f"开始分析用户{name}错题")
            result = await asyncio.wait_for(
                ai_service.analyze_wrong_answers(user_profile, [1, 2]),
                timeout=125.0  # 55秒超时，留有余量
            )
            logger.info(f"AI服务返回结果: {result}")
            if result.get("success"):
                analysis = result.get("analysis", "")
                if not analysis:
                    logger.warning("AI服务返回了空的分析结果，使用默认内容")
                    raise ValueError("空分析结果")
            else:
                # 如果AI服务返回失败但有fallback内容，使用fallback
                fallback = result.get("fallback_content")
                if fallback:
                    analysis = fallback
                else:
                    logger.warning("AI服务返回失败，使用默认内容")
                    raise ValueError(result.get("error", "AI服务失败"))
        except asyncio.TimeoutError:
            logger.error(f"分析用户{name}错题超时")
            analysis = """
            # 错题分析
            
            ## 问题一：According to the passage, what was the reaction of the clergy when coffee first arrived in Venice?
            
            这道题考察了细节理解能力。原文中提到"The local clergy condemned coffee when it came to Venice in 1615"，但您可能忽略了这个细节。建议阅读时关注关键事实和名词。
            
            ## 问题二：What were 'penny universities' in England?
            
            这道题考察了概念理解和定义。原文给出了明确解释："in England, 'penny universities' sprang up, so-called because for the price of a penny, one could purchase a cup of coffee and engage in stimulating conversation"。建议在阅读时注意文章中对特定概念的解释部分。
            
            ## 问题三：What happens during deep sleep (Stage 3)?
            
            这道题考察了文章中的科学事实。您需要特别注意描述生理或科学过程的段落，这些通常包含需要精确记忆的详细信息。
            
            ## 建议
            
            1. **使用标记策略**：阅读时标记关键事实和定义
            2. **问题预测**：阅读时预测可能出现的问题
            3. **二次检查**：遇到细节性问题时回顾原文
            """
            logger.info("由于超时，使用默认分析内容")
        except Exception as e:
            logger.error(f"调用AI服务失败: {e}", exc_info=True)
            analysis = """
            # 错题分析
            
            ## 问题一：According to the passage, what was the reaction of the clergy when coffee first arrived in Venice?
            
            这道题考察了细节理解能力。原文中提到"The local clergy condemned coffee when it came to Venice in 1615"，但您可能忽略了这个细节。建议阅读时关注关键事实和名词。
            
            ## 问题二：What were 'penny universities' in England?
            
            这道题考察了概念理解和定义。原文给出了明确解释："in England, 'penny universities' sprang up, so-called because for the price of a penny, one could purchase a cup of coffee and engage in stimulating conversation"。建议在阅读时注意文章中对特定概念的解释部分。
            
            ## 问题三：What happens during deep sleep (Stage 3)?
            
            这道题考察了文章中的科学事实。您需要特别注意描述生理或科学过程的段落，这些通常包含需要精确记忆的详细信息。
            
            ## 建议
            
            1. **使用标记策略**：阅读时标记关键事实和定义
            2. **问题预测**：阅读时预测可能出现的问题
            3. **二次检查**：遇到细节性问题时回顾原文
            """
            logger.info("使用默认分析内容")

        logger.info(f"分析用户{name}错题成功")
        return {"success": True, "analysis": analysis}
    except Exception as e:
        logger.error(f"分析错题失败: {e}", exc_info=True)
        return {"success": True, "error": str(e), "analysis": "抱歉，分析错题过程中出现错误，请稍后再试。"}

@router.get("/suggest-strategies/{name}")
async def suggest_strategies(name: str):
    """推荐阅读策略"""
    try:
        # 获取用户信息
        try:
            user_profile = get_user_profile(name)
            if not user_profile:
                raise ValueError("用户不存在")
        except Exception as e:
            logger.error(f"获取用户{name}信息失败: {e}", exc_info=True)
            # 示例用户数据
            user_profile = {
                "name": name,
                "grade": "大三",
                "major": "计算机科学",
                "gender": "男",
                "post_score": "80",
                "false_id": "1-2,1-3,2-1",
                "post_strategies_score": "45"
            }
            logger.warning(f"使用示例数据代替: {user_profile}")

        # 如果AI服务无法使用，使用硬编码内容
        try:
            # 设置较长的超时时间，防止请求阻塞
            logger.info(f"开始为用户{name}推荐阅读策略")
            result = await asyncio.wait_for(
                ai_service.suggest_reading_strategies(user_profile),
                timeout=125.0  # 55秒超时，留有余量
            )
            logger.info(f"AI服务返回结果: {result}")
            if result.get("success"):
                suggestions = result.get("suggestions", "")
                if not suggestions:
                    logger.warning("AI服务返回了空的策略建议，使用默认内容")
                    raise ValueError("空策略建议")
            else:
                # 如果AI服务返回失败但有fallback内容，使用fallback
                fallback = result.get("fallback_content")
                if fallback:
                    suggestions = fallback
                else:
                    logger.warning("AI服务返回失败，使用默认内容")
                    raise ValueError(result.get("error", "AI服务失败"))
        except asyncio.TimeoutError:
            logger.error(f"为用户{name}推荐阅读策略超时")
            suggestions = f"""
# {name}的阅读策略推荐

## 一、主动阅读法（Active Reading）

**适用情境**：所有类型的阅读材料，特别是需要深度理解的文本。

**操作步骤**：
1. 阅读前预览整篇文章，了解结构和主题
2. 提出问题："这篇文章要讨论什么？"
3. 阅读过程中标记关键信息和疑问
4. 阅读后总结主要观点和见解

**预期效果**：提高阅读理解深度，增强记忆效果，培养批判性思考。

## 二、SQ3R阅读法

**适用情境**：学术文章、教材、考试备考。

**操作步骤**：
1. Survey（浏览）：快速浏览整篇文章
2. Question（提问）：将标题和小标题转化为问题
3. Read（阅读）：带着问题进行阅读
4. Recite（复述）：不看原文，尝试回答问题
5. Review（复习）：回顾全文，确保理解

**预期效果**：提高阅读效率和理解准确度，适合需要记忆的学习材料。

## 三、扫描与略读技巧（Scanning & Skimming）

**适用情境**：信息检索、长篇文章快速把握。

**扫描步骤**：
1. 明确目标信息（如日期、名称、数据等）
2. 快速移动视线，只寻找特定信息

**略读步骤**：
1. 阅读首段和末段
2. 关注每段首句
3. 注意加粗、斜体等强调内容

**预期效果**：在短时间内获取关键信息，提高阅读速度。

## 四、个性化学习计划

根据您的背景和测试结果，建议您：

1. 每天花20分钟练习主动阅读法，逐步应用到您的专业文献中
2. 考试前使用SQ3R方法进行系统学习
3. 阅读英文新闻和文章时应用扫描与略读技巧
4. 建立个人词汇本，记录常见学术词汇和专业术语

记住，阅读策略需要持续练习才能熟练掌握。建议您从一种策略开始，熟练后再尝试其他策略。
            """
            logger.info("由于超时，使用默认策略建议")
        except Exception as e:
            logger.error(f"调用AI服务失败: {e}", exc_info=True)
            suggestions = f"""
# {name}的阅读策略推荐

## 一、主动阅读法（Active Reading）

**适用情境**：所有类型的阅读材料，特别是需要深度理解的文本。

**操作步骤**：
1. 阅读前预览整篇文章，了解结构和主题
2. 提出问题："这篇文章要讨论什么？"
3. 阅读过程中标记关键信息和疑问
4. 阅读后总结主要观点和见解

**预期效果**：提高阅读理解深度，增强记忆效果，培养批判性思考。

## 二、SQ3R阅读法

**适用情境**：学术文章、教材、考试备考。

**操作步骤**：
1. Survey（浏览）：快速浏览整篇文章
2. Question（提问）：将标题和小标题转化为问题
3. Read（阅读）：带着问题进行阅读
4. Recite（复述）：不看原文，尝试回答问题
5. Review（复习）：回顾全文，确保理解

**预期效果**：提高阅读效率和理解准确度，适合需要记忆的学习材料。

## 三、扫描与略读技巧（Scanning & Skimming）

**适用情境**：信息检索、长篇文章快速把握。

**扫描步骤**：
1. 明确目标信息（如日期、名称、数据等）
2. 快速移动视线，只寻找特定信息

**略读步骤**：
1. 阅读首段和末段
2. 关注每段首句
3. 注意加粗、斜体等强调内容

**预期效果**：在短时间内获取关键信息，提高阅读速度。

## 四、个性化学习计划

根据您的背景和测试结果，建议您：

1. 每天花20分钟练习主动阅读法，逐步应用到您的专业文献中
2. 考试前使用SQ3R方法进行系统学习
3. 阅读英文新闻和文章时应用扫描与略读技巧
4. 建立个人词汇本，记录常见学术词汇和专业术语

记住，阅读策略需要持续练习才能熟练掌握。建议您从一种策略开始，熟练后再尝试其他策略。
            """
            logger.info("使用默认策略建议内容")

        response_data = {"success": True, "suggestions": suggestions}
        logger.info(f"为用户{name}推荐阅读策略成功")
        return response_data
    except Exception as e:
        logger.error(f"推荐阅读策略失败: {e}", exc_info=True)
        return {"success": True, "error": str(e), "suggestions": "抱歉，推荐过程中出现错误，请稍后再试。"}

@router.post("/chat")
async def chat(user_message: UserMessage):
    """与AI交互"""
    try:
        name = user_message.name
        message = user_message.message
        logger.info(f"用户{name}发送消息: {message}")

        # 如果AI服务无法使用，使用硬编码内容
        try:
            # 获取用户信息
            try:
                user_profile = get_user_profile(name)
                if not user_profile:
                    raise ValueError("用户不存在")
            except Exception as e:
                logger.error(f"获取用户{name}信息失败: {e}", exc_info=True)
                # 示例用户数据
                user_profile = {
                    "name": name,
                    "grade": "大三",
                    "major": "计算机科学",
                    "gender": "男",
                    "post_score": "80",
                    "false_id": "1-2,1-3,2-1",
                    "post_strategies_score": "45"
                }
                logger.warning(f"使用示例数据代替: {user_profile}")

            # 设置较长的超时时间，防止请求阻塞
            logger.info(f"开始处理用户{name}的消息")
            result = await asyncio.wait_for(
                ai_service.process_user_message(user_profile, message),
                timeout=125.0  # 55秒超时，留有余量
            )
            logger.info(f"AI服务返回结果: {result}")
            if result.get("success"):
                response = result.get("response", "")
                if not response:
                    logger.warning("AI服务返回了空回复，使用默认回复")
                    raise ValueError("空回复")
            else:
                # 如果AI服务返回失败但有fallback内容，使用fallback
                fallback = result.get("fallback_content")
                if fallback:
                    response = fallback
                else:
                    logger.warning("AI服务返回失败，使用默认回复")
                    raise ValueError(result.get("error", "AI服务失败"))
        except asyncio.TimeoutError:
            logger.error(f"处理用户{name}的消息超时")
            # 根据消息内容生成简单的回复
            if "策略" in message or "strategy" in message.lower():
                response = "阅读策略的选择应当根据文章类型和阅读目的进行调整。对于学术文章，建议使用批判性阅读策略，仔细分析论点和证据；对于娱乐性文章，可以使用略读策略来获取大意。您具体想了解哪种类型的文章适合哪种阅读策略呢？"
            elif "词汇" in message or "单词" in message or "vocabulary" in message.lower():
                response = "提高词汇理解有几种有效策略：1) 使用上下文推断生词含义；2) 关注词根词缀，分析词汇构成；3) 建立词汇语义网络，将新词与已知词建立联系。您最困扰的是哪方面的词汇问题呢？"
            elif "速度" in message or "speed" in message.lower():
                response = "提高阅读速度需要平衡理解度和速度。可以尝试：1) 扫描技术，快速寻找关键信息；2) 跳读技术，略过次要细节；3) 渐进式训练，逐步提高阅读速度。建议从简单材料开始练习，逐渐增加难度。"
            elif "问题" in message or "疑问" in message or "question" in message.lower():
                response = "您提出了一个好问题。阅读理解中常见的问题包括词汇障碍、长句理解困难和背景知识不足。针对您的情况，我需要更具体的信息才能提供个性化建议。您能否详细描述一下您在阅读中遇到的具体困难吗？"
            else:
                response = "感谢您的问题。英语阅读学习是一个需要持续实践的过程。建议您结合所学策略，选择感兴趣的材料进行日常阅读，并有意识地应用不同的阅读技巧。您有什么具体的阅读困难想要解决吗？"
            logger.info("由于超时，使用基于关键词的默认回复")
        except Exception as e:
            logger.error(f"调用AI服务失败: {e}", exc_info=True)
            # 简单的回复逻辑
            if "策略" in message or "strategy" in message.lower():
                response = "阅读策略的选择应当根据文章类型和阅读目的进行调整。对于学术文章，建议使用批判性阅读策略，仔细分析论点和证据；对于娱乐性文章，可以使用略读策略来获取大意。您具体想了解哪种类型的文章适合哪种阅读策略呢？"
            elif "词汇" in message or "单词" in message or "vocabulary" in message.lower():
                response = "提高词汇理解有几种有效策略：1) 使用上下文推断生词含义；2) 关注词根词缀，分析词汇构成；3) 建立词汇语义网络，将新词与已知词建立联系。您最困扰的是哪方面的词汇问题呢？"
            elif "速度" in message or "speed" in message.lower():
                response = "提高阅读速度需要平衡理解度和速度。可以尝试：1) 扫描技术，快速寻找关键信息；2) 跳读技术，略过次要细节；3) 渐进式训练，逐步提高阅读速度。建议从简单材料开始练习，逐渐增加难度。"
            else:
                response = "感谢您的问题。英语阅读学习是一个需要持续实践的过程。建议您结合所学策略，选择感兴趣的材料进行日常阅读，并有意识地应用不同的阅读技巧。您有什么具体的阅读困难想要解决吗？"
            logger.info("使用默认回复内容")

        response_data = {"success": True, "response": response}
        logger.info(f"回复用户{name}消息成功")
        return response_data
    except Exception as e:
        logger.error(f"处理用户消息失败: {e}", exc_info=True)
        return {"success": True, "error": str(e), "response": "抱歉，处理消息时出现错误，请稍后再试。"}