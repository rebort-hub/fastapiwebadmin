<template>
  <div class="login-page-root">
    <div class="login-auth-split">
      <div class="login-auth-split__col login-auth-split__col--illustration">
        <LoginLeftView />
      </div>
      <div class="login-auth-split__col login-auth-split__col--form">
        <div class="login-page-panel">
          <div class="login-page-panel__main">
            <div class="auth-right-wrap">
              <div class="form-intro">
                <h3 class="title">注册账号</h3>
                <p class="sub-title">创建您的账号，开始使用系统</p>
              </div>

              <el-alert
                v-if="!state.registerEnabled && state.configLoaded"
                title="注册功能已关闭，请联系管理员"
                type="warning"
                :closable="false"
                show-icon
                style="margin-bottom: 16px"
              />

              <el-form
                v-else
                ref="formRef"
                :model="state.form"
                :rules="rules"
                size="large"
                label-position="top"
                @keyup.enter="handleSubmit"
              >
                <div class="step-indicator">
                  <div class="step" :class="{ active: state.step >= 1, completed: state.step > 1 }">
                    <div class="step-number">1</div>
                    <div class="step-label">基本信息</div>
                  </div>
                  <div class="step-divider" />
                  <div class="step" :class="{ active: state.step >= 2 }">
                    <div class="step-number">2</div>
                    <div class="step-label">邮箱验证</div>
                  </div>
                </div>

                <template v-if="state.step === 1">
                  <el-form-item label="用户名" prop="username">
                    <el-input v-model.trim="state.form.username" placeholder="3-20 个字符" clearable />
                  </el-form-item>
                  <el-form-item label="密码" prop="password">
                    <el-input
                      v-model.trim="state.form.password"
                      type="password"
                      placeholder="至少 6 位"
                      show-password
                      autocomplete="off"
                    />
                  </el-form-item>
                  <el-form-item label="确认密码" prop="confirmPassword">
                    <el-input
                      v-model.trim="state.form.confirmPassword"
                      type="password"
                      placeholder="再次输入密码"
                      show-password
                      autocomplete="off"
                    />
                  </el-form-item>
                  <el-form-item label="邮箱" prop="email">
                    <el-input v-model.trim="state.form.email" placeholder="用于接收验证码" clearable />
                  </el-form-item>
                  <el-form-item label="昵称（可选）" prop="nickname" class="auth-last-field">
                    <el-input v-model.trim="state.form.nickname" placeholder="显示名称" clearable />
                  </el-form-item>
                  <el-form-item class="auth-action-item">
                    <el-button type="primary" class="auth-submit-btn" @click="nextStep">下一步</el-button>
                  </el-form-item>
                </template>

                <template v-else>
                  <el-form-item label="邮箱验证码" prop="code">
                    <div class="email-code-row">
                      <el-input
                        v-model.trim="state.form.code"
                        maxlength="4"
                        placeholder="4 位数字验证码"
                        clearable
                        class="email-code-input"
                      />
                      <el-button
                        class="email-code-btn"
                        :loading="state.sendingCode"
                        :disabled="state.countdown > 0"
                        @click="sendCode"
                      >
                        {{ state.countdown > 0 ? `${state.countdown}s 后重发` : '获取验证码' }}
                      </el-button>
                    </div>
                  </el-form-item>
                  <el-form-item prop="agreement">
                    <el-checkbox v-model="state.form.agreement">我已阅读并同意相关服务条款</el-checkbox>
                  </el-form-item>
                  <div class="step-actions">
                    <el-button @click="state.step = 1">上一步</el-button>
                    <el-button type="primary" :loading="state.loading" @click="submitRegister">注册</el-button>
                  </div>
                </template>
              </el-form>

              <div class="auth-footer-links">
                <span>已有账号？</span>
                <router-link to="/login">返回登录</router-link>
              </div>
            </div>
          </div>
          <footer class="login-page-footer">
            <span>Copyright © 2024-2027 fastapiwebadmin</span>
          </footer>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts" name="registerIndex">
import { defineAsyncComponent, onMounted, reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import type { FormInstance, FormRules } from 'element-plus';
import { ElMessage, ElNotification } from 'element-plus';
import { useAuthApi } from '/@/api/auth/index';
import { NextLoading } from '/@/utils/loading';

const LoginLeftView = defineAsyncComponent(() => import('/@/views/login/component/LoginLeftView.vue'));

const router = useRouter();
const formRef = ref<FormInstance>();

const state = reactive({
  step: 1,
  loading: false,
  sendingCode: false,
  countdown: 0,
  registerEnabled: true,
  configLoaded: false,
  form: {
    username: '',
    password: '',
    confirmPassword: '',
    email: '',
    nickname: '',
    code: '',
    agreement: false,
  },
});

const validateConfirm = (_rule: unknown, value: string, callback: (err?: Error) => void) => {
  if (!value) callback(new Error('请再次输入密码'));
  else if (value !== state.form.password) callback(new Error('两次输入的密码不一致'));
  else callback();
};

const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度为 3-20 个字符', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 64, message: '密码至少 6 位', trigger: 'blur' },
  ],
  confirmPassword: [{ required: true, validator: validateConfirm, trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' },
  ],
  code: [
    { required: true, message: '请输入邮箱验证码', trigger: 'blur' },
    { len: 4, message: '验证码为 4 位', trigger: 'blur' },
  ],
  agreement: [
    {
      validator: (_rule, value, callback) => {
        if (!value) callback(new Error('请同意服务条款'));
        else callback();
      },
      trigger: 'change',
    },
  ],
};

const loadConfig = async () => {
  try {
    const res = await useAuthApi().getCaptcha();
    state.registerEnabled = !!res.data?.register_enabled;
  } catch {
    state.registerEnabled = false;
  } finally {
    state.configLoaded = true;
  }
};

const startCountdown = () => {
  state.countdown = 60;
  const timer = setInterval(() => {
    state.countdown -= 1;
    if (state.countdown <= 0) clearInterval(timer);
  }, 1000);
};

const sendCode = async () => {
  if (!state.form.email) {
    ElMessage.warning('请先填写邮箱');
    return;
  }
  state.sendingCode = true;
  try {
    await useAuthApi().sendEmailCode({
      username: state.form.username || state.form.email,
      title: '注册验证码',
      mail: state.form.email,
    });
    ElMessage.success('验证码已发送至邮箱');
    startCountdown();
  } catch {
    /* request 拦截器已提示 */
  } finally {
    state.sendingCode = false;
  }
};

const nextStep = async () => {
  if (!formRef.value) return;
  try {
    await formRef.value.validateField(['username', 'password', 'confirmPassword', 'email']);
    state.step = 2;
  } catch {
    /* validation failed */
  }
};

const handleSubmit = () => {
  if (state.step === 1) nextStep();
  else submitRegister();
};

const submitRegister = async () => {
  if (!formRef.value) return;
  try {
    await formRef.value.validate();
  } catch {
    return;
  }
  state.loading = true;
  try {
    await useAuthApi().register({
      username: state.form.username,
      password: state.form.password,
      email: state.form.email,
      code: state.form.code,
      nickname: state.form.nickname || undefined,
    });
    ElNotification.success({ title: '注册成功', message: '请使用新账号登录' });
    setTimeout(() => router.push('/login'), 1500);
  } catch {
    /* request 拦截器已提示 */
  } finally {
    state.loading = false;
  }
};

onMounted(async () => {
  NextLoading.done();
  await loadConfig();
});
</script>

<style scoped lang="scss">
.login-page-root {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100vh;
  overflow: hidden;
  background: #f5f5f5;
}

.login-auth-split {
  display: flex;
  flex: 1;
  min-height: 0;
}

.login-auth-split__col--illustration {
  flex: 0 0 58%;
  min-width: 0;
}

.login-auth-split__col--form {
  display: flex;
  flex: 1;
  flex-direction: column;
  min-width: 0;
  background: #f5f5f5;
}

.login-page-panel {
  display: flex;
  flex: 1;
  flex-direction: column;
  min-height: 0;
}

.login-page-panel__main {
  display: flex;
  flex: 1;
  align-items: center;
  justify-content: center;
  padding: 48px 32px 16px;
}

.auth-right-wrap {
  width: min(440px, 100%);
  padding: 8px 0;
}

.form-intro .title {
  margin: 0;
  font-size: 32px;
  font-weight: 600;
  line-height: 1.2;
  color: #1f2937;
}

.form-intro .sub-title {
  margin: 10px 0 28px;
  font-size: 14px;
  color: #6b7280;
}

.login-page-footer {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px 24px 24px;
  font-size: 13px;
  color: #9ca3af;
}

@media (max-width: 960px) {
  .login-auth-split {
    flex-direction: column;
  }

  .login-auth-split__col--illustration {
    flex: 0 0 auto;
    min-height: 240px;
  }
}

.step-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-bottom: 24px;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;

  .step-number {
    display: flex;
    width: 32px;
    height: 32px;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    background: #e5e7eb;
    color: #9ca3af;
    font-size: 14px;
    font-weight: 600;
  }

  .step-label {
    font-size: 12px;
    color: #9ca3af;
  }

  &.active .step-number {
    background: var(--el-color-primary);
    color: #fff;
  }

  &.active .step-label {
    color: var(--el-color-primary);
  }

  &.completed .step-number {
    background: var(--el-color-success);
    color: #fff;
  }
}

.step-divider {
  width: 48px;
  height: 2px;
  background: #e5e7eb;
}

.email-code-row {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;

  :deep(.email-code-input) {
    flex: 1;
    min-width: 0;
  }

  .email-code-btn {
    flex-shrink: 0;
    min-width: 120px;
    height: 40px;
  }
}

.auth-action-item {
  margin-top: 8px;
  margin-bottom: 0;

  :deep(.el-form-item__content) {
    margin-left: 0 !important;
  }
}

.auth-last-field {
  margin-bottom: 8px;
}

.step-actions {
  display: flex;
  gap: 12px;
  margin-top: 8px;

  .el-button {
    flex: 1;
    height: 42px;
  }
}

.auth-submit-btn {
  width: 100%;
  height: 42px;
  border-radius: 8px;
}

.auth-footer-links {
  margin-top: 20px;
  text-align: center;
  font-size: 14px;
  color: #6b7280;

  a {
    margin-left: 4px;
    color: var(--el-color-primary);
    text-decoration: none;

    &:hover {
      text-decoration: underline;
    }
  }
}
</style>
