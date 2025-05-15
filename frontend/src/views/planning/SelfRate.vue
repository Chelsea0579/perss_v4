<template>
  <div class="self-rate">
    <v-card>
      <v-card-title class="text-h5 primary--text">
        <v-icon start icon="mdi-checkbox-marked-circle-outline"></v-icon>
        英语阅读能力自评
      </v-card-title>

      <v-card-text>
        <p class="text-body-1 mb-4">
          请根据您的实际情况，为每项描述选择最符合的选项。您的选择将帮助我们更好地了解您的英语阅读水平和需求。
        </p>

        <div v-if="selfRateItems.length === 0" class="text-center py-4">
          <v-progress-circular indeterminate color="primary"></v-progress-circular>
          <div class="mt-2">加载中...</div>
        </div>

        <template v-else>
          <v-table>
            <thead>
              <tr>
                <th>序号</th>
                <th>描述</th>
                <th class="text-center" v-for="i in 5" :key="`header-${i}`">
                  {{ getColumnHeader(i) }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in currentItems" :key="`item-${item.id}`">
                <td>{{ startIndex + index + 1 }}</td>
                <td>{{ item.内容 }}</td>
                <td class="text-center" v-for="i in 5" :key="`option-${i}`">
                  <v-radio-group
                    v-model="answers[startIndex + index]"
                    inline
                    hide-details
                    class="ma-0 pa-0 justify-center"
                  >
                    <v-radio :value="i" :disabled="completed"></v-radio>
                  </v-radio-group>
                </td>
              </tr>
            </tbody>
          </v-table>

          <div class="text-center mt-4">
            <v-pagination
              v-model="currentPage"
              :length="totalPages"
              :total-visible="7"
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
            您还有 {{ unansweredCount }} 个项目未评估。请确保所有项目都已选择后再继续。
          </v-alert>
        </template>
      </v-card-text>

      <v-divider></v-divider>

      <v-card-actions>
        <v-btn
          v-if="!completed"
          variant="outlined"
          color="error"
          @click="resetForm"
        >
          重置
        </v-btn>

        <v-spacer></v-spacer>

        <v-btn
          color="primary"
          variant="flat"
          :disabled="hasUnansweredQuestions"
          :loading="loading"
          @click="submitForm"
        >
          继续
          <v-icon end icon="mdi-arrow-right"></v-icon>
        </v-btn>
      </v-card-actions>
    </v-card>
  </div>
</template>

<script>
import { computed, ref, onMounted, watch } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';

export default {
  name: 'SelfRate',

  setup() {
    const store = useStore();
    const router = useRouter();

    // 自评量表数据
    const selfRateItems = computed(() => store.state.selfRateItems);
    const answers = ref([]);
    const completed = ref(false);

    // 分页
    const itemsPerPage = 10;
    const currentPage = ref(1);

    // 计算总页数
    const totalPages = computed(() => {
      return Math.ceil(selfRateItems.value.length / itemsPerPage);
    });

    // 计算当前页的项目
    const currentItems = computed(() => {
      const start = (currentPage.value - 1) * itemsPerPage;
      const end = start + itemsPerPage;
      return selfRateItems.value.slice(start, end);
    });

    // 当前页起始索引
    const startIndex = computed(() => {
      return (currentPage.value - 1) * itemsPerPage;
    });

    // 获取列标题
    const getColumnHeader = (index) => {
      const headers = {
        1: '完全不符合',
        2: '有些不符合',
        3: '有些符合',
        4: '比较符合',
        5: '非常符合'
      };

      return headers[index] || '';
    };

    // 计算未回答的问题数量
    const unansweredCount = computed(() => {
      return answers.value.filter(a => !a).length;
    });

    // 是否有未回答的问题
    const hasUnansweredQuestions = computed(() => {
      return unansweredCount.value > 0;
    });

    // 重置表单
    const resetForm = () => {
      answers.value = new Array(selfRateItems.value.length).fill(null);
    };

    // 提交表单
    const submitForm = () => {
      if (hasUnansweredQuestions.value) {
        // 如果有未回答的问题，切换到第一个未回答的问题所在页
        const firstUnansweredIndex = answers.value.findIndex(a => !a);
        if (firstUnansweredIndex !== -1) {
          currentPage.value = Math.floor(firstUnansweredIndex / itemsPerPage) + 1;
        }
        return;
      }

      // 标记为已完成
      completed.value = true;

      // 导航到用户画像页面
      router.push({ name: 'UserProfile' });
    };

    // 加载自评量表
    const loadSelfRateItems = async () => {
      await store.dispatch('fetchSelfRateItems');

      // 初始化答案数组
      if (answers.value.length === 0) {
        answers.value = new Array(selfRateItems.value.length).fill(null);
      }
    };

    // 组件挂载时加载数据
    onMounted(() => {
      loadSelfRateItems();
    });

    return {
      selfRateItems,
      answers,
      completed,
      currentPage,
      totalPages,
      currentItems,
      startIndex,
      unansweredCount,
      hasUnansweredQuestions,
      loading: computed(() => store.state.loading),
      getColumnHeader,
      resetForm,
      submitForm
    };
  }
};
</script>

<style scoped>
.self-rate {
  max-width: 100%;
}

.v-table {
  border: 1px solid #e0e0e0;
}

.v-table th, .v-table td {
  padding: 8px;
  vertical-align: middle;
}

.v-table th:nth-child(2), .v-table td:nth-child(2) {
  text-align: left;
  min-width: 300px;
}

.v-table th:not(:nth-child(2)), .v-table td:not(:nth-child(2)) {
  width: 80px;
}
</style>