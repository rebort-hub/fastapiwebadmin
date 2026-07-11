<template>
  <el-form
    ref="loginFormRef"
    :model="state.ruleForm"
    :rules="state.rules"
    size="large"
    class="login-content-form"
    @keyup.enter="onSignIn"
  >
    <el-form-item class="login-animation1" prop="userName">
      <el-input
        v-model="state.ruleForm.userName"
        placeholder="请输入用户名"
        clearable
        autocomplete="off"
      >
        <template #prefix>
          <el-icon class="el-input__icon"><ele-User /></el-icon>
        </template>
      </el-input>
    </el-form-item>

    <el-form-item class="login-animation2" prop="password">
      <el-input
        v-model="state.ruleForm.password"
        :type="state.isShowPassword ? 'text' : 'password'"
        placeholder="请输入登录密码"
        autocomplete="off"
      >
        <template #prefix>
          <el-icon class="el-input__icon"><ele-Unlock /></el-icon>
        </template>
        <template #suffix>
          <i
            class="iconfont el-input__icon login-content-password"
            :class="state.isShowPassword ? 'icon-yincangmima' : 'icon-xianshimima'"
            @click="state.isShowPassword = !state.isShowPassword"
          />
        </template>
      </el-input>
    </el-form-item>

    <el-form-item v-if="state.captcha.enable" class="login-animation3" prop="captcha">
      <div class="login-captcha-wrap">
        <el-input
          v-model="state.ruleForm.captcha"
          maxlength="8"
          placeholder="请输入验证码"
          clearable
          autocomplete="off"
        >
          <template #prefix>
            <el-icon class="el-input__icon"><ele-Key /></el-icon>
          </template>
        </el-input>
        <button class="login-captcha-img" type="button" title="点击刷新验证码" @click="refreshCaptcha(true)">
          <el-icon v-if="state.captchaLoading" class="is-loading"><ele-Loading /></el-icon>
          <img v-else-if="state.captcha.img_base" :src="state.captcha.img_base" alt="验证码" />
          <span v-else>点击刷新</span>
        </button>
      </div>
    </el-form-item>

    <el-form-item class="login-animation4">
      <DragVerify v-model="state.sliderOk" />
    </el-form-item>

    <div class="login-options-row">
      <el-checkbox v-model="state.remember">记住账号</el-checkbox>
      <router-link class="login-forget-link" to="/forget-password">忘记密码？</router-link>
    </div>

    <el-form-item class="login-animation5">
      <el-button
        type="primary"
        class="login-content-submit"
        round
        v-waves
        :loading="state.loading.signIn"
        @click="onSignIn"
      >
        登 录
      </el-button>
    </el-form-item>
  </el-form>

  <ThirdPartyLogin :register-enabled="state.registerEnabled" @oauth="onOAuth" />
</template>

<script setup lang="ts">
defineOptions({ name: 'loginAccount' })
import { computed, defineAsyncComponent, onMounted, reactive, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { initBackEndControlRoutes } from '/@/router/backEnd';
import { Session } from '/@/utils/storage';
import { formatAxis } from '/@/utils/formatTime';
import { NextLoading } from '/@/utils/loading';
import { useUserApi } from '/@/api/useSystemApi/user';
import { useAuthApi } from '/@/api/auth/index';
import { useUserStore } from '/@/stores/user';
import { startOAuthLogin, type OAuthProvider } from '/@/utils/oauth';

const DragVerify = defineAsyncComponent(() => import('/@/views/login/component/DragVerify.vue'));
const ThirdPartyLogin = defineAsyncComponent(() => import('/@/views/login/component/ThirdPartyLogin.vue'));

const REMEMBER_KEY = 'fastapiwebadmin:login:username';
const loginFormRef = ref();
const route = useRoute();
const router = useRouter();

const state = reactive({
  isShowPassword: false,
  remember: true,
  sliderOk: false,
  captchaLoading: false,
  captcha: {
    enable: false,
    img_base: '',
    key: '',
  },
  registerEnabled: false,
  ruleForm: {
    userName: '',
    password: '',
    captcha: '',
  },
  rules: {
    userName: [
      { required: true, message: '请输入用户名', trigger: 'blur' },
      { min: 2, max: 20, message: '用户名长度在 2 到 20 个字符', trigger: 'blur' },
    ],
    password: [
      { required: true, message: '请输入密码', trigger: 'blur' },
      { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' },
    ],
    captcha: [{ required: true, message: '请输入验证码', trigger: 'blur' }],
  },
  loading: {
    signIn: false,
  },
});

const currentTime = computed(() => formatAxis(new Date()));

const refreshCaptcha = async (resetField = false) => {
  try {
    state.captchaLoading = true;
    const res = await useAuthApi().getCaptcha();
    const data = res.data || {};
    state.captcha.enable = !!data.enable;
    state.captcha.img_base = data.img_base || '';
    state.captcha.key = data.key || '';
    state.registerEnabled = !!data.register_enabled;
    if (resetField) state.ruleForm.captcha = '';
  } catch (error: any) {
    state.captcha.enable = false;
    ElMessage.error(error?.message || '获取验证码失败');
  } finally {
    state.captchaLoading = false;
  }
};

watch(
  () => state.captcha.enable,
  (enabled) => {
    state.rules.captcha = enabled
      ? [{ required: true, message: '请输入验证码', trigger: 'blur' }]
      : [];
  },
  { immediate: true }
);

const onOAuth = (provider: OAuthProvider) => {
  startOAuthLogin(provider);
};

const onSignIn = async () => {
  if (!loginFormRef.value) return;
  if (!state.sliderOk) {
    ElMessage.warning('请拖动滑块完成验证');
    return;
  }

  try {
    await loginFormRef.value.validate();
  } catch {
    ElMessage.error('请检查输入信息');
    return;
  }

  state.loading.signIn = true;
  try {
    const payload: Record<string, string> = {
      username: state.ruleForm.userName,
      password: state.ruleForm.password,
    };
    if (state.captcha.enable) {
      payload.captcha = state.ruleForm.captcha;
      payload.captcha_key = state.captcha.key;
    }

    const res = await useUserApi().signIn(payload);
    if (state.remember) {
      localStorage.setItem(REMEMBER_KEY, state.ruleForm.userName);
    } else {
      localStorage.removeItem(REMEMBER_KEY);
    }
    Session.set('token', res.data.token);
    await useUserStore().setUserInfos();
    await initBackEndControlRoutes();
    signInSuccess(false);
  } catch {
    state.sliderOk = false;
    await refreshCaptcha(true);
    state.loading.signIn = false;
  }
};

const signInSuccess = (isNoPower: boolean) => {
  if (isNoPower) {
    ElMessage.warning('抱歉，您没有登录权限');
    Session.clear();
  } else {
    const params = route.query?.params || {};
    if (route.query?.redirect) {
      router.push({
        path: route.query?.redirect as string,
        query: Object.keys(params).length > 0 ? JSON.parse(params as string) : '',
      });
    } else {
      router.push('/home');
    }
    ElMessage.success(`${currentTime.value}，欢迎回来！`);
    NextLoading.start();
  }
  state.loading.signIn = false;
};

onMounted(async () => {
  const remembered = localStorage.getItem(REMEMBER_KEY);
  if (remembered) state.ruleForm.userName = remembered;
  await refreshCaptcha();
});
</script>

<style scoped lang="scss">
.login-content-form {
  :deep(.el-input__wrapper) {
    border-radius: 8px;
    min-height: 40px;
  }

  .login-captcha-wrap {
    display: flex;
    gap: 12px;
    width: 100%;
  }

  .login-captcha-img {
    display: flex;
    width: 132px;
    height: 40px;
    flex-shrink: 0;
    align-items: stretch;
    justify-content: stretch;
    padding: 0;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    background: #f8fafc;
    cursor: pointer;
    overflow: hidden;
  }

  .login-captcha-img img {
    display: block;
    width: 100%;
    height: 100%;
    object-fit: fill;
  }

  .login-options-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: 4px 0 16px;
  }

  .login-forget-link {
    font-size: 14px;
    color: var(--el-color-primary);
    text-decoration: none;

    &:hover {
      text-decoration: underline;
    }
  }

  .login-content-password {
    display: inline-block;
    width: 20px;
    cursor: pointer;
  }

  .login-content-submit {
    width: 100%;
    height: 42px;
    letter-spacing: 2px;
    font-weight: 500;
    border-radius: 8px;
  }

  @for $i from 1 through 5 {
    .login-animation#{$i} {
      opacity: 0;
      animation-name: error-num;
      animation-duration: 0.5s;
      animation-fill-mode: forwards;
      animation-delay: calc($i / 10) + s;
    }
  }
}
</style>
