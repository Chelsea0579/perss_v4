# PERSS - 个性化英语阅读支持系统

PERSS（Personalized English Reading Support System）是一个基于大模型的个性化英语阅读支持系统，旨在帮助学习者提升英语阅读能力和阅读策略应用能力。

## 系统架构

- **后端**：FastAPI
- **前端**：Vue.js + Vuetify 3
- **数据库**：SQLite
- **AI 服务**：DeepseekAPI

## 功能模块

系统分为三个主要模块：

1. **计划部分**
   - 系统介绍
   - 自评量表
   - 用户信息采集
   - 阅读能力前测
   - 阅读策略前测

2. **执行阶段**
   - 用户画像分析
   - 错题分析
   - 阅读策略推荐
   - AI 交互学习

3. **反馈部分**
   - 阅读能力后测
   - 阅读策略后测
   - 学习总结与反馈

## 安装与运行

### 环境要求

- Python 3.9.21+
- Node.js 14+
- npm 6+

### 安装依赖

1. 安装 Python 依赖：

```bash
pip install -r requirements.txt
```

2. 安装前端依赖：

```bash
cd frontend
npm run serve
npm install
```

### 运行系统

使用一键启动脚本：

```bash
conda activate perss_v4
python run.py
```

该脚本会同时启动后端和前端服务，并自动打开浏览器访问前端界面。

- 后端服务运行在: http://localhost:8000
- 前端服务运行在: http://localhost:8091

## 项目结构

```
perss_v4/
│
├── app/                    # 后端代码
│   ├── routers/            # API路由
│   ├── schemas/            # Pydantic数据模型
│   ├── models/             # SQLAlchemy数据库模型（如有）
│   ├── ai_service.py       # AI服务接口
│   ├── database.py         # 数据库连接和操作
│   ├── config.py           # 配置文件
│   └── main.py             # FastAPI应用入口
│
├── frontend/               # 前端代码
│   ├── src/                # Vue源代码
│   │   ├── api/            # API接口
│   │   ├── components/     # Vue组件
│   │   ├── views/          # 页面视图
│   │   ├── router.js       # 路由配置
│   │   ├── store.js        # Vuex状态管理
│   │   ├── App.vue         # 主组件
│   │   └── main.js         # Vue入口
│   └── public/             # 静态资源
│
├── PERSS_DB.sqlite         # SQLite数据库
├── requirements.txt        # Python依赖
├── run.py                  # 启动脚本
└── README.md               # 项目说明
```

## API文档

启动后端服务后，可以通过以下URL访问API文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 许可证

Copyright © 2025