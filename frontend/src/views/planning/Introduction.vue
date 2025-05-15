<template>
  <div class="introduction">
    <v-card class="mb-4">
      <v-card-title class="text-h5 primary--text">
        欢迎使用个性化英语阅读支持系统
      </v-card-title>

      <v-card-text>
        <div v-if="introduction" v-html="formattedIntroduction"></div>
        <v-skeleton-loader v-else type="text" />
      </v-card-text>

      <v-divider></v-divider>

      <v-card-text>
        <h3 class="text-subtitle-1 mb-2">系统特点</h3>
        <v-row>
          <v-col cols="12" md="4">
            <v-card variant="outlined" height="100%">
              <v-card-title class="text-h6 primary--text">
                <v-icon icon="mdi-clipboard-outline" class="mr-2"></v-icon>
                计划阶段
              </v-card-title>
              <v-card-text>
                通过自评量表、用户画像采集和前测，了解您的英语阅读水平和阅读策略使用情况，为后续的个性化学习提供基础。
              </v-card-text>
            </v-card>
          </v-col>

          <v-col cols="12" md="4">
            <v-card variant="outlined" height="100%">
              <v-card-title class="text-h6 primary--text">
                <v-icon icon="mdi-book-open-variant" class="mr-2"></v-icon>
                执行阶段
              </v-card-title>
              <v-card-text>
                与AI助手互动，获取个性化的阅读策略指导和错题解析，提升英语阅读能力和策略意识。
              </v-card-text>
            </v-card>
          </v-col>

          <v-col cols="12" md="4">
            <v-card variant="outlined" height="100%">
              <v-card-title class="text-h6 primary--text">
                <v-icon icon="mdi-chart-line" class="mr-2"></v-icon>
                反馈阶段
              </v-card-title>
              <v-card-text>
                通过后测和策略问卷，评估学习成果，获得学习总结和未来学习建议，巩固所学内容。
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-card-text>

      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn
          color="primary"
          variant="flat"
          :to="{ name: 'SelfRate' }"
        >
          开始使用
          <v-icon end icon="mdi-arrow-right"></v-icon>
        </v-btn>
      </v-card-actions>
    </v-card>
  </div>
</template>

<script>
import { computed, onMounted } from 'vue';
import { useStore } from 'vuex';

export default {
  name: 'Introduction',

  setup() {
    const store = useStore();

    // 获取系统介绍
    const introduction = computed(() => store.state.introduction);

    // 格式化介绍文本，将换行符转换为<p>标签
    const formattedIntroduction = computed(() => {
      if (!introduction.value) return '';

      return introduction.value
        .split('\n')
        .filter(paragraph => paragraph.trim() !== '')
        .map(paragraph => `<p class="mb-2">${paragraph}</p>`)
        .join('');
    });

    // 组件挂载时获取系统介绍
    onMounted(() => {
      if (!introduction.value) {
        store.dispatch('fetchIntroduction');
      }
    });

    return {
      introduction,
      formattedIntroduction
    };
  }
};
</script>

<style scoped>
.introduction {
  max-width: 100%;
}

.v-card-text p {
  text-indent: 2em;
  line-height: 1.6;
}
</style>