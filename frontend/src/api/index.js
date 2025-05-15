import axios from 'axios';

// 确定当前环境
const isDevelopment = process.env.NODE_ENV === 'development';

// 创建axios实例
const api = axios.create({
  // 在开发环境中使用相对路径，让Vue代理处理
  // 在生产环境中使用完整URL
  baseURL: isDevelopment ? '/api' : 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json'
  },
  timeout: 30000 // 30秒超时
});

// 创建具有更长超时时间的axios实例，用于AI相关操作
const aiApi = axios.create({
  baseURL: isDevelopment ? '/api' : 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json'
  },
  timeout: 130000 // 60秒超时，AI操作需要更长时间
});

// 请求拦截器
api.interceptors.request.use(
  config => {
    console.log(`发送请求: ${config.method.toUpperCase()} ${config.url}`, config);
    return config;
  },
  error => {
    console.error('请求配置错误:', error);
    return Promise.reject(error);
  }
);

// AI API的请求拦截器
aiApi.interceptors.request.use(
  config => {
    console.log(`发送AI请求: ${config.method.toUpperCase()} ${config.url}`, config);
    return config;
  },
  error => {
    console.error('AI请求配置错误:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  response => {
    console.log(`收到响应: ${response.config.url}, 状态: ${response.status}`);
    return response.data;
  },
  error => {
    if (error.response) {
      // 服务器返回了错误响应
      console.error(`API错误: ${error.response.status} - ${error.response.statusText}`);
      console.error('完整错误对象:', error);
    } else if (error.request) {
      // 请求已发送但没有收到响应
      console.error('API错误: 没有收到服务器响应，请检查后端服务是否运行');
      console.error('请求对象:', error.request);
    } else {
      // 请求配置出错
      console.error('API错误:', error.message);
    }
    return Promise.reject(error);
  }
);

// AI API的响应拦截器
aiApi.interceptors.response.use(
  response => {
    console.log(`收到AI响应: ${response.config.url}, 状态: ${response.status}`);
    return response.data;
  },
  error => {
    if (error.response) {
      // 服务器返回了错误响应
      console.error(`AI API错误: ${error.response.status} - ${error.response.statusText}`);
      console.error('完整错误对象:', error);
    } else if (error.request) {
      // 请求已发送但没有收到响应
      console.error('AI API错误: 没有收到服务器响应，请检查后端服务是否运行');
      console.error('请求对象:', error.request);
    } else {
      // 请求配置出错
      console.error('AI API错误:', error.message);
    }
    return Promise.reject(error);
  }
);

// 计划阶段API
const planningApi = {
  // 获取系统介绍
  getIntroduction: () => api.get('/introduction'),

  // 获取自评量表
  getSelfRateItems: () => api.get('/self-rate'),

  // 创建用户画像
  createUserProfile: (userData) => {
    console.log('准备发送的用户画像数据:', userData);
    return api.post('/user-profile', userData);
  },

  // 获取试卷
  getExam: (examId) => api.get(`/exam/${examId}`),

  // 获取策略列表
  getStrategies: () => api.get('/strategies'),

  // 提交试卷结果
  submitExamResult: (result) => api.post('/exam-result', result),

  // 提交策略问卷结果
  submitStrategyResult: (result) => api.post('/strategy-result', result),
};

// 执行阶段API
const executionApi = {
  // 获取用户信息
  getUserProfile: (userName) => api.get(`/user/${userName}`),

  // 分析用户画像
  analyzeProfile: (userName) => aiApi.get(`/analyze-profile/${userName}`),

  // 分析错题
  analyzeWrongAnswers: (userName) => aiApi.get(`/analyze-wrong-answers/${userName}`),

  // 推荐策略
  suggestStrategies: (userName) => aiApi.get(`/suggest-strategies/${userName}`),

  // 聊天
  chat: (userName, message) => aiApi.post('/chat', { name: userName, message })
};

// 反馈阶段API
const feedbackApi = {
  // 获取学习总结
  getFinalSummary: (userName) => aiApi.get(`/final-summary/${userName}`)
};

// 调试API - 开发环境使用
const debugApi = {
  // 测试API是否可用
  testConnection: () => {
    const urls = [
      '/introduction',
      '/self-rate',
      '/strategies'
    ];
    
    // 显示所有API请求路径
    console.log('API基础URL:', api.defaults.baseURL);
    urls.forEach(url => {
      console.log('可用API路径:', api.defaults.baseURL + url);
    });
    
    // 尝试请求系统介绍接口测试连接
    return api.get('/introduction')
      .then(response => {
        console.log('API连接测试成功:', response);
        return {success: true, message: 'API连接成功', data: response};
      })
      .catch(error => {
        console.error('API连接测试失败:', error);
        return {success: false, message: `API连接失败: ${error.message}`};
      });
  }
};

// 导出所有API
export default {
  planning: planningApi,
  execution: executionApi,
  feedback: feedbackApi,
  debug: debugApi
};