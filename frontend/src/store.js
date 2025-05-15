import { createStore } from 'vuex';
import api from './api';

export default createStore({
  state: {
    // 用户信息
    userName: localStorage.getItem('userName') || '',
    userProfile: null,

    // 计划阶段
    introduction: '',
    selfRateItems: [],
    examData: {},
    strategyItems: [],

    // 执行阶段
    profileAnalysis: '',
    wrongAnswersAnalysis: '',
    strategySuggestions: '',
    chatHistory: [],

    // 反馈阶段
    finalSummary: '',

    // 系统状态
    loading: false,
    error: null,
    currentPhase: localStorage.getItem('currentPhase') || 'planning'
  },

  getters: {
    isAuthenticated(state) {
      return !!state.userName;
    },

    getCurrentPhase(state) {
      return state.currentPhase;
    },

    getPhaseProgress(state) {
      const phases = {
        planning: ['introduction', 'self-rate', 'user-profile', 'pre-test', 'strategy-pre-test'],
        execution: ['ai-interaction'],
        feedback: ['post-test', 'strategy-post-test', 'summary']
      };

      return phases[state.currentPhase] || [];
    }
  },

  mutations: {
    SET_LOADING(state, loading) {
      state.loading = loading;
    },

    SET_ERROR(state, error) {
      state.error = error;
    },

    SET_USER_NAME(state, name) {
      state.userName = name;
      localStorage.setItem('userName', name);
    },

    SET_USER_PROFILE(state, profile) {
      state.userProfile = profile;
    },

    SET_INTRODUCTION(state, text) {
      state.introduction = text;
    },

    SET_SELF_RATE_ITEMS(state, items) {
      state.selfRateItems = items;
    },

    SET_EXAM_DATA(state, { id, data }) {
      if (!state.examData) {
        state.examData = {};
      }
      state.examData = {
        ...state.examData,
        [id]: data
      };
    },

    SET_STRATEGY_ITEMS(state, items) {
      state.strategyItems = items;
    },

    SET_PROFILE_ANALYSIS(state, analysis) {
      state.profileAnalysis = analysis;
    },

    SET_WRONG_ANSWERS_ANALYSIS(state, analysis) {
      state.wrongAnswersAnalysis = analysis;
    },

    SET_STRATEGY_SUGGESTIONS(state, suggestions) {
      state.strategySuggestions = suggestions;
    },

    ADD_CHAT_MESSAGE(state, message) {
      state.chatHistory.push(message);
    },

    SET_FINAL_SUMMARY(state, summary) {
      state.finalSummary = summary;
    },

    SET_CURRENT_PHASE(state, phase) {
      state.currentPhase = phase;
      localStorage.setItem('currentPhase', phase);
    }
  },

  actions: {
    // 计划阶段
    async fetchIntroduction({ commit }) {
      commit('SET_LOADING', true);
      try {
        const response = await api.planning.getIntroduction();
        console.log('Introduction API响应:', response);

        // 处理不同格式的响应
        if (response && response.content) {
          commit('SET_INTRODUCTION', response.content);
        }
        else if (response && response.success && response.introduction) {
          commit('SET_INTRODUCTION', response.introduction);
        }
        else if (typeof response === 'string') {
          commit('SET_INTRODUCTION', response);
        }
        else if (response && typeof response === 'object') {
          // 尝试从对象中提取内容
          const possibleContent = response.text || response.data || response.message || JSON.stringify(response);
          commit('SET_INTRODUCTION', possibleContent);
          console.log('从未知格式提取内容:', possibleContent);
        }
        else {
          console.error('未知的API响应格式:', response);
          commit('SET_ERROR', '获取系统介绍失败');
        }
      } catch (error) {
        console.error('获取系统介绍出错:', error);
        commit('SET_ERROR', error.message || '获取系统介绍失败');
      } finally {
        commit('SET_LOADING', false);
      }
    },

    async fetchSelfRateItems({ commit }) {
      commit('SET_LOADING', true);
      try {
        const response = await api.planning.getSelfRateItems();
        console.log('SelfRate API响应:', response);

        // 处理不同格式的响应
        if (Array.isArray(response)) {
          // 如果直接返回数组
          commit('SET_SELF_RATE_ITEMS', response);
        }
        else if (response && response.items) {
          // 如果返回包含items字段的对象
          commit('SET_SELF_RATE_ITEMS', response.items);
        }
        else if (response && response.success && response.items) {
          // 如果返回旧格式
          commit('SET_SELF_RATE_ITEMS', response.items);
        }
        else if (response && typeof response === 'object') {
          // 尝试从对象中找到可能的数组
          for (const key in response) {
            if (Array.isArray(response[key])) {
              commit('SET_SELF_RATE_ITEMS', response[key]);
              console.log('从未知格式提取自评量表:', key);
              break;
            }
          }
        }
        else {
          console.error('未知的API响应格式:', response);
          commit('SET_ERROR', '获取自评量表失败');
        }
      } catch (error) {
        console.error('获取自评量表出错:', error);
        commit('SET_ERROR', error.message || '获取自评量表失败');
      } finally {
        commit('SET_LOADING', false);
      }
    },

    async createUserProfile({ commit }, userData) {
      commit('SET_LOADING', true);
      try {
        const response = await api.planning.createUserProfile(userData);
        console.log('创建用户画像响应:', response);

        // 处理不同格式的响应
        if (response.success === true ||
            (response.message && response.message.includes('成功')) ||
            !response.error) {
          commit('SET_USER_NAME', userData.name);
          return true;
        } else {
          commit('SET_ERROR', response.error || response.message || '创建用户画像失败');
          return false;
        }
      } catch (error) {
        console.error('创建用户画像错误:', error);
        commit('SET_ERROR', error.message || '创建用户画像失败');
        return false;
      } finally {
        commit('SET_LOADING', false);
      }
    },

    async fetchExam({ commit }, examId) {
      commit('SET_LOADING', true);
      try {
        const response = await api.planning.getExam(examId);
        console.log(`获取试卷${examId}响应:`, response);

        // 处理不同格式的响应
        if (response.exam_id || response.content || response.questions) {
          commit('SET_EXAM_DATA', { id: examId, data: response });
          return response;
        }
        else if (response.success && (response.exam_id || response.content || response.questions)) {
          commit('SET_EXAM_DATA', { id: examId, data: response });
          return response;
        }
        else {
          commit('SET_ERROR', `获取试卷${examId}失败`);
          return null;
        }
      } catch (error) {
        console.error(`获取试卷${examId}错误:`, error);
        commit('SET_ERROR', error.message || `获取试卷${examId}失败`);
        return null;
      } finally {
        commit('SET_LOADING', false);
      }
    },

    async fetchStrategies({ commit }) {
      commit('SET_LOADING', true);
      try {
        const response = await api.planning.getStrategies();
        console.log('获取策略列表响应:', response);

        // 处理不同格式的响应
        if (Array.isArray(response)) {
          commit('SET_STRATEGY_ITEMS', response);
        }
        else if (response.items) {
          commit('SET_STRATEGY_ITEMS', response.items);
        }
        else if (response.success && response.items) {
          commit('SET_STRATEGY_ITEMS', response.items);
        }
        else {
          console.error('未知的API响应格式:', response);
          commit('SET_ERROR', '获取策略列表失败');
        }
      } catch (error) {
        console.error('获取策略列表错误:', error);
        commit('SET_ERROR', error.message || '获取策略列表失败');
      } finally {
        commit('SET_LOADING', false);
      }
    },

    async submitExamResult({ commit, state }, { examId, score, wrongQuestions }) {
      commit('SET_LOADING', true);
      try {
        const result = {
          name: state.userName,
          exam_id: examId,
          score: score,
          wrong_questions: wrongQuestions
        };

        const response = await api.planning.submitExamResult(result);
        console.log('提交试卷结果响应:', response);

        // 处理不同格式的响应
        return response.success === true ||
               (response.message && response.message.includes('成功')) ||
               !response.error;
      } catch (error) {
        console.error('提交试卷结果错误:', error);
        commit('SET_ERROR', error.message || '提交试卷结果失败');
        return false;
      } finally {
        commit('SET_LOADING', false);
      }
    },

    async submitStrategyResult({ commit, state }, { score, isPreTest }) {
      commit('SET_LOADING', true);
      try {
        const result = {
          name: state.userName,
          score: score,
          is_pre_test: isPreTest
        };

        const response = await api.planning.submitStrategyResult(result);
        console.log('提交策略问卷结果响应:', response);

        // 处理不同格式的响应
        return response.success === true ||
               (response.message && response.message.includes('成功')) ||
               !response.error;
      } catch (error) {
        console.error('提交策略问卷结果错误:', error);
        commit('SET_ERROR', error.message || '提交策略问卷结果失败');
        return false;
      } finally {
        commit('SET_LOADING', false);
      }
    },

    // 执行阶段
    async fetchUserProfile({ commit, state }) {
      if (!state.userName) return null;

      commit('SET_LOADING', true);
      try {
        const response = await api.execution.getUserProfile(state.userName);
        console.log('获取用户信息响应:', response);

        // 处理不同格式的响应
        if (response && response.user) {
          commit('SET_USER_PROFILE', response.user);
          return response.user;
        }
        else if (response && response.success && response.user) {
          commit('SET_USER_PROFILE', response.user);
          return response.user;
        }
        else if (response && typeof response === 'object' && !response.error) {
          // 可能直接返回用户对象
          commit('SET_USER_PROFILE', response);
          return response;
        }
        else {
          commit('SET_ERROR', '获取用户信息失败');
          return null;
        }
      } catch (error) {
        console.error('获取用户信息错误:', error);
        commit('SET_ERROR', error.message || '获取用户信息失败');
        return null;
      } finally {
        commit('SET_LOADING', false);
      }
    },

    async fetchProfileAnalysis({ commit, state }) {
      if (!state.userName) return '';

      commit('SET_LOADING', true);
      try {
        const response = await api.execution.analyzeProfile(state.userName);
        console.log('分析用户画像响应:', response);

        // 处理不同格式的响应
        if (response && response.analysis) {
          commit('SET_PROFILE_ANALYSIS', response.analysis);
          return response.analysis;
        }
        else if (response && response.success && response.analysis) {
          commit('SET_PROFILE_ANALYSIS', response.analysis);
          return response.analysis;
        }
        else if (typeof response === 'string') {
          commit('SET_PROFILE_ANALYSIS', response);
          return response;
        }
        else if (response) {
          // 如果响应存在但格式不符合预期，尝试提取可能的内容
          const possibleContent = response.text || response.data || response.message || JSON.stringify(response);
          commit('SET_PROFILE_ANALYSIS', possibleContent);
          console.log('从未知格式提取内容:', possibleContent);
          return possibleContent;
        }
        else {
          commit('SET_ERROR', '分析用户画像失败');
          return '';
        }
      } catch (error) {
        console.error('分析用户画像错误:', error);
        commit('SET_ERROR', error.message || '分析用户画像失败');
        return '';
      } finally {
        commit('SET_LOADING', false);
      }
    },

    async fetchWrongAnswersAnalysis({ commit, state }) {
      if (!state.userName) return '';

      commit('SET_LOADING', true);
      try {
        const response = await api.execution.analyzeWrongAnswers(state.userName);
        console.log('分析错题响应:', response);

        // 处理不同格式的响应
        if (response && response.analysis) {
          commit('SET_WRONG_ANSWERS_ANALYSIS', response.analysis);
          return response.analysis;
        }
        else if (response && response.success && response.analysis) {
          commit('SET_WRONG_ANSWERS_ANALYSIS', response.analysis);
          return response.analysis;
        }
        else if (typeof response === 'string') {
          commit('SET_WRONG_ANSWERS_ANALYSIS', response);
          return response;
        }
        else if (response) {
          // 如果响应存在但格式不符合预期，尝试提取可能的内容
          const possibleContent = response.text || response.data || response.message || JSON.stringify(response);
          commit('SET_WRONG_ANSWERS_ANALYSIS', possibleContent);
          console.log('从未知格式提取内容:', possibleContent);
          return possibleContent;
        }
        else {
          commit('SET_ERROR', response && response.error || '分析错题失败');
          return '';
        }
      } catch (error) {
        console.error('分析错题错误:', error);
        commit('SET_ERROR', error.message || '分析错题失败');
        return '';
      } finally {
        commit('SET_LOADING', false);
      }
    },

    async fetchStrategySuggestions({ commit, state }) {
      if (!state.userName) return '';

      commit('SET_LOADING', true);
      try {
        const response = await api.execution.suggestStrategies(state.userName);
        console.log('获取策略建议响应:', response);

        // 处理不同格式的响应
        if (response && response.suggestions) {
          commit('SET_STRATEGY_SUGGESTIONS', response.suggestions);
          return response.suggestions;
        }
        else if (response && response.success && response.suggestions) {
          commit('SET_STRATEGY_SUGGESTIONS', response.suggestions);
          return response.suggestions;
        }
        else if (typeof response === 'string') {
          commit('SET_STRATEGY_SUGGESTIONS', response);
          return response;
        }
        else if (response) {
          // 如果响应存在但格式不符合预期，尝试提取可能的内容
          const possibleContent = response.text || response.data || response.message || JSON.stringify(response);
          commit('SET_STRATEGY_SUGGESTIONS', possibleContent);
          console.log('从未知格式提取内容:', possibleContent);
          return possibleContent;
        }
        else {
          commit('SET_ERROR', response && response.error || '获取策略建议失败');
          // 设置默认内容，确保界面不空白
          const defaultSuggestions = `
# 阅读策略建议

由于系统暂时无法提供个性化的阅读策略建议，以下是一些通用的阅读策略，希望能对您有所帮助：

## 一、扫读技巧 (Skimming)

**目的**：快速获取文章的主要内容和结构。

**方法**：
1. 阅读标题和副标题
2. 阅读每段的第一句和最后一句
3. 注意加粗、斜体等强调内容
4. 阅读图表和总结段落

## 二、细读技巧 (Intensive Reading)

**目的**：深入理解文章的细节和论点。

**方法**：
1. 阅读每一个句子
2. 标记关键词和重要信息
3. 注意过渡词和逻辑连接词
4. 思考作者的意图和态度

## 三、SQ3R 方法

1. **Survey**：快速浏览全文
2. **Question**：提出问题
3. **Read**：阅读文章
4. **Recite**：复述内容
5. **Review**：回顾全文

希望这些通用策略对您有所帮助。如需获取更个性化的建议，请稍后再试。
          `;
          commit('SET_STRATEGY_SUGGESTIONS', defaultSuggestions);
          return defaultSuggestions;
        }
      } catch (error) {
        console.error('获取策略建议错误:', error);
        commit('SET_ERROR', error.message || '获取策略建议失败');
        
        // 设置默认内容，确保界面不空白
        const defaultSuggestions = `
# 阅读策略建议

由于系统暂时无法提供个性化的阅读策略建议，以下是一些通用的阅读策略，希望能对您有所帮助：

## 一、扫读技巧 (Skimming)

**目的**：快速获取文章的主要内容和结构。

**方法**：
1. 阅读标题和副标题
2. 阅读每段的第一句和最后一句
3. 注意加粗、斜体等强调内容
4. 阅读图表和总结段落

## 二、细读技巧 (Intensive Reading)

**目的**：深入理解文章的细节和论点。

**方法**：
1. 阅读每一个句子
2. 标记关键词和重要信息
3. 注意过渡词和逻辑连接词
4. 思考作者的意图和态度

## 三、SQ3R 方法

1. **Survey**：快速浏览全文
2. **Question**：提出问题
3. **Read**：阅读文章
4. **Recite**：复述内容
5. **Review**：回顾全文

希望这些通用策略对您有所帮助。如需获取更个性化的建议，请稍后再试。
        `;
        commit('SET_STRATEGY_SUGGESTIONS', defaultSuggestions);
        return defaultSuggestions;
      } finally {
        commit('SET_LOADING', false);
      }
    },

    async sendChatMessage({ commit, state }, message) {
      if (!state.userName) return null;

      // 添加用户消息到历史
      const userMessage = {
        role: 'user',
        content: message,
        timestamp: new Date().toISOString()
      };
      commit('ADD_CHAT_MESSAGE', userMessage);

      commit('SET_LOADING', true);
      try {
        const response = await api.execution.chat(state.userName, message);
        console.log('发送消息响应:', response);

        // 处理不同格式的响应
        if (response && response.response) {
          // 添加AI回复到历史
          const aiMessage = {
            role: 'assistant',
            content: response.response,
            timestamp: new Date().toISOString()
          };
          commit('ADD_CHAT_MESSAGE', aiMessage);
          return aiMessage;
        }
        else if (response && response.success && response.response) {
          const aiMessage = {
            role: 'assistant',
            content: response.response,
            timestamp: new Date().toISOString()
          };
          commit('ADD_CHAT_MESSAGE', aiMessage);
          return aiMessage;
        }
        else if (typeof response === 'string') {
          const aiMessage = {
            role: 'assistant',
            content: response,
            timestamp: new Date().toISOString()
          };
          commit('ADD_CHAT_MESSAGE', aiMessage);
          return aiMessage;
        }
        else if (response) {
          // 如果响应存在但格式不符合预期，尝试提取可能的内容
          const possibleContent = response.text || response.data || response.message || JSON.stringify(response);
          const aiMessage = {
            role: 'assistant',
            content: possibleContent,
            timestamp: new Date().toISOString()
          };
          commit('ADD_CHAT_MESSAGE', aiMessage);
          console.log('从未知格式提取内容:', possibleContent);
          return aiMessage;
        }
        else {
          commit('SET_ERROR', response && response.error || '发送消息失败');
          return null;
        }
      } catch (error) {
        console.error('发送消息错误:', error);
        commit('SET_ERROR', error.message || '发送消息失败');
        return null;
      } finally {
        commit('SET_LOADING', false);
      }
    },

    // 反馈阶段
    async fetchFinalSummary({ commit, state }) {
      if (!state.userName) return '';

      commit('SET_LOADING', true);
      try {
        const response = await api.feedback.getFinalSummary(state.userName);
        console.log('获取学习总结响应:', response);

        // 处理不同格式的响应
        if (response && response.summary) {
          commit('SET_FINAL_SUMMARY', response.summary);
          return response.summary;
        }
        else if (response && response.success && response.summary) {
          commit('SET_FINAL_SUMMARY', response.summary);
          return response.summary;
        }
        else if (typeof response === 'string') {
          commit('SET_FINAL_SUMMARY', response);
          return response;
        }
        else if (response) {
          // 如果响应存在但格式不符合预期，尝试提取可能的内容
          const possibleContent = response.text || response.data || response.message || JSON.stringify(response);
          commit('SET_FINAL_SUMMARY', possibleContent);
          console.log('从未知格式提取内容:', possibleContent);
          return possibleContent;
        }
        else {
          commit('SET_ERROR', '获取学习总结失败');
          return '';
        }
      } catch (error) {
        console.error('获取学习总结错误:', error);
        commit('SET_ERROR', error.message || '获取学习总结失败');
        return '';
      } finally {
        commit('SET_LOADING', false);
      }
    },

    // 系统状态
    setCurrentPhase({ commit }, phase) {
      commit('SET_CURRENT_PHASE', phase);
    }
  }
});