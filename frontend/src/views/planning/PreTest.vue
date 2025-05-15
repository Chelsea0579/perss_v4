<template>
  <div class="pre-test">
    <v-card>
      <v-card-title class="text-h5 primary--text d-flex align-center">
        <v-icon start icon="mdi-file-document-outline"></v-icon>
        阅读前测 - 试卷 {{ id }}
        <v-chip class="ml-auto" color="warning" v-if="!examCompleted">进行中</v-chip>
        <v-chip class="ml-auto" color="success" v-else>已完成</v-chip>
      </v-card-title>

      <v-card-text v-if="!examData">
        <v-skeleton-loader type="article"></v-skeleton-loader>
      </v-card-text>

      <template v-else>
        <v-card-text class="pb-0">
          <div class="d-flex align-center mb-4">
            <div>
              <h3 class="text-subtitle-1">剩余时间：</h3>
              <div class="text-h6" :class="{'red--text': timeLeft < 300}">
                {{ formatTime(timeLeft) }}
              </div>
            </div>

            <v-spacer></v-spacer>

            <div class="text-right">
              <h3 class="text-subtitle-1">得分：</h3>
              <div class="text-h6">{{ examCompleted ? score : '-' }}/100</div>
            </div>
          </div>

          <v-divider class="mb-4"></v-divider>

          <div class="reading-passage">
            <h3 class="text-h6 mb-3">阅读原文</h3>
            <div class="reading-content">{{ examData.content }}</div>
          </div>
        </v-card-text>

        <v-card-text>
          <h3 class="text-h6 mb-3">题目（共{{ examData.questions.length }}题，每题{{ questionScore }}分）</h3>

          <div
            v-for="(question, index) in examData.questions"
            :key="`question-${index}`"
            class="question-item mb-6"
          >
            <div class="question-header d-flex align-center mb-2">
              <h4 class="text-subtitle-1">问题 {{ index + 1 }}</h4>
              <v-spacer></v-spacer>
              <v-chip
                v-if="examCompleted"
                :color="isAnswerCorrect(index) ? 'success' : 'error'"
                size="small"
              >
                {{ isAnswerCorrect(index) ? '正确' : '错误' }}
              </v-chip>
            </div>

            <div class="question-content mb-2">{{ question.question }}</div>

            <div v-if="!examCompleted">
              <v-text-field
                v-model="answers[index]"
                label="请输入您的答案"
                variant="outlined"
                density="comfortable"
                :disabled="examCompleted"
              ></v-text-field>
            </div>

            <div v-else class="answer-section">
              <div class="d-flex">
                <div class="text-subtitle-2 mr-2">您的答案：</div>
                <div :class="{'text-success': isAnswerCorrect(index), 'text-error': !isAnswerCorrect(index)}">
                  {{ answers[index] || '未作答' }}
                </div>
              </div>

              <div class="d-flex mt-2">
                <div class="text-subtitle-2 mr-2">正确答案：</div>
                <div class="text-success">{{ question.answer }}</div>
              </div>
            </div>
          </div>
        </v-card-text>

        <v-divider></v-divider>

        <v-card-actions>
          <v-btn
            v-if="id == 1 && !examCompleted"
            variant="outlined"
            color="error"
            @click="confirmReset"
          >
            重置
          </v-btn>

          <v-spacer></v-spacer>

          <v-btn
            v-if="!examCompleted"
            color="primary"
            variant="flat"
            :loading="loading"
            :disabled="!canSubmit"
            @click="submitExam"
          >
            提交
          </v-btn>

          <v-btn
            v-else-if="id == 1"
            color="primary"
            variant="flat"
            :to="{ name: 'PreTest', params: { id: 2 } }"
          >
            下一份试卷
            <v-icon end icon="mdi-arrow-right"></v-icon>
          </v-btn>

          <v-btn
            v-else
            color="primary"
            variant="flat"
            :to="{ name: 'StrategyPreTest' }"
          >
            继续
            <v-icon end icon="mdi-arrow-right"></v-icon>
          </v-btn>
        </v-card-actions>
      </template>
    </v-card>

    <!-- 确认对话框 -->
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
          <p v-if="unansweredCount > 0" class="text-warning">
            您还有 {{ unansweredCount }} 题未作答。
          </p>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn variant="text" @click="confirmSubmitDialog = false">取消</v-btn>
          <v-btn color="primary" @click="confirmSubmit">确认提交</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';

export default {
  name: 'PreTest',

  props: {
    id: {
      type: [String, Number],
      required: true
    }
  },

  setup(props) {
    const store = useStore();
    const router = useRouter();

    // 考试数据
    const examId = computed(() => {
      const parsedId = parseInt(props.id);
      return isNaN(parsedId) ? 1 : parsedId; // Default to 1 if invalid
    });
    const examData = ref(null);
    const answers = ref([]);
    const examCompleted = ref(false);
    const score = ref(0);
    const questionScore = ref(10); // 每题10分
    const wrongQuestions = ref([]);

    // 对话框状态
    const confirmResetDialog = ref(false);
    const confirmSubmitDialog = ref(false);

    // 计时器
    const timeLeft = ref(1800); // 30分钟 = 1800秒
    let timer = null;

    // 读取考试数据
    const loadExamData = async () => {
      const response = await store.dispatch('fetchExam', examId.value);

      if (response) {
        examData.value = response;
        // 初始化答案数组
        answers.value = new Array(response.questions.length).fill('');

        // 开始计时
        startTimer();
      }
    };

    // 开始计时
    const startTimer = () => {
      if (timer) clearInterval(timer);

      timer = setInterval(() => {
        if (timeLeft.value > 0) {
          timeLeft.value--;
        } else {
          // 时间到，自动提交
          clearInterval(timer);
          if (!examCompleted.value) {
            submitExam();
          }
        }
      }, 1000);
    };

    // 格式化时间
    const formatTime = (seconds) => {
      const minutes = Math.floor(seconds / 60);
      const remainingSeconds = seconds % 60;
      return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
    };

    // 计算未作答题目数量
    const unansweredCount = computed(() => {
      return answers.value.filter(answer => !answer.trim()).length;
    });

    // 判断是否可以提交
    const canSubmit = computed(() => {
      return answers.value.some(answer => answer.trim() !== '');
    });

    // 确认重置对话框
    const confirmReset = () => {
      confirmResetDialog.value = true;
    };

    // 重置答案
    const resetAnswers = () => {
      answers.value = new Array(examData.value.questions.length).fill('');
      confirmResetDialog.value = false;
    };

    // 提交前确认
    const submitExam = () => {
      confirmSubmitDialog.value = true;
    };

    // 确认提交
    const confirmSubmit = async () => {
      confirmSubmitDialog.value = false;

      // 计算得分
      let earnedScore = 0;
      wrongQuestions.value = [];

      examData.value.questions.forEach((question, index) => {
        const userAnswer = answers.value[index].trim().toLowerCase();
        const correctAnswer = question.answer.trim().toLowerCase();

        if (userAnswer === correctAnswer) {
          earnedScore += questionScore.value;
        } else {
          // 记录错题，格式：examId-questionNumber
          wrongQuestions.value.push(`${examId.value}-${index + 1}`);
        }
      });

      score.value = earnedScore;
      examCompleted.value = true;

      // 保存结果到服务器
      await store.dispatch('submitExamResult', {
        examId: examId.value,
        score: score.value,
        wrongQuestions: wrongQuestions.value
      });

      // 停止计时器
      clearInterval(timer);
    };

    // 判断答案是否正确
    const isAnswerCorrect = (index) => {
      const userAnswer = answers.value[index].trim().toLowerCase();
      const correctAnswer = examData.value.questions[index].answer.trim().toLowerCase();
      return userAnswer === correctAnswer;
    };

    // 组件挂载时
    onMounted(() => {
      loadExamData();
    });

    // 组件卸载前清除计时器
    onBeforeUnmount(() => {
      if (timer) {
        clearInterval(timer);
      }
    });

    // 监听路由变化，重新加载考试数据
    watch(() => props.id, (newId) => {
      // examId is already computed, no need to set it
      examCompleted.value = false;
      score.value = 0;
      timeLeft.value = 1800;
      loadExamData();
    });

    return {
      examId,
      examData,
      answers,
      examCompleted,
      score,
      questionScore,
      wrongQuestions,
      timeLeft,
      confirmResetDialog,
      confirmSubmitDialog,
      unansweredCount,
      canSubmit,
      formatTime,
      confirmReset,
      resetAnswers,
      submitExam,
      confirmSubmit,
      isAnswerCorrect,
      loading: computed(() => store.state.loading)
    };
  }
};
</script>

<style scoped>
.pre-test {
  max-width: 100%;
}

.reading-passage {
  margin-bottom: 24px;
}

.reading-content {
  background-color: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
  max-height: 300px;
  overflow-y: auto;
  white-space: pre-line;
  line-height: 1.6;
}

.question-item {
  border-left: 3px solid #e0e0e0;
  padding-left: 16px;
}

.text-success {
  color: #4caf50;
}

.text-error {
  color: #f44336;
}

.text-warning {
  color: #ff9800;
}
</style>