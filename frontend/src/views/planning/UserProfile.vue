<template>
  <div class="user-profile">
    <v-card>
      <v-card-title class="text-h5 primary--text">
        <v-icon start icon="mdi-account-outline"></v-icon>
        用户信息采集
      </v-card-title>

      <v-card-text>
        <p class="text-body-1 mb-4">
          为了提供个性化的英语阅读学习支持，请填写以下信息，帮助我们更好地了解您的英语学习背景和需求。
        </p>

        <v-form ref="form" v-model="valid" @submit.prevent="submitForm">
          <v-container>
            <v-row>
              <!-- 基本信息 -->
              <v-col cols="12">
                <h3 class="text-subtitle-1 mb-2">基本信息</h3>
              </v-col>

              <v-col cols="12" md="6">
                <v-text-field
                  v-model="formData.name"
                  label="姓名"
                  variant="outlined"
                  required
                  :rules="nameRules"
                ></v-text-field>
              </v-col>

              <v-col cols="12" md="6">
                <v-select
                  v-model="formData.gender"
                  label="性别"
                  variant="outlined"
                  :items="['男', '女', '其他']"
                ></v-select>
              </v-col>

              <v-col cols="12" md="6">
                <v-text-field
                  v-model="formData.grade"
                  label="年级"
                  variant="outlined"
                  hint="例如：大一、大二、硕士一年级等"
                ></v-text-field>
              </v-col>

              <v-col cols="12" md="6">
                <v-text-field
                  v-model="formData.major"
                  label="专业"
                  variant="outlined"
                ></v-text-field>
              </v-col>

              <!-- CET-4相关信息 -->
              <v-col cols="12">
                <h3 class="text-subtitle-1 mb-2">英语四级(CET-4)信息</h3>
              </v-col>

              <v-col cols="12" md="6">
                <v-radio-group
                  v-model="formData.cet4_taken"
                  label="是否参加过英语四级考试"
                  inline
                >
                  <v-radio value="是" label="是"></v-radio>
                  <v-radio value="否" label="否"></v-radio>
                </v-radio-group>
              </v-col>

              <v-col cols="12" md="6" v-if="formData.cet4_taken === '是'">
                <v-text-field
                  v-model="formData.cet4_score"
                  label="英语四级总分"
                  variant="outlined"
                  type="number"
                  min="0"
                  max="710"
                ></v-text-field>
              </v-col>

              <v-col cols="12" md="6" v-if="formData.cet4_taken === '是'">
                <v-text-field
                  v-model="formData.cet4_reading_score"
                  label="英语四级阅读分数"
                  variant="outlined"
                  type="number"
                  min="0"
                  max="249"
                  hint="四级阅读满分为249分"
                ></v-text-field>
              </v-col>

              <!-- CET-6相关信息 -->
              <v-col cols="12">
                <h3 class="text-subtitle-1 mb-2">英语六级(CET-6)信息</h3>
              </v-col>

              <v-col cols="12" md="6">
                <v-radio-group
                  v-model="formData.cet6_taken"
                  label="是否参加过英语六级考试"
                  inline
                >
                  <v-radio value="是" label="是"></v-radio>
                  <v-radio value="否" label="否"></v-radio>
                </v-radio-group>
              </v-col>

              <v-col cols="12" md="6" v-if="formData.cet6_taken === '是'">
                <v-text-field
                  v-model="formData.cet6_score"
                  label="英语六级总分"
                  variant="outlined"
                  type="number"
                  min="0"
                  max="710"
                ></v-text-field>
              </v-col>

              <v-col cols="12" md="6" v-if="formData.cet6_taken === '是'">
                <v-text-field
                  v-model="formData.cet6_reading_score"
                  label="英语六级阅读分数"
                  variant="outlined"
                  type="number"
                  min="0"
                  max="249"
                  hint="六级阅读满分为249分"
                ></v-text-field>
              </v-col>

              <!-- 其他英语考试信息 -->
              <v-col cols="12">
                <h3 class="text-subtitle-1 mb-2">其他英语考试信息（选填）</h3>
              </v-col>

              <v-col cols="12" md="4">
                <v-text-field
                  v-model="formData.exam_name"
                  label="考试名称"
                  variant="outlined"
                  hint="例如：托福、雅思、专四、专八等"
                ></v-text-field>
              </v-col>

              <v-col cols="12" md="4">
                <v-text-field
                  v-model="formData.total_score"
                  label="总分"
                  variant="outlined"
                  type="number"
                ></v-text-field>
              </v-col>

              <v-col cols="12" md="4">
                <v-text-field
                  v-model="formData.reading_score"
                  label="阅读分数"
                  variant="outlined"
                  type="number"
                ></v-text-field>
              </v-col>
            </v-row>
          </v-container>
        </v-form>
      </v-card-text>

      <v-divider></v-divider>

      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn
          color="primary"
          variant="flat"
          :loading="loading"
          :disabled="!valid"
          @click="submitForm"
        >
          保存并继续
          <v-icon end icon="mdi-arrow-right"></v-icon>
        </v-btn>
      </v-card-actions>
    </v-card>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';

export default {
  name: 'UserProfile',

  setup() {
    const store = useStore();
    const router = useRouter();
    const form = ref(null);
    const valid = ref(false);
    const loading = computed(() => store.state.loading);

    // 表单数据
    const formData = ref({
      name: '',
      gender: '',
      grade: '',
      major: '',
      cet4_taken: null,
      cet4_score: '',
      cet4_reading_score: '',
      cet6_taken: null,
      cet6_score: '',
      cet6_reading_score: '',
      exam_name: '',
      total_score: '',
      reading_score: ''
    });

    // 表单验证规则
    const nameRules = [
      v => !!v || '姓名不能为空',
      v => (v && v.length <= 20) || '姓名不能超过20个字符'
    ];

    // 提交表单
    const submitForm = async () => {
      if (!valid.value) return;

      const userData = {
        name: formData.value.name,
        grade: formData.value.grade,
        major: formData.value.major,
        gender: formData.value.gender,
        cet4_taken: formData.value.cet4_taken,
        cet4_score: formData.value.cet4_score,
        cet4_reading_score: formData.value.cet4_reading_score,
        cet6_taken: formData.value.cet6_taken,
        cet6_score: formData.value.cet6_score,
        cet6_reading_score: formData.value.cet6_reading_score,
        other_scores: formData.value.exam_name ? "是" : "否",
        exam_name: formData.value.exam_name,
        total_score: formData.value.total_score,
        reading_score: formData.value.reading_score
      };

      const success = await store.dispatch('createUserProfile', userData);

      if (success) {
        // 导航到前测页面
        router.push({ name: 'PreTest', params: { id: 1 } });
      }
    };

    // 组件挂载时，检查是否有用户名，有则预填表单
    onMounted(async () => {
      const userName = store.state.userName;
      if (userName) {
        formData.value.name = userName;

        // 获取用户信息
        await store.dispatch('fetchUserProfile');
        const userProfile = store.state.userProfile;

        // 如果有用户信息，预填表单
        if (userProfile) {
          formData.value.gender = userProfile.gender || '';
          formData.value.grade = userProfile.grade || '';
          formData.value.major = userProfile.major || '';
          formData.value.cet4_taken = userProfile['Have you taken the CET-4 exam:'] || null;
          formData.value.cet4_score = userProfile['CET-4 score'] || '';
          formData.value.cet4_reading_score = userProfile['CET-4 reading score'] || '';
          formData.value.cet6_taken = userProfile['Have you taken the CET-6 exam'] || null;
          formData.value.cet6_score = userProfile['CET-6 score'] || '';
          formData.value.cet6_reading_score = userProfile['CET-6 reading score'] || '';
          formData.value.exam_name = userProfile['Exam name'] || '';
          formData.value.total_score = userProfile['Total score'] || '';
          formData.value.reading_score = userProfile['Reading score'] || '';
        }
      }
    });

    return {
      form,
      valid,
      loading,
      formData,
      nameRules,
      submitForm
    };
  }
};
</script>

<style scoped>
.user-profile {
  max-width: 100%;
}
</style>