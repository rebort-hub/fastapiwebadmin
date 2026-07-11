<template>
  <div class="login-left-view">
    <div class="login-left-view__hero">
      <div class="login-left-view__hero-ring">
        <img :src="logos.main" class="login-left-view__hero-logo" alt="logo" />
      </div>
    </div>
    <div class="login-left-view__desc">
      <h2>企业级后台管理平台</h2>
      <p>支持 RBAC 权限、插件化业务扩展、动态路由与企业级运维能力</p>
    </div>
    <div class="login-left-view__decor login-left-view__decor--circle" />
    <div class="login-left-view__decor login-left-view__decor--square" />
    <div class="login-left-view__decor login-left-view__decor--dot" />
  </div>
</template>

<script setup lang="ts" name="LoginLeftView">
import { logos } from '/@/config/assets';
</script>

<style scoped lang="scss">
.login-left-view {
  position: relative;
  display: flex;
  height: 100%;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px;
  overflow: hidden;
  background: linear-gradient(135deg, #eef2ff 0%, #f8fafc 45%, #ecfeff 100%);
}

.login-left-view__hero {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 32px;
}

.login-left-view__hero-ring {
  display: flex;
  width: 160px;
  height: 160px;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgb(255 255 255 / 72%);
  box-shadow: 0 18px 40px rgb(93 135 255 / 18%);
}

.login-left-view__hero-logo {
  width: 72px;
  height: 72px;
  object-fit: contain;
}

.login-left-view__desc {
  max-width: 420px;
  text-align: center;
}

.login-left-view__desc h2 {
  margin: 0 0 12px;
  font-size: 28px;
  font-weight: 600;
  color: #1f2937;
}

.login-left-view__desc p {
  margin: 0;
  font-size: 14px;
  line-height: 1.7;
  color: #6b7280;
}

.login-left-view__decor {
  position: absolute;
  pointer-events: none;
}

.login-left-view__decor--circle {
  top: 12%;
  left: 10%;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: rgb(93 135 255 / 10%);
}

.login-left-view__decor--square {
  right: 12%;
  bottom: 18%;
  width: 88px;
  height: 88px;
  border-radius: 18px;
  background: rgb(16 185 129 / 10%);
  transform: rotate(18deg);
}

.login-left-view__decor--dot {
  top: 22%;
  right: 18%;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #5d87ff;
  opacity: 0.45;
}
</style>
