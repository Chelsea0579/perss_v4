<template>
  <div class="exam-question">
    <div class="question-container">
      <div class="question-header d-flex align-center">
        <h4 class="text-subtitle-1">问题 {{ number }}</h4>
        <v-spacer></v-spacer>
        <v-chip
          v-if="showResult"
          :color="isCorrect ? 'success' : 'error'"
          size="small"
        >
          {{ isCorrect ? '正确' : '错误' }}
        </v-chip>
      </div>

      <div class="question-content">{{ question }}</div>

      <div v-if="!showResult">
        <v-text-field
          v-model="userAnswer"
          label="请输入您的答案"
          variant="outlined"
          density="comfortable"
          :disabled="disabled"
          @update:model-value="updateAnswer"
        ></v-text-field>
      </div>

      <div v-else class="answer-section">
        <div class="d-flex">
          <div class="text-subtitle-2 mr-2">您的答案：</div>
          <div :class="{'text-success': isCorrect, 'text-error': !isCorrect}">
            {{ userAnswer || '未作答' }}
          </div>
        </div>

        <div class="d-flex mt-2">
          <div class="text-subtitle-2 mr-2">正确答案：</div>
          <div class="text-success">{{ answer }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue';

export default {
  name: 'ExamQuestion',

  props: {
    number: {
      type: Number,
      required: true
    },
    question: {
      type: String,
      required: true
    },
    answer: {
      type: String,
      required: true
    },
    initialValue: {
      type: String,
      default: ''
    },
    showResult: {
      type: Boolean,
      default: false
    },
    disabled: {
      type: Boolean,
      default: false
    }
  },

  emits: ['update:answer'],

  setup(props, { emit }) {
    const userAnswer = ref(props.initialValue);

    // 判断答案是否正确
    const isCorrect = computed(() => {
      const normalizedUserAnswer = userAnswer.value.trim().toLowerCase();
      const normalizedCorrectAnswer = props.answer.trim().toLowerCase();
      return normalizedUserAnswer === normalizedCorrectAnswer;
    });

    // 更新答案
    const updateAnswer = () => {
      emit('update:answer', userAnswer.value);
    };

    // 监听初始值变化
    watch(() => props.initialValue, (newValue) => {
      userAnswer.value = newValue;
    });

    return {
      userAnswer,
      isCorrect,
      updateAnswer
    };
  }
};
</script>

<style scoped>
.question-container {
  border-left: 3px solid #e0e0e0;
  padding-left: 16px;
  margin-bottom: 24px;
}

.question-header {
  margin-bottom: 8px;
}

.question-content {
  margin-bottom: 16px;
  line-height: 1.5;
}

.text-success {
  color: #4caf50;
}

.text-error {
  color: #f44336;
}
</style>