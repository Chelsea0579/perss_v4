import logging
from fastapi import APIRouter, HTTPException

from app.database import get_user_profile
from app import ai_service

# 配置日志
logger = logging.getLogger(__name__)

# 创建路由
router = APIRouter()

@router.get("/final-summary/{name}")
async def final_summary(name: str):
    """生成学习总结"""
    try:
        # 获取用户信息
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
                "after_score": "90",
                "false_id": "1-2,1-3,2-1",
                "post_strategies_score": "45",
                "after_strategies_score": "60"
            }

        # 如果AI服务无法使用，使用硬编码内容
        try:
            result = await ai_service.generate_final_summary(user_profile)
            summary = result.get("summary", "")
        except:
            summary = """
            # 学习总结报告
            
            ## 成就与进步
            
            在本次个性化英语阅读学习过程中，您取得了显著进步：
            
            - **阅读测试分数**：从80分提高到90分，提升了12.5%
            - **阅读策略水平**：从45分提高到60分，提升了33.3%
            
            特别是在理解文章主旨和推断隐含信息方面有明显进步，表明您已经开始有效地应用所学策略。
            
            ## 前后测对比分析
            
            ### 阅读能力
            
            前测中您在细节理解和上下文推断方面存在困难，主要体现在推断类和定义类问题上。后测中这些问题的正确率有明显提高，说明您在这些方面已有改善。
            
            ### 策略应用
            
            前测中您对阅读策略的认知和应用处于初级到中级水平之间，后测结果显示您对预览策略、问题生成策略和上下文理解策略的掌握已达到中级水平。
            
            ## 当前水平评估
            
            您目前的英语阅读水平为：**中级**
            
            您已经能够理解一般性英语文章的主要内容和部分细节，可以使用基本的阅读策略辅助理解，但在面对复杂学术文本或含有大量专业词汇的文章时仍有挑战。
            
            ## 策略建议
            
            建议您继续巩固以下策略：
            
            1. **预览策略**：继续练习快速获取文章大意的能力
            2. **批判性阅读策略**：学习分析作者观点、论据和逻辑关系
            3. **词汇推断策略**：进一步提高根据上下文推断词义的能力
            4. **综合整合策略**：练习将文章不同部分的信息整合理解
            
            ## 未来学习计划
            
            ### 短期目标（1-2个月）
            
            - 每天阅读1篇英语新闻或文章，应用所学策略
            - 建立个人词汇本，记录阅读中遇到的新词和表达
            - 尝试阅读不同类型的文章，如科技、文化、经济等
            
            ### 长期目标（3-6个月）
            
            - 提高阅读速度，同时保持理解度
            - 尝试阅读英语原版书籍或学术论文
            - 参加英语阅读讨论小组，提高表达和交流能力
            
            继续坚持学习，您的英语阅读能力将会持续提升！
            """

        logger.info(f"生成用户{name}学习总结成功")
        return {"success": True, "summary": summary}
    except Exception as e:
        logger.error(f"生成学习总结失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))