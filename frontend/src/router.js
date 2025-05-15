import { createRouter, createWebHistory } from 'vue-router';

// 计划阶段视图
import Introduction from './views/planning/Introduction.vue';
import SelfRate from './views/planning/SelfRate.vue';
import UserProfile from './views/planning/UserProfile.vue';
import PreTest from './views/planning/PreTest.vue';
import StrategyPreTest from './views/planning/StrategyPreTest.vue';

// 执行阶段视图
import AIInteraction from './views/execution/AIInteraction.vue';

// 反馈阶段视图
import PostTest from './views/feedback/PostTest.vue';
import StrategyPostTest from './views/feedback/StrategyPostTest.vue';
import Summary from './views/feedback/Summary.vue';

const routes = [
  {
    path: '/',
    redirect: '/introduction',
  },

  // 计划阶段路由
  {
    path: '/introduction',
    name: 'Introduction',
    component: Introduction,
    meta: {
      title: '系统介绍',
      phase: 'planning',
      order: 1
    }
  },
  {
    path: '/self-rate',
    name: 'SelfRate',
    component: SelfRate,
    meta: {
      title: '能力自评',
      phase: 'planning',
      order: 2
    }
  },
  {
    path: '/user-profile',
    name: 'UserProfile',
    component: UserProfile,
    meta: {
      title: '用户信息',
      phase: 'planning',
      order: 3
    }
  },
  {
    path: '/pre-test/:id',
    name: 'PreTest',
    component: PreTest,
    props: true,
    meta: {
      title: '阅读前测',
      phase: 'planning',
      order: 4
    }
  },
  {
    path: '/strategy-pre-test',
    name: 'StrategyPreTest',
    component: StrategyPreTest,
    meta: {
      title: '策略前测',
      phase: 'planning',
      order: 5
    }
  },

  // 执行阶段路由
  {
    path: '/ai-interaction',
    name: 'AIInteraction',
    component: AIInteraction,
    meta: {
      title: '个性化学习',
      phase: 'execution',
      order: 6
    }
  },

  // 反馈阶段路由
  {
    path: '/post-test/:id',
    name: 'PostTest',
    component: PostTest,
    props: true,
    meta: {
      title: '阅读后测',
      phase: 'feedback',
      order: 7
    }
  },
  {
    path: '/strategy-post-test',
    name: 'StrategyPostTest',
    component: StrategyPostTest,
    meta: {
      title: '策略后测',
      phase: 'feedback',
      order: 8
    }
  },
  {
    path: '/summary',
    name: 'Summary',
    component: Summary,
    meta: {
      title: '学习总结',
      phase: 'feedback',
      order: 9
    }
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// 全局导航守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = `PERSS - ${to.meta.title || '英语阅读支持系统'}`;

  // 检查用户名
  const userName = localStorage.getItem('userName');

  // 如果不是首页且没有用户名，重定向到用户信息页面
  if (to.path !== '/introduction' && to.path !== '/self-rate' && to.path !== '/user-profile' && !userName) {
    next('/user-profile');
  } else {
    next();
  }
});

export default router;