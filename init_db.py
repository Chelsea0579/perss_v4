import sqlite3
import logging
import os
import sys
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 数据库路径
DATABASE_PATH = "D:/PycharmProjects/perss_v4/PERSS_DB.sqlite"


def init_db():
    """初始化数据库，检查结构并创建必要的表"""
    # 确保数据库目录存在
    db_dir = os.path.dirname(DATABASE_PATH)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)

    # 连接数据库
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        logger.info("成功连接到数据库")

        # 获取当前表
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0] for table in cursor.fetchall()]
        logger.info(f"数据库中的表: {tables}")

        # 检查并创建必要的表
        check_and_create_tables(conn, tables)

        # 检查每个表的结构
        check_table_structure(conn, tables)

        # 关闭数据库连接
        conn.close()
        logger.info("数据库检查完成，结构正确")

    except sqlite3.Error as e:
        logger.error(f"数据库错误: {e}")
        sys.exit(1)


def check_and_create_tables(conn, existing_tables):
    """检查并创建必要的表"""
    cursor = conn.cursor()

    # 必要的表
    required_tables = [
        'CognitiveStrategies',
        'Strategies',
        'User Profile',
        'exam',
        'introduction',
        'self_rate'
    ]

    # 创建缺失的表
    for table in required_tables:
        if table not in existing_tables:
            logger.warning(f"表 {table} 不存在，将创建")

            if table == 'CognitiveStrategies':
                cursor.execute('''
                CREATE TABLE "CognitiveStrategies" (
                    "id" INTEGER PRIMARY KEY,
                    "content" TEXT,
                    "detail" TEXT
                );
                ''')
                # 插入示例数据
                insert_cognitive_strategies(conn)

            elif table == 'Strategies':
                cursor.execute('''
                CREATE TABLE "Strategies" (
                    "id" INTEGER PRIMARY KEY,
                    "content" TEXT,
                    "1.I have never heard of this strategy before." TEXT,
                    "2.I have heard of this strategy,but I don't know what it means." TEXT,
                    "3.I have heard of this strategy,and I think I know what it means." TEXT,
                    "4.I know this strategy,and I can explain how and when to use it." TEXT,
                    "5.I know this strategy quite well,and I often use it when Iread." TEXT
                );
                ''')
                # 插入示例数据
                insert_strategies(conn)

            elif table == 'User Profile':
                cursor.execute('''
                CREATE TABLE "User Profile" (
                    "name" TEXT PRIMARY KEY,
                    "grade" TEXT,
                    "major" TEXT,
                    "gender" TEXT,
                    "Have you taken the CET-4 exam:" TEXT,
                    "CET-4 score" TEXT,
                    "CET-4 reading score" TEXT,
                    "Have you taken the CET-6 exam" TEXT,
                    "CET-6 score" TEXT,
                    "CET-6 reading score" TEXT,
                    "Other English scores for reference" TEXT,
                    "Exam name" TEXT,
                    "Total score" TEXT,
                    "Reading score" TEXT,
                    "post_score" TEXT,
                    "false_id" TEXT,
                    "post_strategies_score" TEXT,
                    "after_strategies_score" TEXT,
                    "after_score" TEXT
                );
                ''')

            elif table == 'exam':
                cursor.execute('''
                CREATE TABLE "exam" (
                    "id" INTEGER PRIMARY KEY,
                    "content" TEXT,
                    "t1" TEXT,
                    "a1" TEXT,
                    "t2" TEXT,
                    "a2" TEXT,
                    "t3" TEXT,
                    "a3" TEXT,
                    "t4" TEXT,
                    "a4" TEXT,
                    "t5" TEXT,
                    "a5" TEXT
                );
                ''')
                # 插入示例数据
                insert_exams(conn)

            elif table == 'introduction':
                cursor.execute('''
                CREATE TABLE "introduction" (
                    "同学你好！欢迎使用英语阅读个性化学习支持系统。这个系统旨在帮助你提升英语阅读能力，尤其是阅读策略这方面。该系统的设计基于自我调节学习理，该理论强调学习者在学习过程中通过计划、执行和反馈的循环，不断调整自己的学习策略，提升学习效果。系统按照计划-执行-反馈的三个阶段设计一系列活动，帮助你在阅读过程中不断优化自己的阅读策略。" TEXT
                );
                ''')
                # 插入系统介绍
                cursor.execute('''
                INSERT INTO "introduction" VALUES (
                    "同学你好！欢迎使用英语阅读个性化学习支持系统。这个系统旨在帮助你提升英语阅读能力，尤其是阅读策略这方面。该系统的设计基于自我调节学习理，该理论强调学习者在学习过程中通过计划、执行和反馈的循环，不断调整自己的学习策略，提升学习效果。系统按照计划-执行-反馈的三个阶段设计一系列活动，帮助你在阅读过程中不断优化自己的阅读策略。"
                );
                ''')

            elif table == 'self_rate':
                cursor.execute('''
                CREATE TABLE "self_rate" (
                    "id" INTEGER PRIMARY KEY,
                    "内容" TEXT,
                    "完全不符合1" TEXT,
                    "有些不符合2" TEXT,
                    "有些符合3" TEXT,
                    "比较符合4" TEXT,
                    "非常符合5" TEXT
                );
                ''')
                # 插入示例数据
                insert_self_rate_items(conn)

    conn.commit()


def check_table_structure(conn, tables):
    """检查每个表的结构和数据"""
    cursor = conn.cursor()

    for table in tables:
        # 获取表的列信息
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        logger.info(f"表 {table} 的列: {column_names}")

        # 获取表的记录数
        cursor.execute(f"SELECT COUNT(*) FROM \"{table}\"")
        count = cursor.fetchone()[0]
        logger.info(f"表 {table} 有 {count} 条记录")

        # 如果表没有数据，发出警告
        if count == 0:
            logger.warning(f"表 {table} 没有数据")
            # 对于必要的表，添加示例数据
            if table == 'introduction':
                cursor.execute('''
                INSERT INTO "introduction" VALUES (
                    "同学你好！欢迎使用英语阅读个性化学习支持系统。这个系统旨在帮助你提升英语阅读能力，尤其是阅读策略这方面。该系统的设计基于自我调节学习理，该理论强调学习者在学习过程中通过计划、执行和反馈的循环，不断调整自己的学习策略，提升学习效果。系统按照计划-执行-反馈的三个阶段设计一系列活动，帮助你在阅读过程中不断优化自己的阅读策略。"
                );
                ''')
                conn.commit()


def insert_cognitive_strategies(conn):
    """插入认知策略示例数据"""
    strategies = [
        (1, "Frame Sentences", "使用框架句帮助学生理解句式结构和内容词汇"),
        (2, "Ask and Answer Questions", "提问并回答问题，促进主动阅读理解"),
        (3, "Clarify", "澄清不理解的部分，寻求解释或查询资源"),
        (4, "Collaborative Strategic Reading", "小组合作阅读，交流理解和策略"),
        (5, "Concept Maps", "创建概念图，可视化文本中的关键概念和关系"),
        (6, "Evaluating", "评估文本质量、可靠性和相关性"),
        (7, "Graphic Organizers", "使用图形组织器整理文本信息"),
        (8, "Highlight Texts", "高亮标记重要信息，识别关键点"),
        (9, "Inferencing", "基于文本和背景知识进行推理，理解隐含信息"),
        (10, "Mental Imagery", "形成心理图像，增强理解和记忆"),
        (11, "Monitor Comprehension", "监控自己的理解程度，识别困难点"),
        (12, "Predict", "预测文本内容和发展，然后验证"),
        (13, "Question Generation", "生成关于文本的问题，促进深度理解"),
        (14, "Reciprocal Teaching", "轮流担任教师角色，教授阅读策略"),
        (15, "Retelling", "复述文本内容，检验理解程度"),
        (16, "Summarization", "概括文本主要内容和要点"),
        (17, "Think-Aloud", "大声说出阅读过程中的思考"),
        (18, "Using Context", "利用上下文线索理解生词和难句"),
        (19, "Visualizing", "将文本内容可视化，创建图像辅助理解"),
        (20, "Word Analysis", "分析词汇结构，理解词义"),
        (21, "Text Structure", "识别文本结构（如因果、比较对比等）"),
        (22, "Prior Knowledge Activation", "激活相关背景知识，连接新旧信息")
    ]

    cursor = conn.cursor()
    cursor.executemany('''
    INSERT INTO "CognitiveStrategies" ("id", "content", "detail")
    VALUES (?, ?, ?)
    ''', strategies)
    conn.commit()


def insert_strategies(conn):
    """插入策略问卷示例数据"""
    strategies = [
        (1, "I preview the reading material before I begin to read."),
        (2, "Before I begin reading, I think about the topic to see what I already know about it."),
        (3, "I try to predict what the material is about when I read."),
        (4, "While I am reading, I periodically check if the material is making sense to me."),
        (5, "I adjust my reading speed according to what I'm reading."),
        (6, "I create visual images from what I'm reading."),
        (7, "I try to identify the main ideas when I read."),
        (8, "I pay attention to text features like bold print and headings."),
        (9, "When I don't understand something, I try to figure it out from the surrounding context."),
        (10, "I ask myself questions about what I am reading."),
        (11, "When reading, I translate from English into my native language."),
        (12, "I make notes or underline/highlight important information when I read."),
        (13, "After reading, I summarize or paraphrase what I've read."),
        (14, "I discuss what I read with others to check my understanding."),
        (15, "I look for relationships between ideas in the text.")
    ]

    cursor = conn.cursor()
    cursor.executemany('''
    INSERT INTO "Strategies" ("id", "content")
    VALUES (?, ?)
    ''', strategies)
    conn.commit()


def insert_exams(conn):
    """插入考试示例数据"""
    exams = [
        (1,
         "The History of Coffee\n\nCoffee cultivation and trade began on the Arabian Peninsula. By the 15th century, coffee was being grown in the Yemeni district of Arabia, and by the 16th century, it was known in Persia, Egypt, Syria, and Turkey. Coffee was not only enjoyed in homes but also in the many public coffee houses — called qahveh khaneh — which began to appear in cities across the Near East. The popularity of the coffee houses was unequaled, and people frequented them for all kinds of social activities.\n\nEuropean travelers to the Near East brought back stories of an unusual dark black beverage. By the 17th century, coffee had made its way to Europe and was becoming popular across the continent. Some people reacted to this new beverage with suspicion or fear, calling it the 'bitter invention of Satan.' The local clergy condemned coffee when it came to Venice in 1615. The controversy was so great that Pope Clement VIII was asked to intervene. Before making a decision, he decided to taste the beverage for himself. He found it so satisfying that he gave it papal approval.\n\nDespite such controversy, coffee houses were quickly becoming centers of social activity and communication in the major cities of England, Austria, France, Germany, and Holland. In England, 'penny universities' sprang up, so-called because for the price of a penny, one could purchase a cup of coffee and engage in stimulating conversation.\n\nCoffee began to replace the common breakfast drinks of the time — beer and wine. Those who drank coffee instead of alcohol began the day alert and energized, and not surprisingly, the quality of their work was greatly improved. (This could actually be considered one of the greatest impacts of coffee on modern society.)\n\nBy the mid-17th century, there were over 300 coffee houses in London, many of which attracted like-minded patrons, including merchants, shippers, brokers, and artists. Many businesses grew out of these specialized coffee houses. Lloyd's of London, for example, came into existence at the Edward Lloyd's Coffee House.",
         "When did coffee cultivation and trade begin?", "On the Arabian Peninsula",
         "According to the passage, what was the reaction of the clergy when coffee first arrived in Venice?",
         "They condemned it",
         "What were 'penny universities' in England?",
         "Coffee houses where people could engage in conversation for a penny",
         "How did coffee change breakfast habits in Europe?", "It replaced beer and wine",
         "What major business mentioned in the passage originated from a coffee house?", "Lloyd's of London"),
        (2,
         "The Importance of Sleep\n\nSleep is a natural and recurring state of rest for the mind and body, with the eyes usually closed and consciousness being either fully or partially lost. It is a time when the body's systems are in an anabolic state, helping to restore the immune, nervous, skeletal, and muscular systems. These are vital processes that maintain mood, memory, and cognitive function, and play a large role in the function of the endocrine and immune systems. In fact, chronic sleep deprivation can cause numerous health issues.\n\nThe amount of sleep each person needs depends on many factors, including age. Infants generally require about 16-18 hours a day, while teenagers need about 9-10 hours on average. For most adults, 7-8 hours a night appears to be the best amount of sleep. However, the quality of sleep is just as important as the quantity.\n\nSleep occurs in a recurring cycle of 90 to 110 minutes and is divided into two categories: non-REM (which is further split into three phases) and REM sleep. Each type is linked to specific brain waves and neuronal activity. You cycle through all stages of non-REM and REM sleep several times during a typical night, with increasingly longer, deeper REM periods occurring toward morning.\n\nNon-REM sleep consists of three stages. Stage 1 is the lightest, lasting just 1-7 minutes. During this time, your heartbeat, breathing, and eye movements slow, and your muscles relax with occasional twitches. This is the stage between being awake and falling asleep. Stage 2 is a period of light sleep during which your heartbeat and breathing slow, and muscles relax even further. Your body temperature drops and eye movements stop. Brain wave activity slows but is marked by brief bursts of electrical activity. Stage 3 is the period of deep sleep that you need to feel refreshed in the morning. It occurs in longer periods during the first half of the night. Your heartbeat and breathing slow to their lowest levels during sleep, and your muscles are relaxed. It may be difficult to wake you during this stage.\n\nREM sleep first occurs about 90 minutes after falling asleep. Your eyes move rapidly from side to side behind closed eyelids. Mixed frequency brain wave activity becomes closer to that seen in wakefulness. Your breathing becomes faster and irregular, and your heart rate and blood pressure increase to near waking levels. Most of your dreaming occurs during REM sleep, although some can also occur in non-REM sleep. Your arm and leg muscles become temporarily paralyzed, which prevents you from acting out your dreams.",
         "What is sleep described as in the passage?", "A natural and recurring state of rest for the mind and body",
         "According to the passage, what happens during deep sleep (Stage 3)?",
         "Heartbeat and breathing slow to their lowest levels",
         "How long after falling asleep does REM sleep first occur?", "About 90 minutes",
         "What health aspect is NOT mentioned as being restored during sleep?", "Digestive system",
         "What happens to your muscles during REM sleep?", "They become temporarily paralyzed"),
        (3,
         "Ocean Acidification\n\nOcean acidification is the ongoing decrease in the pH of the Earth's oceans, caused by the uptake of carbon dioxide (CO2) from the atmosphere. Seawater is slightly basic (meaning pH > 7), and ocean acidification involves a shift towards a less basic (more acidic) pH level. Between 1751 and 2021, the pH value of the ocean surface is estimated to have decreased from approximately 8.25 to 8.14.\n\nThe primary cause of ocean acidification is human-driven carbon dioxide emissions. When CO2 enters the ocean, it reacts with water molecules (H2O) to form carbonic acid (H2CO3). This weak acid then partially dissociates into hydrogen ions (H+) and bicarbonate ions (HCO3-). The increase in hydrogen ions causes the decrease in pH, making the ocean more acidic.\n\nThis increased acidity has significant negative impacts on marine life, particularly organisms that build shells or skeletons from calcium carbonate (CaCO3), such as corals, mollusks, and some plankton. In more acidic conditions, the carbonate ions (CO3 2-) that these organisms need to build their structures combine with the excess hydrogen ions to form bicarbonate ions, making carbonate less available. Additionally, under more acidic conditions, existing calcium carbonate structures begin to dissolve.\n\nCoral reefs are particularly vulnerable to ocean acidification. These important ecosystems provide habitat for about 25% of all marine species and are already threatened by rising sea temperatures due to climate change. Ocean acidification compounds this threat by potentially slowing coral growth and weakening existing coral structures.\n\nBeyond calcifying organisms, research is revealing that ocean acidification may impact marine life in more subtle ways. Some fish species show behavioral changes, such as reduced ability to detect predators, in more acidic water. Certain invertebrates show reduced reproductive success. These effects could cascade through marine food webs, affecting the overall biodiversity and productivity of the ocean ecosystem.\n\nMitigating ocean acidification requires global action to reduce carbon dioxide emissions. Since most ocean acidification is caused by CO2 in the atmosphere, the same actions that help combat climate change – transitioning to renewable energy, increasing energy efficiency, and preserving carbon sinks like forests – will also help slow ocean acidification.",
         "What is the primary cause of ocean acidification?", "Human-driven carbon dioxide emissions",
         "What chemical reaction occurs when CO2 enters the ocean?", "It reacts with water to form carbonic acid",
         "Why are corals particularly vulnerable to ocean acidification?",
         "They build structures from calcium carbonate",
         "According to the passage, what behavioral change has been observed in some fish species due to ocean acidification?",
         "Reduced ability to detect predators",
         "What action is suggested to mitigate ocean acidification?", "Reduce carbon dioxide emissions"),
        (4,
         "Artificial Intelligence in Healthcare\n\nArtificial intelligence (AI) is rapidly transforming the healthcare industry, offering new ways to improve patient outcomes, reduce costs, and enhance the efficiency of care delivery. AI refers to the simulation of human intelligence in machines that are programmed to think and learn like humans. In healthcare, AI applications range from simple administrative workflows to complex clinical decision support systems.\n\nOne of the most promising applications of AI in healthcare is in medical imaging analysis. AI algorithms can be trained to identify abnormalities in X-rays, MRIs, CT scans, and other imaging modalities with accuracy that sometimes exceeds that of human radiologists. For example, deep learning models have demonstrated the ability to detect early signs of breast cancer in mammograms, identify stroke and hemorrhage in brain scans, and spot signs of diabetic retinopathy in eye images. These capabilities could enable earlier disease detection and potentially save lives.\n\nAI is also being used to analyze vast amounts of healthcare data to identify patterns and insights that humans might miss. Predictive analytics models can forecast patient deterioration, readmission risks, or the likelihood of developing specific conditions based on electronic health records (EHRs) and other data sources. By identifying high-risk patients, healthcare providers can intervene earlier and potentially prevent adverse outcomes.\n\nIn the pharmaceutical industry, AI is accelerating drug discovery and development processes. Machine learning algorithms can analyze biological data to identify potential drug targets, predict how molecules will behave in the human body, and even design new drug compounds. This could significantly reduce the time and cost of bringing new treatments to market.\n\nNatural language processing (NLP), a branch of AI focused on the interaction between computers and human language, is improving administrative efficiency in healthcare. NLP can automate the transcription of clinical notes, extract relevant information from medical literature, and enhance the functionality of virtual assistants and chatbots for patient engagement.\n\nDespite its promise, AI in healthcare faces significant challenges. Ensuring the privacy and security of patient data used to train AI models is paramount. Regulatory frameworks need to evolve to address the unique considerations of AI-based medical tools. There are also concerns about algorithmic bias, where AI systems might perform differently across demographic groups if trained on non-representative data. Addressing these challenges will be crucial for realizing the full potential of AI in healthcare.",
         "What is one of the most promising applications of AI in healthcare according to the passage?",
         "Medical imaging analysis",
         "How can predictive analytics models help healthcare providers?",
         "By identifying high-risk patients for early intervention",
         "In what way is AI benefiting the pharmaceutical industry?",
         "Accelerating drug discovery and development processes",
         "What is natural language processing (NLP) improving in healthcare?", "Administrative efficiency",
         "What challenge of AI in healthcare is related to training data?", "Algorithmic bias")
    ]

    cursor = conn.cursor()
    for exam in exams:
        cursor.execute('''
        INSERT INTO "exam" ("id", "content", "t1", "a1", "t2", "a2", "t3", "a3", "t4", "a4", "t5", "a5")
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', exam)
    conn.commit()


def insert_self_rate_items(conn):
    """插入自评量表示例数据"""
    items = [
        (1, "我能够理解简单的英语阅读材料，如短文和故事。"),
        (2, "我能够在英语阅读中识别出主要观点和细节。"),
        (3, "我通常能够理解英语文章中的词汇和短语。"),
        (4, "我能够推断英语文章中未明确表达的信息。"),
        (5, "我能够迅速识别英语阅读材料的整体结构。"),
        (6, "我在阅读英语时能够保持专注。"),
        (7, "我能够有效地分析英语文章的论点和论据。"),
        (8, "我能够理解英语阅读材料中的不同观点和视角。"),
        (9, "我能够以较快的速度阅读英语文章，同时保持理解。"),
        (10, "我能够使用上下文线索来理解不熟悉的词汇。"),
        (11, "我能够识别和理解英语文章中的比喻和成语。"),
        (12, "我能够批判性地评估英语阅读材料中的论点和证据。"),
        (13, "我能够灵活调整阅读策略以适应不同类型的英语文本。"),
        (14, "我能够识别英语文章中的作者意图和态度。"),
        (15, "我在阅读英语材料时能够做好笔记和摘要。"),
        (16, "我能够在不需要频繁查词典的情况下阅读英语文章。"),
        (17, "我在阅读前会预览英语文章的标题、小标题和图表。"),
        (18, "我能够将英语阅读材料中的新信息与已有知识联系起来。"),
        (19, "我能够理解复杂的英语语法结构，如长句和嵌套从句。"),
        (20, "我在阅读完英语文章后能够准确回答相关问题。"),
        (21, "我能够欣赏和理解英语文学作品的深层含义。"),
        (22, "我对自己的英语阅读能力有信心。")
    ]

    cursor = conn.cursor()
    cursor.executemany('''
    INSERT INTO "self_rate" ("id", "内容")
    VALUES (?, ?)
    ''', items)
    conn.commit()


if __name__ == "__main__":
    init_db()
    print("数据库检查完成，可以启动应用。")