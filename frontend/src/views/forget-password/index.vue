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
                <h3 class="title">忘记密码</h3>
                <p class="sub-title">通过邮箱验证码重置您的登录密码</p>
              </div>

              <div class="step-indicator">
                <div class="step" :class="{ active: state.step >= 1, completed: state.step > 1 }">
                  <div class="step-number">1</div>
                  <div class="step-label">验证身份</div>
                </div>
                <div class="step-divider" />
                <div class="step" :class="{ active: state.step >= 2 }">
                  <div class="step-number">2</div>
                  <div class="step-label">重置密码</div>
                </div>
              </div>

              <el-form
                v-if="state.step === 1"
                ref="step1Ref"
                :model="state.step1"
                :rules="step1Rules"
                size="large"
                label-position="top"
                @keyup.enter="nextStep"
              >
                <el-form-item label="用户名 / 邮箱" prop="account">
                  <el-input v-model.trim="state.step1.account" placeholder="请输入注册邮箱" clearable />
                </el-form-item>
                <el-form-item label="邮箱验证码" prop="code">
                  <div class="email-code-row">
                    <el-input
                      v-model.trim="state.step1.code"
                      maxlength="4"
                      placeholder="4 位数字验证码"
                      clearable
                      class="email-code-input"
                    />
                    <el-button
                      class="email-code-btn"
                      :loading="state.sendingCode"
                      :disabled="state.countdown > 0 || !state.step1.account"
                      @click="sendCode"
                    >
                      {{ state.countdown > 0 ? `${state.countdown}s 后重发` : '获取验证码' }}
                    </el-button>
                  </div>
                </el-form-item>
                <el-form-item class="auth-action-item">
                  <el-button type="primary" class="auth-submit-btn" :loading="state.loading" @click="nextStep">
                    下一步
                  </el-button>
                </el-form-item>
              </el-form>

              <el-form
                v-else
                ref="step2Ref"
                :model="state.step2"
                :rules="step2Rules"
                size="large"
                label-position="top"
                @keyup.enter="resetPassword"
              >
                <el-form-item label="新密码" prop="newPassword">
                  <el-input
                    v-model.trim="state.step2.newPassword"
                    type="password"
                    show-password
                    autocomplete="new-password"
                    placeholder="至少 6 位"
                  />
                </el-form-item>
                <el-form-item label="确认新密码" prop="confirmPassword">
                  <el-input
                    v-model.trim="state.step2.confirmPassword"
                    type="password"
                    show-password
                    autocomplete="new-password"
                    placeholder="再次输入新密码"
                  />
                </el-form-item>
                <div class="step-actions">
                  <el-button @click="state.step = 1">上一步</el-button>
                  <el-button type="primary" :loading="state.loading" @click="resetPassword">重置密码</el-button>
                </div>
              </el-form>

              <div class="auth-footer-links">
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

<script setup lang="ts" name="forgetPasswordIndex">
import { defineAsyncComponent, onMounted, reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import type { FormInstance, FormRules } from 'element-plus';
import { ElMessage, ElNotification } from 'element-plus';
import { useAuthApi } from '/@/api/auth/index';
import { NextLoading } from '/@/utils/loading';

const LoginLeftView = defineAsyncComponent(() => import('/@/views/login/component/LoginLeftView.vue'));

const router = useRouter();
const step1Ref = ref<FormInstance>();
const step2Ref = ref<FormInstance>();

const state = reactive({
  step: 1,
  loading: false,
  sendingCode: false,
  countdown: 0,
  step1: {
    account: '',
    code: '',
  },
  step2: {
    newPassword: '',
    confirmPassword: '',
  },
});

const step1Rules: FormRules = {
  account: [{ required: true, message: '请输入邮箱', trigger: 'blur' }],
  code: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { len: 4, message: '验证码为 4 位', trigger: 'blur' },
  ],
};

const validateConfirm = (_rule: unknown, value: string, callback: (err?: Error) => void) => {
  if (!value) callback(new Error('请再次输入新密码'));
  else if (value !== state.step2.newPassword) callback(new Error('两次输入的密码不一致'));
  else callback();
};

const step2Rules: FormRules = {
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 64, message: '密码至少 6 位', trigger: 'blur' },
  ],
  confirmPassword: [{ required: true, validator: validateConfirm, trigger: 'blur' }],
};

const startCountdown = () => {
  state.countdown = 60;
  const timer = setInterval(() => {
    state.countdown -= 1;
    if (state.countdown <= 0) clearInterval(timer);
  }, 1000);
};

const sendCode = async () => {
  if (!state.step1.account) {
    ElMessage.warning('请先输入邮箱');
    return;
  }
  state.sendingCode = true;
  try {
    await useAuthApi().sendEmailCode({
      username: state.step1.account,
      title: '忘记密码验证码',
      mail: state.step1.account,
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
  if (!step1Ref.value) return;
  try {
    await step1Ref.value.validate();
    state.step = 2;
  } catch {
    /* validation failed */
  }
};

const resetPassword = async () => {
  if (!step2Ref.value) return;
  try {
    await step2Ref.value.validate();
  } catch {
    return;
  }
  state.loading = true;
  try {
    await useAuthApi().forgetPassword({
      username: state.step1.account,
      email: state.step1.account,
      code: state.step1.code,
      new_password: state.step2.newPassword,
    });
    ElNotification.success({ title: '重置成功', message: '请使用新密码登录' });
    setTimeout(() => router.push('/login'), 1500);
  } catch {
    /* request 拦截器已提示 */
  } finally {
    state.loading = false;
  }
};

onMounted(() => {
  NextLoading.done();
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

.step-actions {
  display: flex;
  gap: 12px;

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

  a {
    color: var(--el-color-primary);
    text-decoration: none;

    &:hover {
      text-decoration: underline;
    }
  }
}
</style>
