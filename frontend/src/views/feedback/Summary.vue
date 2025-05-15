<template>
  <div class="summary">
    <v-card>
      <v-card-title class="text-h5 primary--text">
        <v-icon start icon="mdi-chart-bar"></v-icon>
        学习总结与反馈
      </v-card-title>

      <v-card-text>
        <v-alert
          v-if="!finalSummary && !loading"
          type="info"
          variant="tonal"
          border="start"
        >
          正在生成您的学习总结，请点击下方按钮获取。
          <v-btn
            variant="text"
            color="primary"
            @click="loadFinalSummary"
            class="mt-2"
          >
            生成总结
          </v-btn>
        </v-alert>

        <v-skeleton-loader
          v-else-if="loading"
          type="article,table"
        ></v-skeleton-loader>

        <template v-else-if="finalSummary">
          <div class="summary-content">
            <div v-html="formattedSummary"></div>
          </div>

          <v-divider class="my-4"></v-divider>

          <v-row>
            <v-col cols="12" md="6">
              <v-card variant="outlined" class="score-card">
                <v-card-title class="text-h6">
                  <v-icon start icon="mdi-file-document-outline"></v-icon>
                  阅读测试成绩
                </v-card-title>
                <v-card-text>
                  <v-row align="center">
                    <v-col cols="6">
                      <h4 class="text-subtitle-2">前测分数</h4>
                      <div class="text-h4">{{ userProfile.post_score || 0 }}<span class="text-subtitle-1">/100</span></div>
                    </v-col>
                    <v-col cols="6">
                      <h4 class="text-subtitle-2">后测分数</h4>
                      <div class="text-h4">{{ userProfile.after_score || 0 }}<span class="text-subtitle-1">/100</span></div>
                    </v-col>
                  </v-row>

                  <v-progress-linear
                    :model-value="calculateImprovement('score')"
                    color="success"
                    height="20"
                    striped
                    class="mt-4"
                  >
                    <template v-slot:default="{ value }">
                      <span>提高了 {{ Math.round(value) }}%</span>
                    </template>
                  </v-progress-linear>
                </v-card-text>
              </v-card>
            </v-col>

            <v-col cols="12" md="6">
              <v-card variant="outlined" class="score-card">
                <v-card-title class="text-h6">
                  <v-icon start icon="mdi-clipboard-list-outline"></v-icon>
                  阅读策略水平
                </v-card-title>
                <v-card-text>
                  <v-row align="center">
                    <v-col cols="6">
                      <h4 class="text-subtitle-2">前测分数</h4>
                      <div class="text-h4">{{ userProfile.post_strategies_score || 0 }}<span class="text-subtitle-1">/75</span></div>
                    </v-col>
                    <v-col cols="6">
                      <h4 class="text-subtitle-2">后测分数</h4>
                      <div class="text-h4">{{ userProfile.after_strategies_score || 0 }}<span class="text-subtitle-1">/75</span></div>
                    </v-col>
                  </v-row>

                  <v-progress-linear
                    :model-value="calculateImprovement('strategy')"
                    color="info"
                    height="20"
                    striped
                    class="mt-4"
                  >
                    <template v-slot:default="{ value }">
                      <span>提高了 {{ Math.round(value) }}%</span>
                    </template>
                  </v-progress-linear>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>

          <v-card variant="outlined" class="mt-4">
            <v-card-title class="text-h6">
              <v-icon start icon="mdi-certificate-outline"></v-icon>
              英语阅读水平评定
            </v-card-title>
            <v-card-text>
              <v-row>
                <v-col cols="12" md="4">
                  <v-card variant="flat" class="text-center pa-4">
                    <h4 class="text-subtitle-2">前测水平</h4>
                    <v-chip
                      size="large"
                      :color="getLevelColor(getScoreLevel(userProfile.post_score || 0))"
                      class="mt-2"
                    >
                      {{ getScoreLevel(userProfile.post_score || 0) }}
                    </v-chip>
                  </v-card>
                </v-col>

                <v-col cols="12" md="4">
                  <v-card variant="flat" class="text-center pa-4">
                    <h4 class="text-subtitle-2">后测水平</h4>
                    <v-chip
                      size="large"
                      :color="getLevelColor(getScoreLevel(userProfile.after_score || 0))"
                      class="mt-2"
                    >
                      {{ getScoreLevel(userProfile.after_score || 0) }}
                    </v-chip>
                  </v-card>
                </v-col>

                <v-col cols="12" md="4">
                  <v-card variant="flat" class="text-center pa-4">
                    <h4 class="text-subtitle-2">策略掌握水平</h4>
                    <v-chip
                      size="large"
                      :color="getLevelColor(getStrategyLevel(userProfile.after_strategies_score || 0))"
                      class="mt-2"
                    >
                      {{ getStrategyLevel(userProfile.after_strategies_score || 0) }}
                    </v-chip>
                  </v-card>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </template>
      </v-card-text>

      <v-divider></v-divider>

      <v-card-actions>
        <v-btn
          color="error"
          variant="text"
          @click="restartSystem"
        >
          <v-icon start icon="mdi-restart"></v-icon>
          重新开始
        </v-btn>

        <v-spacer></v-spacer>

        <v-btn
          v-if="finalSummary"
          color="primary"
          variant="flat"
        >
          完成学习
          <v-icon end icon="mdi-check"></v-icon>
        </v-btn>
      </v-card-actions>
    </v-card>

    <!-- 重启确认对话框 -->
    <v-dialog v-model="confirmRestartDialog" max-width="400">
      <v-card>
        <v-card-title>确认重新开始</v-card-title>
        <v-card-text>
          您确定要重新开始整个学习过程吗？此操作将清除您的学习进度，但保留您的用户信息和成绩记录。
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="confirmRestartDialog = false">取消</v-btn>
          <v-btn color="error" @click="confirmRestart">确认</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';
import { marked } from 'marked';

export default {
  name: 'Summary',

  setup() {
    const store = useStore();
    const router = useRouter();

    // 用户信息
    const userProfile = computed(() => store.state.userProfile || {});

    // 学习总结
    const finalSummary = computed(() => store.state.finalSummary);
    const loading = computed(() => store.state.loading);

    // 重启确认对话框
    const confirmRestartDialog = ref(false);

    // 格式化总结内容
    const formattedSummary = computed(() => {
      return finalSummary.value ? marked(finalSummary.value) : '';
    });

    // 加载学习总结
    const loadFinalSummary = async () => {
      // 确保已获取用户信息
      if (!userProfile.value.name) {
        await store.dispatch('fetchUserProfile');
      }

      await store.dispatch('fetchFinalSummary');
    };

    // 计算提高百分比
    const calculateImprovement = (type) => {
      if (type === 'score') {
        const preScore = parseInt(userProfile.value.post_score) || 0;
        const postScore = parseInt(userProfile.value.after_score) || 0;

        if (preScore === 0) return 0;
        return ((postScore - preScore) / preScore) * 100;
      } else {
        const preScore = parseInt(userProfile.value.post_strategies_score) || 0;
        const postScore = parseInt(userProfile.value.after_strategies_score) || 0;

        if (preScore === 0) return 0;
        return ((postScore - preScore) / preScore) * 100;
      }
    };

    // 获取阅读水平
    const getScoreLevel = (score) => {
      if (score < 60) return '初级';
      if (score < 80) return '中级';
      return '高级';
    };

    // 获取策略水平
    const getStrategyLevel = (score) => {
      if (score <= 25) return '初级';
      if (score <= 50) return '中级';
      return '高级';
    };

    // 获取水平对应的颜色
    const getLevelColor = (level) => {
      if (level === '初级') return 'warning';
      if (level === '中级') return 'info';
      return 'success';
    };

    // 重启系统
    const restartSystem = () => {
      confirmRestartDialog.value = true;
    };

    // 确认重启
    const confirmRestart = () => {
      // 保留用户名，但清除其他状态
      const userName = store.state.userName;

      // 重置阶段
      store.dispatch('setCurrentPhase', 'planning');

      // 清除缓存的状态
      store.commit('SET_PROFILE_ANALYSIS', '');
      store.commit('SET_WRONG_ANSWERS_ANALYSIS', '');
      store.commit('SET_STRATEGY_SUGGESTIONS', '');

      confirmRestartDialog.value = false;

      // 跳转到系统介绍页
      router.push({ name: 'Introduction' });
    };

    // 组件挂载时，获取用户信息和学习总结
    onMounted(async () => {
      await store.dispatch('fetchUserProfile');

      // 如果有学习总结，直接显示
      if (!finalSummary.value) {
        // 检查是否已完成后测
        if (userProfile.value.after_score && userProfile.value.after_strategies_score) {
          loadFinalSummary();
        }
      }
    });

    return {
      userProfile,
      finalSummary,
      loading,
      formattedSummary,
      confirmRestartDialog,
      loadFinalSummary,
      calculateImprovement,
      getScoreLevel,
      getStrategyLevel,
      getLevelColor,
      restartSystem,
      confirmRestart
    };
  }
};
</script>

<style scoped>
.summary {
  max-width: 100%;
}

.summary-content {
  background-color: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 24px;
  max-height: 400px;
  overflow-y: auto;
}

.score-card {
  height: 100%;
}
</style>