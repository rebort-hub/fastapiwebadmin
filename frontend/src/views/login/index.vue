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
                <h3 class="title">{{ getThemeConfig.globalTitle }}</h3>
                <p class="sub-title">欢迎回来，请登录您的账号</p>
              </div>
              <Account />
            </div>
          </div>
          <footer class="login-page-footer">
            <span>Copyright © 2024-2027 fastapiwebadmin</span>
            <span class="login-page-footer__sep">|</span>
            <a class="login-page-footer__link" href="https://beian.miit.gov.cn/" target="_blank">贵ICP备202698015号</a>
          </footer>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineOptions({ name: 'loginIndex' })
import { computed, defineAsyncComponent, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { storeToRefs } from 'pinia';
import { ElMessage } from 'element-plus';
import { useThemeConfig } from '/@/stores/themeConfig';
import { NextLoading } from '/@/utils/loading';
import { Session } from '/@/utils/storage';
import { initBackEndControlRoutes } from '/@/router/backEnd';
import { useUserStore } from '/@/stores/user';
import {
  parseOAuthCallbackParams,
  resolveOAuthRedirectTarget,
  stripOAuthCallbackParams,
} from '/@/utils/oauth';

const Account = defineAsyncComponent(() => import('/@/views/login/component/account.vue'));
const LoginLeftView = defineAsyncComponent(() => import('/@/views/login/component/LoginLeftView.vue'));

const storesThemeConfig = useThemeConfig();
const { themeConfig } = storeToRefs(storesThemeConfig);
const route = useRoute();
const router = useRouter();

const getThemeConfig = computed(() => themeConfig.value);

const handleOAuthCallback = async () => {
  const { accessToken, oauthError, redirect } = parseOAuthCallbackParams(route.query as Record<string, unknown>);
  if (!oauthError && !accessToken) return;

  const nextQuery = stripOAuthCallbackParams(route.query);
  await router.replace({ path: '/login', query: nextQuery });

  if (oauthError) {
    ElMessage.error(decodeURIComponent(oauthError));
    return;
  }

  if (!accessToken) return;

  try {
    Session.set('token', accessToken);
    await useUserStore().setUserInfos();
    await initBackEndControlRoutes();
    await router.push(resolveOAuthRedirectTarget(redirect));
    ElMessage.success('第三方登录成功');
    NextLoading.start();
  } catch {
    Session.clear();
    ElMessage.error('第三方登录失败，请尝试账号密码登录');
  }
};

onMounted(async () => {
  NextLoading.done();
  await handleOAuthCallback();
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
  gap: 8px;
  padding: 16px 24px 24px;
  font-size: 13px;
  color: #9ca3af;
}

.login-page-footer__sep {
  color: #d1d5db;
}

.login-page-footer__link {
  color: inherit;
  text-decoration: none;
}

.login-page-footer__link:hover {
  color: var(--el-color-primary);
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
</style>
