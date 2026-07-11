<template>
  <div class="login-third-party">
    <div class="login-divider">
      <span class="login-divider__line" />
      <span class="login-divider__text">其他登录方式</span>
      <span class="login-divider__line" />
    </div>
    <div class="login-oauth-icons">
      <el-tooltip v-for="item in oauthItems" :key="item.key" :content="item.tip" placement="top">
        <button
          class="login-oauth-btn"
          type="button"
          :aria-label="item.tip"
          @click="emit('oauth', item.key)"
        >
          <component :is="item.icon" :class="item.className" />
        </button>
      </el-tooltip>
    </div>
    <div v-if="registerEnabled" class="login-register-row">
      <span>还没有账号？</span>
      <router-link to="/register">立即注册</router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
defineOptions({ name: 'ThirdPartyLogin' })
import type { Component } from 'vue';
import type { OAuthProvider } from '/@/utils/oauth';
import WechatIcon from '/@/views/login/component/oauth-icons/WechatIcon.vue';
import QqIcon from '/@/views/login/component/oauth-icons/QqIcon.vue';
import GithubIcon from '/@/views/login/component/oauth-icons/GithubIcon.vue';
import GiteeIcon from '/@/views/login/component/oauth-icons/GiteeIcon.vue';

defineProps<{ registerEnabled?: boolean }>();

const emit = defineEmits<{ (e: 'oauth', provider: OAuthProvider): void }>();

const oauthItems: Array<{
  key: OAuthProvider;
  tip: string;
  icon: Component;
  className: string;
}> = [
  { key: 'wechat', tip: '微信登录', icon: WechatIcon, className: 'is-wechat' },
  { key: 'qq', tip: 'QQ 登录', icon: QqIcon, className: 'is-qq' },
  { key: 'github', tip: 'GitHub 登录', icon: GithubIcon, className: 'is-github' },
  { key: 'gitee', tip: 'Gitee 登录', icon: GiteeIcon, className: 'is-gitee' },
];
</script>

<style scoped lang="scss">
.login-third-party {
  margin-top: 24px;
}

.login-divider {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 18px;
}

.login-divider__line {
  flex: 1;
  height: 1px;
  background: #e5e7eb;
}

.login-divider__text {
  font-size: 13px;
  color: #9ca3af;
  white-space: nowrap;
}

.login-oauth-icons {
  display: flex;
  justify-content: center;
  gap: 16px;
}

.login-oauth-btn {
  display: flex;
  width: 44px;
  height: 44px;
  align-items: center;
  justify-content: center;
  border: 1px solid #e5e7eb;
  border-radius: 50%;
  background: #fff;
  cursor: pointer;
  transition: all 0.2s ease;
}

.login-oauth-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 18px rgb(15 23 42 / 8%);
}

:deep(.is-wechat) {
  color: #07c160;
}

:deep(.is-qq) {
  color: #12b7f5;
}

:deep(.is-github) {
  color: #24292f;
}

:deep(.is-gitee) {
  color: #c71d23;
}

.login-register-row {
  margin-top: 18px;
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
