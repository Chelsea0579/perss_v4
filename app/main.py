import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
from pathlib import Path

# 导入配置
from app.config import CORS_ORIGINS, API_PREFIX 

# 导入自定义路由模块
from app.routers import planning, execution, feedback

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 创建FastAPI应用 - 不使用中间件参数
app = FastAPI(
    title="个性化英语阅读支持系统API",
    description="为英语阅读学习提供个性化支持的API服务",
    version="1.0.0",
)

# 注册路由
app.include_router(planning.router, prefix=API_PREFIX)
app.include_router(execution.router, prefix=API_PREFIX)
app.include_router(feedback.router, prefix=API_PREFIX)

# 根路径，显示欢迎页面
@app.get("/", response_class=HTMLResponse)
async def root():
    """API根路径，显示简单的欢迎页面"""
    return """
    <html>
        <head>
            <title>PERSS API</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    line-height: 1.6;
                }
                h1 {
                    color: #1976D2;
                }
                .footer {
                    margin-top: 40px;
                    font-size: 0.9em;
                    color: #666;
                }
            </style>
        </head>
        <body>
            <h1>个性化英语阅读支持系统API</h1>
            <p>欢迎使用PERSS API服务，该API为个性化英语阅读支持系统提供后端支持。</p>
            <p>该系统基于计划-执行-反馈三阶段设计，通过个性化分析和反馈，帮助用户提升英语阅读能力。</p>
            <h2>API文档</h2>
            <p>查看API文档，请访问 <a href="/docs">/docs</a> 或 <a href="/redoc">/redoc</a></p>
            <h2>测试客户端</h2>
            <p>使用简易测试客户端，请访问 <a href="/client">/client</a></p>
            <div class="footer">
                <p>&copy; 2025 个性化英语阅读支持系统</p>
            </div>
        </body>
    </html>
    """

# 简易测试客户端
@app.get("/client", response_class=HTMLResponse)
async def test_client():
    """简易测试客户端页面"""
    return """
    <html>
        <head>
            <title>PERSS 测试客户端</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 1000px;
                    margin: 0 auto;
                    padding: 20px;
                    line-height: 1.6;
                }
                h1, h2, h3 {
                    color: #1976D2;
                }
                .card {
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    padding: 16px;
                    margin-bottom: 20px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .form-group {
                    margin-bottom: 15px;
                }
                label {
                    display: block;
                    margin-bottom: 5px;
                    font-weight: bold;
                }
                input, select, textarea {
                    width: 100%;
                    padding: 8px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    box-sizing: border-box;
                }
                textarea {
                    height: 100px;
                    font-family: monospace;
                }
                button {
                    background-color: #1976D2;
                    color: white;
                    border: none;
                    padding: 10px 15px;
                    border-radius: 4px;
                    cursor: pointer;
                }
                button:hover {
                    background-color: #1565C0;
                }
                #response {
                    background-color: #f5f5f5;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    padding: 10px;
                    white-space: pre-wrap;
                    font-family: monospace;
                    max-height: 300px;
                    overflow-y: auto;
                }
                .tabs {
                    display: flex;
                    border-bottom: 1px solid #ddd;
                    margin-bottom: 20px;
                }
                .tab {
                    padding: 10px 20px;
                    cursor: pointer;
                    border: 1px solid transparent;
                    border-bottom: none;
                }
                .tab.active {
                    background-color: #f5f5f5;
                    border-color: #ddd;
                    border-radius: 4px 4px 0 0;
                }
                .tab-content {
                    display: none;
                }
                .tab-content.active {
                    display: block;
                }
            </style>
        </head>
        <body>
            <h1>PERSS 测试客户端</h1>
            
            <div class="tabs">
                <div class="tab active" onclick="showTab('tab-intro')">系统介绍</div>
                <div class="tab" onclick="showTab('tab-self-rate')">自评量表</div>
                <div class="tab" onclick="showTab('tab-user-profile')">用户画像</div>
                <div class="tab" onclick="showTab('tab-custom')">自定义请求</div>
            </div>
            
            <!-- 系统介绍 -->
            <div id="tab-intro" class="tab-content active">
                <div class="card">
                    <h3>获取系统介绍</h3>
                    <button onclick="getIntroduction()">获取介绍</button>
                </div>
            </div>
            
            <!-- 自评量表 -->
            <div id="tab-self-rate" class="tab-content">
                <div class="card">
                    <h3>获取自评量表</h3>
                    <button onclick="getSelfRate()">获取量表</button>
                    <div id="self-rate-form" style="margin-top: 20px; display: none;">
                        <h4>自评量表</h4>
                        <div id="self-rate-items"></div>
                    </div>
                </div>
            </div>
            
            <!-- 用户画像 -->
            <div id="tab-user-profile" class="tab-content">
                <div class="card">
                    <h3>创建用户画像</h3>
                    <div class="form-group">
                        <label for="name">姓名</label>
                        <input type="text" id="name" placeholder="请输入姓名">
                    </div>
                    <div class="form-group">
                        <label for="grade">年级</label>
                        <input type="text" id="grade" placeholder="请输入年级">
                    </div>
                    <div class="form-group">
                        <label for="major">专业</label>
                        <input type="text" id="major" placeholder="请输入专业">
                    </div>
                    <div class="form-group">
                        <label for="gender">性别</label>
                        <select id="gender">
                            <option value="男">男</option>
                            <option value="女">女</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="cet4_taken">是否参加过四级考试</label>
                        <select id="cet4_taken">
                            <option value="是">是</option>
                            <option value="否">否</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="cet4_score">四级总分</label>
                        <input type="text" id="cet4_score" placeholder="请输入四级总分">
                    </div>
                    <div class="form-group">
                        <label for="cet4_reading_score">四级阅读分数</label>
                        <input type="text" id="cet4_reading_score" placeholder="请输入四级阅读分数">
                    </div>
                    <button onclick="createUserProfile()">创建用户画像</button>
                </div>
            </div>
            
            <!-- 自定义请求 -->
            <div id="tab-custom" class="tab-content">
                <div class="card">
                    <h3>自定义API请求</h3>
                    <div class="form-group">
                        <label for="method">请求方法</label>
                        <select id="method">
                            <option value="GET">GET</option>
                            <option value="POST">POST</option>
                            <option value="PUT">PUT</option>
                            <option value="DELETE">DELETE</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="url">请求路径</label>
                        <input type="text" id="url" placeholder="例如: /api/introduction">
                    </div>
                    <div class="form-group">
                        <label for="body">请求体 (POST/PUT)</label>
                        <textarea id="body" placeholder='例如: {"name": "测试用户"}'></textarea>
                    </div>
                    <button onclick="sendCustomRequest()">发送请求</button>
                </div>
            </div>
            
            <!-- 响应区域 -->
            <div class="card">
                <h3>响应结果</h3>
                <div id="response">等待请求...</div>
            </div>
            
            <script>
                // 切换标签页
                function showTab(tabId) {
                    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
                    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
                    
                    const selectedTab = document.querySelector(`.tab[onclick="showTab('${tabId}')"]`);
                    const selectedContent = document.getElementById(tabId);
                    
                    if (selectedTab && selectedContent) {
                        selectedTab.classList.add('active');
                        selectedContent.classList.add('active');
                    }
                }
                
                // 通用请求函数
                async function sendRequest(method, url, body = null) {
                    try {
                        const options = {
                            method: method,
                            headers: {
                                'Content-Type': 'application/json'
                            }
                        };
                        
                        if (body && (method === 'POST' || method === 'PUT')) {
                            options.body = JSON.stringify(body);
                        }
                        
                        const response = await fetch(url, options);
                        const data = await response.json();
                        
                        document.getElementById('response').innerText = 
                            `状态码: ${response.status}\n\n${JSON.stringify(data, null, 2)}`;
                        
                        return { success: true, data };
                    } catch (error) {
                        document.getElementById('response').innerText = 
                            `错误: ${error.message}`;
                        
                        return { success: false, error };
                    }
                }
                
                // 获取系统介绍
                async function getIntroduction() {
                    document.getElementById('response').innerText = '正在请求数据...';
                    await sendRequest('GET', '/api/introduction');
                }
                
                // 获取自评量表
                async function getSelfRate() {
                    document.getElementById('response').innerText = '正在请求数据...';
                    const result = await sendRequest('GET', '/api/self-rate');
                    
                    if (result.success && result.data.items && result.data.items.length > 0) {
                        const itemsContainer = document.getElementById('self-rate-items');
                        itemsContainer.innerHTML = '';
                        
                        result.data.items.forEach(item => {
                            const itemDiv = document.createElement('div');
                            itemDiv.className = 'form-group';
                            itemDiv.innerHTML = `
                                <p><strong>${item.id}. ${item.content || '无法显示内容'}</strong></p>
                                <select id="self-rate-${item.id}">
                                    <option value="1">1 - 完全不符合</option>
                                    <option value="2">2 - 不太符合</option>
                                    <option value="3">3 - 一般</option>
                                    <option value="4">4 - 比较符合</option>
                                    <option value="5">5 - 完全符合</option>
                                </select>
                            `;
                            itemsContainer.appendChild(itemDiv);
                        });
                        
                        document.getElementById('self-rate-form').style.display = 'block';
                    }
                }
                
                // 创建用户画像
                async function createUserProfile() {
                    document.getElementById('response').innerText = '正在请求数据...';
                    
                    const userData = {
                        name: document.getElementById('name').value,
                        grade: document.getElementById('grade').value,
                        major: document.getElementById('major').value,
                        gender: document.getElementById('gender').value,
                        cet4_taken: document.getElementById('cet4_taken').value,
                        cet4_score: document.getElementById('cet4_score').value,
                        cet4_reading_score: document.getElementById('cet4_reading_score').value,
                        cet6_taken: "否",
                        cet6_score: "",
                        cet6_reading_score: "",
                        other_scores: "",
                        exam_name: "",
                        total_score: "",
                        reading_score: ""
                    };
                    
                    await sendRequest('POST', '/api/user-profile', userData);
                }
                
                // 发送自定义请求
                async function sendCustomRequest() {
                    document.getElementById('response').innerText = '正在请求数据...';
                    
                    const method = document.getElementById('method').value;
                    const url = document.getElementById('url').value;
                    const bodyElement = document.getElementById('body');
                    let body = null;
                    
                    if (bodyElement.value.trim() && (method === 'POST' || method === 'PUT')) {
                        try {
                            body = JSON.parse(bodyElement.value);
                        } catch (error) {
                            document.getElementById('response').innerText = 
                                `请求体JSON格式错误: ${error.message}`;
                            return;
                        }
                    }
                    
                    await sendRequest(method, url, body);
                }
            </script>
        </body>
    </html>
    """

# 健康检查端点
@app.get("/healthcheck")
async def healthcheck():
    """API健康检查端点"""
    return {"status": "healthy", "version": "1.0.0"}