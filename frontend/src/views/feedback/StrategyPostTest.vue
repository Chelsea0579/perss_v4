<template>
  <div class="strategy-post-test">
    <v-card>
      <v-card-title class="text-h5 primary--text">
        <v-icon start icon="mdi-clipboard-check-outline"></v-icon>
        阅读策略问卷调查（后测）
      </v-card-title>

      <v-card-text>
        <p class="text-body-1 mb-4">
          请根据您在学习过程后对各种英语阅读策略的了解和掌握情况，为每一项策略选择最符合的选项。
        </p>

        <div v-if="strategyItems.length === 0" class="text-center py-4">
          <v-progress-circular indeterminate color="primary"></v-progress-circular>
          <div class="mt-2">加载中...</div>
        </div>

        <template v-else>
          <v-alert
            type="info"
            variant="tonal"
            border="start"
            icon="mdi-information-outline"
            class="mb-4"
          >
            <p class="mb-0">请为每个策略选择一个选项：</p>
            <ul class="mt-2 mb-0">
              <li>1 - 我从未听说过这个策略</li>
              <li>2 - 我听说过这个策略，但不知道它的含义</li>
              <li>3 - 我听说过这个策略，并且我认为我知道它的含义</li>
              <li>4 - 我了解这个策略，并且我可以解释如何以及何时使用它</li>
              <li>5 - 我非常了解这个策略，并且在阅读时经常使用它</li>
            </ul>
          </v-alert>

          <v-expansion-panels v-model="openPanel">
            <v-expansion-panel
              v-for="(item, index) in strategyItems"
              :key="`strategy-${item.id}`"
              :title="`策略 ${index + 1}`"
              :text="item.content"
            >
              <template v-slot:text>
                <div class="strategy-content mb-4">{{ item.content }}</div>

                <v-radio-group
                  v-model="answers[index]"
                  inline
                  hide-details
                  class="strategy-options"
                >
                  <v-radio
                    v-for="option in 5"
                    :key="`option-${option}`"
                    :label="`${option}`"
                    :value="option"
                    :disabled="completed"
                  ></v-radio>
                </v-radio-group>
              </template>
            </v-expansion-panel>
          </v-expansion-panels>

          <div class="text-center mt-4">
            <v-pagination
              v-model="currentPage"
              :length="totalPages"
              :total-visible="7"
              @update:model-value="changePage"
            ></v-pagination>
          </div>

          <v-alert
            v-if="hasUnansweredQuestions"
            type="warning"
            variant="tonal"
            border="start"
            icon="mdi-alert-outline"
            class="mt-4"
          >
            您还有 {{ unansweredCount }} 个策略未评估。请确保完成所有项目后再提交。
          </v-alert>

          <v-alert
            v-if="completed"
            type="success"
            variant="tonal"
            border="start"
            icon="mdi-check-circle-outline"
            class="mt-4"
          >
            <div class="d-flex align-center">
              <div>
                <p class="mb-1">问卷已完成！您的阅读策略评分为：</p>
                <p class="text-h5 mb-0">{{ totalScore }}/75</p>
              </div>
              <v-spacer></v-spacer>
              <v-chip
                :color="getScoreColor(totalScore)"
                size="large"
              >
                {{ getScoreLevel(totalScore) }}
              </v-chip>
            </div>
          </v-alert>
        </template>
      </v-card-text>

      <v-divider></v-divider>

      <v-card-actions>
        <v-btn
          v-if="!completed"
          variant="outlined"
          color="error"
          @click="confirmReset"
        >
          重置
        </v-btn>

        <v-spacer></v-spacer>

        <v-btn
          v-if="!completed"
          color="primary"
          variant="flat"
          :loading="loading"
          :disabled="hasUnansweredQuestions"
          @click="confirmSubmit"
        >
          提交
        </v-btn>

        <v-btn
          v-else
          color="primary"
          variant="flat"
          :to="{ name: 'Summary' }"
        >
          查看学习总结
          <v-icon end icon="mdi-arrow-right"></v-icon>
        </v-btn>
      </v-card-actions>
    </v-card>

    <!-- 确认重置对话框 -->
    <v-dialog v-model="confirmResetDialog" max-width="400">
      <v-card>
        <v-card-title>确认重置</v-card-title>
        <v-card-text>
          您确定要重置所有答案吗？此操作不可撤销。
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="confirmResetDialog = false">取消</v-btn>
          <v-btn color="error" @click="resetAnswers">确认</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- 提交确认对话框 -->
    <v-dialog v-model="confirmSubmitDialog" max-width="400">
      <v-card>
        <v-card-title>确认提交</v-card-title>
        <v-card-text>
          <p>您确定要提交答案吗？提交后将无法修改。</p>
          <p v-if="hasUnansweredQuestions" class="text-warning">
            您还有 {{ unansweredCount }} 个策略未评估。
          </p>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="confirmSubmitDialog = false">取消</v-btn>
          <v-btn
            color="primary"
            @click="submitAnswers"
            :disabled="hasUnansweredQuestions"
          >
            确认提交
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';

export default {
  name: 'StrategyPostTest',

  setup() {
    const store = useStore();
    const router = useRouter();

    // 策略列表
    const strategyItems = computed(() => store.state.strategyItems);
    const answers = ref([]);
    const completed = ref(false);
    const totalScore = ref(0);

    // 分页
    const itemsPerPage = 5;
    const currentPage = ref(1);
    const openPanel = ref([0]); // 默认展开第一个面板

    // 对话框状态
    const confirmResetDialog = ref(false);
    const confirmSubmitDialog = ref(false);

    // 计算总页数
    const totalPages = computed(() => {
      return Math.ceil(strategyItems.value.length / itemsPerPage);
    });

    // 未答题数量
    const unansweredCount = computed(() => {
      return answers.value.filter(answer => !answer).length;
    });

    // 是否有未答题
    const hasUnansweredQuestions = computed(() => {
      return unansweredCount.value > 0;
    });

    // 加载策略列表
    const loadStrategies = async () => {
      if (strategyItems.value.length === 0) {
        await store.dispatch('fetchStrategies');
        // 初始化答案数组
        answers.value = new Array(strategyItems.value.length).fill(null);
      }
    };

    // 切换页面
    const changePage = (page) => {
      currentPage.value = page;
      // 计算当前页的第一个项目索引
      const startIndex = (page - 1) * itemsPerPage;
      // 默认展开当前页的第一个面板
      openPanel.value = [startIndex % itemsPerPage];
    };

    // 确认重置
    const confirmReset = () => {
      confirmResetDialog.value = true;
    };

    // 重置答案
    const resetAnswers = () => {
      answers.value = new Array(strategyItems.value.length).fill(null);
      confirmResetDialog.value = false;
    };

    // 确认提交
    const confirmSubmit = () => {
      if (hasUnansweredQuestions.value) {
        // 如果有未回答的问题，切换到第一个未回答的问题所在页
        const firstUnansweredIndex = answers.value.findIndex(answer => !answer);
        if (firstUnansweredIndex !== -1) {
          const pageNumber = Math.floor(firstUnansweredIndex / itemsPerPage) + 1;
          currentPage.value = pageNumber;
          // 展开未回答的问题面板
          openPanel.value = [firstUnansweredIndex % itemsPerPage];
        }
      } else {
        confirmSubmitDialog.value = true;
      }
    };

    // 提交答案
    const submitAnswers = async () => {
      // 计算总分
      const score = answers.value.reduce((total, answer) => total + (answer || 0), 0);
      totalScore.value = score;
      completed.value = true;

      // 保存结果到服务器
      await store.dispatch('submitStrategyResult', {
        score: score,
        isPreTest: false
      });

      confirmSubmitDialog.value = false;
    };

    // 获取得分颜色
    const getScoreColor = (score) => {
      if (score <= 25) return 'error';
      if (score <= 50) return 'warning';
      return 'success';
    };

    // 获取得分等级
    const getScoreLevel = (score) => {
      if (score <= 25) return '初级';
      if (score <= 50) return '中级';
      return '高级';
    };

    // 组件挂载时加载策略列表
    onMounted(() => {
      loadStrategies();
    });

    return {
      strategyItems,
      answers,
      completed,
      totalScore,
      currentPage,
      totalPages,
      openPanel,
      confirmResetDialog,
      confirmSubmitDialog,
      unansweredCount,
      hasUnansweredQuestions,
      changePage,
      confirmReset,
      resetAnswers,
      confirmSubmit,
      submitAnswers,
      getScoreColor,
      getScoreLevel,
      loading: computed(() => store.state.loading)
    };
  }
};
</script>

<style scoped>
.strategy-post-test {
  max-width: 100%;
}

.strategy-content {
  background-color: #f8f9fa;
  padding: 12px;
  border-radius: 8px;
  font-style: italic;
}

.strategy-options {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
}

.text-warning {
  color: #ff9800;
}
</style>