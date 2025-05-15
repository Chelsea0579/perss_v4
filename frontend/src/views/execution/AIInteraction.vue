<template>
  <div class="ai-interaction">
    <v-tabs v-model="activeTab" bg-color="transparent">
      <v-tab value="overview">
        <v-icon start icon="mdi-account-details-outline"></v-icon>
        学习概览
      </v-tab>
      <v-tab value="wrong-answers">
        <v-icon start icon="mdi-clipboard-alert-outline"></v-icon>
        错题解析
      </v-tab>
      <v-tab value="strategies">
        <v-icon start icon="mdi-lightbulb-outline"></v-icon>
        策略建议
      </v-tab>
      <v-tab value="chat">
        <v-icon start icon="mdi-message-text-outline"></v-icon>
        个性化辅导
      </v-tab>
    </v-tabs>

    <v-window v-model="activeTab" class="mt-4">
      <!-- 学习概览 -->
      <v-window-item value="overview">
        <v-card>
          <v-card-title class="text-h5 primary--text">
            <v-icon start icon="mdi-account-details-outline"></v-icon>
            学习概览
          </v-card-title>

          <v-card-text>
            <v-alert
              v-if="!profileAnalysis && !loadingAnalysis"
              type="info"
              variant="tonal"
              border="start"
            >
              正在加载个性化学习分析，请稍候...
              <v-btn
                variant="text"
                color="primary"
                @click="loadProfileAnalysis"
                class="mt-2"
              >
                点击分析
              </v-btn>
            </v-alert>

            <div v-else-if="profileAnalysis" class="analysis-content">
              <div v-html="formattedProfileAnalysis"></div>
            </div>

            <v-skeleton-loader
              v-else-if="loadingAnalysis"
              type="article"
            ></v-skeleton-loader>
          </v-card-text>
        </v-card>
      </v-window-item>

      <!-- 错题解析 -->
      <v-window-item value="wrong-answers">
        <v-card>
          <v-card-title class="text-h5 primary--text">
            <v-icon start icon="mdi-clipboard-alert-outline"></v-icon>
            错题解析
          </v-card-title>

          <v-card-text>
            <v-alert
              v-if="!wrongAnswersAnalysis && !loadingWrongAnswers"
              type="info"
              variant="tonal"
              border="start"
            >
              点击下方按钮获取您的错题解析
              <v-btn
                variant="text"
                color="primary"
                @click="loadWrongAnswersAnalysis"
                class="mt-2"
              >
                分析错题
              </v-btn>
            </v-alert>

            <div v-else-if="wrongAnswersAnalysis" class="analysis-content">
              <div v-html="formattedWrongAnswersAnalysis"></div>
            </div>

            <v-skeleton-loader
              v-else-if="loadingWrongAnswers"
              type="article"
            ></v-skeleton-loader>
          </v-card-text>
        </v-card>
      </v-window-item>

      <!-- 策略建议 -->
      <v-window-item value="strategies">
        <v-card>
          <v-card-title class="text-h5 primary--text">
            <v-icon start icon="mdi-lightbulb-outline"></v-icon>
            阅读策略建议
          </v-card-title>

          <v-card-text>
            <v-alert
              v-if="!strategySuggestions && !loadingStrategies"
              type="info"
              variant="tonal"
              border="start"
            >
              点击下方按钮获取个性化阅读策略建议
              <v-btn
                variant="text"
                color="primary"
                @click="loadStrategySuggestions"
                class="mt-2"
              >
                获取建议
              </v-btn>
            </v-alert>

            <div v-else-if="strategySuggestions" class="analysis-content">
              <div v-html="formattedStrategySuggestions"></div>
            </div>

            <v-skeleton-loader
              v-else-if="loadingStrategies"
              type="article"
            ></v-skeleton-loader>
          </v-card-text>
        </v-card>
      </v-window-item>

      <!-- 个性化辅导 -->
      <v-window-item value="chat">
        <v-card>
          <v-card-title class="text-h5 primary--text">
            <v-icon start icon="mdi-message-text-outline"></v-icon>
            个性化辅导交流
          </v-card-title>

          <v-card-text>
            <div class="chat-container">
              <div class="chat-messages" ref="chatMessages">
                <!-- 系统提示消息 -->
                <v-alert
                  v-if="chatHistory.length === 0"
                  type="info"
                  variant="tonal"
                  border="start"
                  class="mb-4"
                >
                  <p>欢迎使用个性化辅导功能！您可以：</p>
                  <ul>
                    <li>询问如何应用特定的阅读策略</li>
                    <li>请求解释难以理解的阅读概念</li>
                    <li>获取针对您水平的阅读材料建议</li>
                    <li>寻求进一步的英语阅读学习方法</li>
                  </ul>
                </v-alert>

                <!-- 聊天消息 -->
                <div
                  v-for="(message, index) in chatHistory"
                  :key="index"
                  :class="['message', message.role === 'user' ? 'user-message' : 'assistant-message']"
                >
                  <div class="message-content">
                    <div v-html="formatMessage(message.content)"></div>
                    <div class="message-time">{{ formatTime(message.timestamp) }}</div>
                  </div>
                </div>

                <!-- 加载中提示 -->
                <div v-if="loading" class="message assistant-message">
                  <div class="message-content">
                    <v-progress-circular
                      indeterminate
                      color="primary"
                      size="24"
                    ></v-progress-circular>
                    <span class="ml-2">思考中...</span>
                  </div>
                </div>
              </div>

              <div class="chat-input">
                <v-textarea
                  v-model="userMessage"
                  variant="outlined"
                  label="输入您的问题"
                  rows="2"
                  auto-grow
                  hide-details
                  class="chat-textarea"
                  @keydown.enter.exact.prevent="sendMessage"
                ></v-textarea>

                <v-btn
                  color="primary"
                  icon
                  class="send-button"
                  @click="sendMessage"
                  :disabled="!userMessage.trim() || loading"
                >
                  <v-icon icon="mdi-send"></v-icon>
                </v-btn>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-window-item>
    </v-window>

    <div class="d-flex justify-end mt-4">
      <v-btn
        color="success"
        variant="flat"
        :to="{ name: 'PostTest', params: { id: 3 } }"
        @click="updatePhase"
      >
        进入后测阶段
        <v-icon end icon="mdi-arrow-right"></v-icon>
      </v-btn>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch, nextTick } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';
import { marked } from 'marked';

export default {
  name: 'AIInteraction',

  setup() {
    const store = useStore();
    const router = useRouter();
    const chatMessages = ref(null);

    // 当前活动标签
    const activeTab = ref('overview');

    // 聊天消息
    const userMessage = ref('');
    const chatHistory = computed(() => store.state.chatHistory);

    // 加载状态
    const loading = computed(() => store.state.loading);
    const loadingAnalysis = ref(false);
    const loadingWrongAnswers = ref(false);
    const loadingStrategies = ref(false);

    // 分析数据
    const profileAnalysis = computed(() => store.state.profileAnalysis);
    const wrongAnswersAnalysis = computed(() => store.state.wrongAnswersAnalysis);
    const strategySuggestions = computed(() => store.state.strategySuggestions);

    // 格式化分析文本，使用Markdown渲染
    const formattedProfileAnalysis = computed(() => {
      return profileAnalysis.value ? marked(profileAnalysis.value) : '';
    });

    const formattedWrongAnswersAnalysis = computed(() => {
      return wrongAnswersAnalysis.value ? marked(wrongAnswersAnalysis.value) : '';
    });

    const formattedStrategySuggestions = computed(() => {
      return strategySuggestions.value ? marked(strategySuggestions.value) : '';
    });

    // 加载用户画像分析
    const loadProfileAnalysis = async () => {
      loadingAnalysis.value = true;
      await store.dispatch('fetchProfileAnalysis');
      loadingAnalysis.value = false;
    };

    // 加载错题分析
    const loadWrongAnswersAnalysis = async () => {
      loadingWrongAnswers.value = true;
      await store.dispatch('fetchWrongAnswersAnalysis');
      loadingWrongAnswers.value = false;
    };

    // 加载策略建议
    const loadStrategySuggestions = async () => {
      loadingStrategies.value = true;
      await store.dispatch('fetchStrategySuggestions');
      loadingStrategies.value = false;
    };

    // 发送聊天消息
    const sendMessage = async () => {
      const message = userMessage.value.trim();
      if (!message || loading.value) return;

      userMessage.value = '';
      await store.dispatch('sendChatMessage', message);
    };

    // 格式化消息，将换行符转换为<br>
    const formatMessage = (message) => {
      return message.replace(/\n/g, '<br>');
    };

    // 格式化时间戳
    const formatTime = (timestamp) => {
      const date = new Date(timestamp);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

    // 更新阶段
    const updatePhase = () => {
      store.dispatch('setCurrentPhase', 'feedback');
    };

    // 组件挂载时
    onMounted(async () => {
      // 获取用户信息
      await store.dispatch('fetchUserProfile');

      // 自动加载用户画像分析
      if (!profileAnalysis.value) {
        loadProfileAnalysis();
      }
    });

    // 监听聊天历史变化，自动滚动到底部
    watch(chatHistory, () => {
      nextTick(() => {
        if (chatMessages.value) {
          chatMessages.value.scrollTop = chatMessages.value.scrollHeight;
        }
      });
    });

    return {
      activeTab,
      userMessage,
      chatHistory,
      chatMessages,
      loading,
      loadingAnalysis,
      loadingWrongAnswers,
      loadingStrategies,
      profileAnalysis,
      wrongAnswersAnalysis,
      strategySuggestions,
      formattedProfileAnalysis,
      formattedWrongAnswersAnalysis,
      formattedStrategySuggestions,
      sendMessage,
      formatMessage,
      formatTime,
      loadProfileAnalysis,
      loadWrongAnswersAnalysis,
      loadStrategySuggestions,
      updatePhase
    };
  }
};
</script>

<style scoped>
.ai-interaction {
  max-width: 100%;
}

.analysis-content {
  max-height: 600px;
  overflow-y: auto;
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.chat-container {
  display: flex;
  flex-direction: column;
  height: 600px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background-color: #f8f9fa;
}

.message {
  margin-bottom: 16px;
  max-width: 80%;
}

.user-message {
  margin-left: auto;
}

.assistant-message {
  margin-right: auto;
}

.message-content {
  padding: 12px;
  border-radius: 12px;
  position: relative;
}

.user-message .message-content {
  background-color: #e3f2fd;
  color: #0d47a1;
}

.assistant-message .message-content {
  background-color: #f5f5f5;
  color: #333;
}

.message-time {
  font-size: 0.7rem;
  color: #757575;
  text-align: right;
  margin-top: 4px;
}

.chat-input {
  display: flex;
  padding: 8px;
  background-color: #fff;
  border-top: 1px solid #e0e0e0;
}

.chat-textarea {
  flex: 1;
}

.send-button {
  margin-left: 8px;
  align-self: flex-end;
}
</style>