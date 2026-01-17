<template>
  <div class="system-monitor-container">
    <!-- 系统状态卡片 -->
    <el-row :gutter="20">
      <el-col :xs="24" :sm="12" :md="8" :lg="8">
        <el-card shadow="hover" class="status-card">
          <div class="card-header">
            <el-icon :size="40" :color="systemStatus.color">
              <component :is="systemStatus.icon" />
            </el-icon>
            <div class="card-title">
              <h3>系统状态</h3>
              <p>{{ systemStatus.text }}</p>
            </div>
          </div>
          <div class="card-content">
            <el-tag :type="systemStatus.type" size="large">
              {{ systemStatus.status }}
            </el-tag>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="8" :lg="8">
        <el-card shadow="hover" class="status-card">
          <div class="card-header">
            <el-icon :size="40" :color="databaseStatus.color">
              <component :is="databaseStatus.icon" />
            </el-icon>
            <div class="card-title">
              <h3>数据库</h3>
              <p>{{ databaseStatus.text }}</p>
            </div>
          </div>
          <div class="card-content">
            <el-tag :type="databaseStatus.type" size="large">
              {{ databaseStatus.status }}
            </el-tag>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="8" :lg="8">
        <el-card shadow="hover" class="status-card">
          <div class="card-header">
            <el-icon :size="40" :color="redisStatus.color">
              <component :is="redisStatus.icon" />
            </el-icon>
            <div class="card-title">
              <h3>Redis</h3>
              <p>{{ redisStatus.text }}</p>
            </div>
          </div>
          <div class="card-content">
            <el-tag :type="redisStatus.type" size="large">
              {{ redisStatus.status }}
            </el-tag>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 系统信息 -->
    <el-card shadow="hover" style="margin-top: 20px">
      <template #header>
        <div class="card-header-title">
          <span>系统信息</span>
          <el-button
            type="primary"
            :icon="Refresh"
            @click="refreshData"
            :loading="loading"
          >
            刷新
          </el-button>
        </div>
      </template>

      <el-descriptions :column="2" border>
        <el-descriptions-item label="系统名称">
          {{ systemInfo.name || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="系统版本">
          {{ systemInfo.version || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="API 地址">
          {{ systemInfo.base_url || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="API 前缀">
          {{ systemInfo.api_prefix || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="检查时间" :span="2">
          {{ systemInfo.timestamp || '-' }}
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 健康检查详情 -->
    <el-card shadow="hover" style="margin-top: 20px">
      <template #header>
        <span>健康检查详情</span>
      </template>

      <el-table :data="healthCheckDetails" stripe>
        <el-table-column prop="component" label="组件" width="150" />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="row.status === 'up' ? 'success' : 'danger'">
              {{ row.status === 'up' ? '正常' : '异常' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="error" label="错误信息">
          <template #default="{ row }">
            {{ row.error || '-' }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 快速操作 -->
    <el-card shadow="hover" style="margin-top: 20px">
      <template #header>
        <span>快速操作</span>
      </template>

      <div class="quick-actions">
        <el-button type="primary" :icon="Document" @click="openApiDocs">
          查看 API 文档
        </el-button>
        <el-button type="success" :icon="View" @click="openSwagger">
          Swagger UI
        </el-button>
        <el-button type="info" :icon="Reading" @click="openRedoc">
          ReDoc 文档
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts" name="systemMonitor">
import { ref, reactive, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import {
  Refresh,
  Document,
  View,
  Reading,
  CircleCheck,
  CircleClose,
  Warning,
} from '@element-plus/icons-vue';
import request from '/@/utils/request';
import { useRouter } from 'vue-router';

const router = useRouter();
const loading = ref(false);

// 系统状态
const systemStatus = reactive({
  status: '检查中...',
  text: '系统运行状态',
  type: 'info' as any,
  color: '#409EFF',
  icon: Warning,
});

// 数据库状态
const databaseStatus = reactive({
  status: '检查中...',
  text: 'MySQL 连接状态',
  type: 'info' as any,
  color: '#409EFF',
  icon: Warning,
});

// Redis 状态
const redisStatus = reactive({
  status: '检查中...',
  text: 'Redis 连接状态',
  type: 'info' as any,
  color: '#409EFF',
  icon: Warning,
});

// 系统信息
const systemInfo = reactive({
  name: '',
  version: '',
  base_url: '',
  api_prefix: '',
  timestamp: '',
});

// 健康检查详情
const healthCheckDetails = ref<any[]>([]);

// 获取健康检查数据
const getHealthCheck = async () => {
  try {
    const res = await request({
      url: '/health/health',  // 移除 /api 前缀
      method: 'get',
    });

    if (res.code === 0 && res.data) {
      const data = res.data;

      // 更新系统状态
      if (data.status === 'healthy') {
        systemStatus.status = '正常';
        systemStatus.type = 'success';
        systemStatus.color = '#67C23A';
        systemStatus.icon = CircleCheck;
      } else {
        systemStatus.status = '异常';
        systemStatus.type = 'danger';
        systemStatus.color = '#F56C6C';
        systemStatus.icon = CircleClose;
      }

      // 更新数据库状态
      if (data.checks?.database) {
        if (data.checks.database.status === 'up') {
          databaseStatus.status = '正常';
          databaseStatus.type = 'success';
          databaseStatus.color = '#67C23A';
          databaseStatus.icon = CircleCheck;
        } else {
          databaseStatus.status = '异常';
          databaseStatus.type = 'danger';
          databaseStatus.color = '#F56C6C';
          databaseStatus.icon = CircleClose;
        }
      }

      // 更新 Redis 状态
      if (data.checks?.redis) {
        if (data.checks.redis.status === 'up') {
          redisStatus.status = '正常';
          redisStatus.type = 'success';
          redisStatus.color = '#67C23A';
          redisStatus.icon = CircleCheck;
        } else {
          redisStatus.status = '异常';
          redisStatus.type = 'danger';
          redisStatus.color = '#F56C6C';
          redisStatus.icon = CircleClose;
        }
      }

      // 更新详情列表
      healthCheckDetails.value = Object.entries(data.checks || {}).map(
        ([key, value]: [string, any]) => ({
          component: key === 'database' ? '数据库' : key === 'redis' ? 'Redis' : key,
          status: value.status,
          error: value.error || '',
        })
      );
    }
  } catch (error) {
    console.error('获取健康检查数据失败:', error);
    ElMessage.error('获取健康检查数据失败');
  }
};

// 获取系统信息
const getSystemInfo = async () => {
  try {
    const res = await request({
      url: '/health/info',  // 移除 /api 前缀
      method: 'get',
    });

    if (res.code === 0 && res.data) {
      Object.assign(systemInfo, res.data);
    }
  } catch (error) {
    console.error('获取系统信息失败:', error);
  }
};

// 刷新数据
const refreshData = async () => {
  loading.value = true;
  try {
    await Promise.all([getHealthCheck(), getSystemInfo()]);
    ElMessage.success('刷新成功');
  } finally {
    loading.value = false;
  }
};

// 打开 API 文档
const openApiDocs = () => {
  router.push('/apiDoc/swagger');
};

// 打开 Swagger
const openSwagger = () => {
  router.push('/apiDoc/swagger');
};

// 打开 ReDoc
const openRedoc = () => {
  router.push('/apiDoc/redoc');
};

// 初始化
onMounted(() => {
  refreshData();
});
</script>

<style scoped lang="scss">
.system-monitor-container {
  padding: 20px;

  .status-card {
    .card-header {
      display: flex;
      align-items: center;
      gap: 15px;

      .card-title {
        h3 {
          margin: 0;
          font-size: 18px;
          font-weight: 500;
        }

        p {
          margin: 5px 0 0 0;
          font-size: 14px;
          color: #909399;
        }
      }
    }

    .card-content {
      margin-top: 20px;
      text-align: center;
    }
  }

  .card-header-title {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .quick-actions {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
  }
}
</style>
