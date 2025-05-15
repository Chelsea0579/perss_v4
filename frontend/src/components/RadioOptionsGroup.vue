<template>
  <div class="radio-options-group">
    <v-radio-group
      v-model="selected"
      :inline="inline"
      :hide-details="hideDetails"
      @update:model-value="updateValue"
      :disabled="disabled"
    >
      <template v-if="label">
        <v-label>{{ label }}</v-label>
      </template>

      <v-radio
        v-for="option in options"
        :key="option.value"
        :label="option.label"
        :value="option.value"
      ></v-radio>
    </v-radio-group>
  </div>
</template>

<script>
import { ref, watch } from 'vue';

export default {
  name: 'RadioOptionsGroup',

  props: {
    modelValue: {
      type: [String, Number, Boolean],
      default: null
    },
    options: {
      type: Array,
      required: true
    },
    label: {
      type: String,
      default: ''
    },
    inline: {
      type: Boolean,
      default: false
    },
    hideDetails: {
      type: Boolean,
      default: false
    },
    disabled: {
      type: Boolean,
      default: false
    }
  },

  emits: ['update:modelValue'],

  setup(props, { emit }) {
    const selected = ref(props.modelValue);

    // 监听值变化
    watch(() => props.modelValue, (newValue) => {
      selected.value = newValue;
    });

    // 更新值
    const updateValue = () => {
      emit('update:modelValue', selected.value);
    };

    return {
      selected,
      updateValue
    };
  }
};
</script>

<style scoped>
.radio-options-group {
  margin-bottom: 16px;
}
</style>