<template>
  <div class="strategy-item">
    <v-card variant="outlined" class="mb-3">
      <v-card-title>
        <div class="d-flex align-center">
          <span class="text-subtitle-1">{{ title }}</span>
          <v-spacer></v-spacer>
          <v-chip
            v-if="showLevel"
            :color="getLevelColor()"
            size="small"
          >
            {{ level }}
          </v-chip>
        </div>
      </v-card-title>

      <v-card-text>
        <div class="strategy-content">{{ content }}</div>

        <div v-if="detail" class="strategy-detail mt-3">
          <v-alert
            type="info"
            variant="tonal"
            density="compact"
          >
            {{ detail }}
          </v-alert>
        </div>

        <div v-if="!hideOptions" class="strategy-options mt-3">
          <v-radio-group
            v-model="selectedOption"
            inline
            hide-details
            @update:model-value="updateValue"
            :disabled="disabled"
          >
            <v-radio
              v-for="option in options"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            ></v-radio>
          </v-radio-group>
        </div>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue';

export default {
  name: 'StrategyItem',

  props: {
    id: {
      type: [Number, String],
      required: true
    },
    title: {
      type: String,
      default: ''
    },
    content: {
      type: String,
      required: true
    },
    detail: {
      type: String,
      default: ''
    },
    options: {
      type: Array,
      default: () => [
        { value: 1, label: '1 - 我从未听说过这个策略' },
        { value: 2, label: '2 - 我听说过这个策略，但不知道它的含义' },
        { value: 3, label: '3 - 我听说过这个策略，并且我认为我知道它的含义' },
        { value: 4, label: '4 - 我了解这个策略，并且我可以解释如何以及何时使用它' },
        { value: 5, label: '5 - 我非常了解这个策略，并且在阅读时经常使用它' }
      ]
    },
    modelValue: {
      type: Number,
      default: null
    },
    hideOptions: {
      type: Boolean,
      default: false
    },
    disabled: {
      type: Boolean,
      default: false
    },
    showLevel: {
      type: Boolean,
      default: false
    },
    level: {
      type: String,
      default: ''
    }
  },

  emits: ['update:modelValue'],

  setup(props, { emit }) {
    const selectedOption = ref(props.modelValue);

    // 监听值变化
    watch(() => props.modelValue, (newValue) => {
      selectedOption.value = newValue;
    });

    // 更新值
    const updateValue = () => {
      emit('update:modelValue', selectedOption.value);
    };

    // 获取等级颜色
    const getLevelColor = () => {
      const levels = {
        '初级': 'error',
        '中级': 'warning',
        '高级': 'success'
      };

      return levels[props.level] || 'info';
    };

    return {
      selectedOption,
      updateValue,
      getLevelColor
    };
  }
};
</script>

<style scoped>
.strategy-content {
  font-style: italic;
  line-height: 1.5;
}

.strategy-detail {
  font-size: 0.9rem;
}

.strategy-options {
  display: flex;
  justify-content: space-between;
}
</style>