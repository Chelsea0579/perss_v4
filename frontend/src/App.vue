<template>
  <v-app>
    <v-app-bar color="primary" density="compact" elevation="2">
      <v-app-bar-title>个性化英语阅读支持系统 (PERSS)</v-app-bar-title>
      <v-spacer></v-spacer>
      <v-chip v-if="userName" color="info" class="ml-2">
        <v-icon start icon="mdi-account"></v-icon>
        {{ userName }}
      </v-chip>
    </v-app-bar>

    <v-main>
      <v-container fluid>
        <v-row>
          <v-col cols="12" md="3" v-if="isAuthenticated">
            <v-card>
              <v-list>
                <v-list-subheader>计划阶段</v-list-subheader>
                <v-list-item
                  v-for="item in planningRoutes"
                  :key="item.path"
                  :to="item.path"
                  :value="item.path"
                  :title="item.meta.title"
                  :disabled="isProgressDisabled(item)"
                >
                  <template v-slot:prepend>
                    <v-icon :icon="getRouteIcon(item)"></v-icon>
                  </template>
                </v-list-item>

                <v-list-subheader>执行阶段</v-list-subheader>
                <v-list-item
                  v-for="item in executionRoutes"
                  :key="item.path"
                  :to="item.path"
                  :value="item.path"
                  :title="item.meta.title"
                  :disabled="isProgressDisabled(item)"
                >
                  <template v-slot:prepend>
                    <v-icon :icon="getRouteIcon(item)"></v-icon>
                  </template>
                </v-list-item>

                <v-list-subheader>反馈阶段</v-list-subheader>
                <v-list-item
                  v-for="item in feedbackRoutes"
                  :key="item.path"
                  :to="item.path"
                  :value="item.path"
                  :title="item.meta.title"
                  :disabled="isProgressDisabled(item)"
                >
                  <template v-slot:prepend>
                    <v-icon :icon="getRouteIcon(item)"></v-icon>
                  </template>
                </v-list-item>
              </v-list>
            </v-card>
          </v-col>

          <v-col cols="12" :md="isAuthenticated ? 9 : 12">
            <v-card>
              <v-card-text>
                <v-progress-linear
                  v-if="loading"
                  indeterminate
                  color="primary"
                ></v-progress-linear>

                <v-alert
                  v-if="error"
                  type="error"
                  variant="tonal"
                  closable
                  @click:close="clearError"
                >
                  {{ error }}
                </v-alert>

                <router-view></router-view>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </v-main>

    <v-footer app>
      <div class="text-center w-100">
        &copy; {{ new Date().getFullYear() }} - 个性化英语阅读支持系统 (PERSS)
      </div>
    </v-footer>
  </v-app>
</template>

<script>
import { computed, onMounted } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';

export default {
  name: 'App',

  setup() {
    const store = useStore();
    const router = useRouter();

    // 计算属性
    const loading = computed(() => store.state.loading);
    const error = computed(() => store.state.error);
    const userName = computed(() => store.state.userName);
    const isAuthenticated = computed(() => store.getters.isAuthenticated);
    const currentPhase = computed(() => store.getters.getCurrentPhase);

    // 路由分组
    const routes = router.getRoutes();

    const planningRoutes = computed(() =>
      routes
        .filter(route => route.meta?.phase === 'planning')
        .sort((a, b) => (a.meta?.order || 0) - (b.meta?.order || 0))
    );

    const executionRoutes = computed(() =>
      routes
        .filter(route => route.meta?.phase === 'execution')
        .sort((a, b) => (a.meta?.order || 0) - (b.meta?.order || 0))
    );

    const feedbackRoutes = computed(() =>
      routes
        .filter(route => route.meta?.phase === 'feedback')
        .sort((a, b) => (a.meta?.order || 0) - (b.meta?.order || 0))
    );

    // 路由图标
    const getRouteIcon = (route) => {
      const icons = {
        'Introduction': 'mdi-information-outline',
        'SelfRate': 'mdi-checkbox-marked-circle-outline',
        'UserProfile': 'mdi-account-outline',
        'PreTest': 'mdi-file-document-outline',
        'StrategyPreTest': 'mdi-clipboard-list-outline',
        'AIInteraction': 'mdi-robot-outline',
        'PostTest': 'mdi-file-check-outline',
        'StrategyPostTest': 'mdi-clipboard-check-outline',
        'Summary': 'mdi-chart-bar'
      };

      return icons[route.name] || 'mdi-circle-outline';
    };

    // 路由禁用逻辑
    const isProgressDisabled = (route) => {
      const phases = ['planning', 'execution', 'feedback'];
      const currentPhaseIndex = phases.indexOf(currentPhase.value);
      const routePhaseIndex = phases.indexOf(route.meta?.phase);

      // 如果路由阶段在当前阶段之后，则禁用
      if (routePhaseIndex > currentPhaseIndex) {
        return true;
      }

      // 如果是前测页面，根据参数确定
      if (route.name === 'PreTest') {
        const id = parseInt(route.path.split('/').pop());
        // 只允许访问试卷1和2
        return id > 2;
      }

      // 如果是后测页面，根据参数确定
      if (route.name === 'PostTest') {
        const id = parseInt(route.path.split('/').pop());
        // 只允许访问试卷3和4
        return id < 3;
      }

      return false;
    };

    // 清除错误
    const clearError = () => {
      store.commit('SET_ERROR', null);
    };

    // 组件挂载时
    onMounted(() => {
      // 如果已登录，获取用户信息
      if (isAuthenticated.value) {
        store.dispatch('fetchUserProfile');
      }
    });

    return {
      loading,
      error,
      userName,
      isAuthenticated,
      currentPhase,
      planningRoutes,
      executionRoutes,
      feedbackRoutes,
      getRouteIcon,
      isProgressDisabled,
      clearError
    };
  }
};
</script>

<style>
.v-application {
  font-family: 'Roboto', sans-serif;
}

.v-card {
  margin-bottom: 16px;
}
</style>