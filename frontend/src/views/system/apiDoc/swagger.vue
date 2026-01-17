<template>
  <div class="api-doc-container">
    <iframe 
      :src="iframeSrc" 
      frameborder="0" 
      class="api-doc-iframe"
      @load="handleLoad"
    ></iframe>
    <div v-if="loading" class="loading-mask">
      <el-icon class="is-loading">
        <Loading />
      </el-icon>
      <span>加载中...</span>
    </div>
  </div>
</template>

<script setup lang="ts" name="swaggerDoc">
import { ref, onMounted } from 'vue';
import { getBaseApiUrl } from '/@/utils/config';
import { Loading } from '@element-plus/icons-vue';

const iframeSrc = ref('');
const loading = ref(true);

onMounted(() => {
  // 使用 getBaseApiUrl() 而不是 getApiBaseUrl()
  // 因为 /docs 路由不需要 /api 前缀
  const baseUrl = getBaseApiUrl();
  iframeSrc.value = `${baseUrl}/docs`;
  console.log('Swagger iframe URL:', iframeSrc.value);
});

const handleLoad = () => {
  loading.value = false;
};
</script>

<style scoped lang="scss">
.api-doc-container {
  position: relative;
  width: 100%;
  height: calc(100vh - 50px);
  overflow: hidden;

  .api-doc-iframe {
    width: 100%;
    height: 100%;
    border: none;
  }

  .loading-mask {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background-color: rgba(255, 255, 255, 0.9);
    z-index: 1000;

    .el-icon {
      font-size: 40px;
      margin-bottom: 10px;
      color: var(--el-color-primary);
    }

    span {
      font-size: 14px;
      color: #666;
    }
  }
}
</style>
