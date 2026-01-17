<template>
  <div class="home-container">
    <!-- 顶部欢迎区域 -->
    <el-card class="welcome-card" shadow="never">
      <div class="welcome-content">
        <div class="welcome-left">
          <h2 class="welcome-title">你好，{{ userInfo.nickname || '管理员' }}</h2>
          <p class="welcome-desc">{{ greetingText }}，欢迎回来！</p>
        </div>
        <div class="welcome-right">
          <span class="welcome-time">{{ currentDate }}</span>
        </div>
      </div>
    </el-card>

    <!-- 数据统计卡片 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6" :lg="6" :xl="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon user-icon">
              <el-icon :size="32"><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.users }}</div>
              <div class="stat-label">用户总数</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6" :lg="6" :xl="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon menu-icon">
              <el-icon :size="32"><Menu /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.menus }}</div>
              <div class="stat-label">菜单数量</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6" :lg="6" :xl="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon role-icon">
              <el-icon :size="32"><Avatar /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.roles }}</div>
              <div class="stat-label">角色数量</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6" :lg="6" :xl="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon online-icon">
              <el-icon :size="32"><Clock /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.online }}</div>
              <div class="stat-label">在线用户</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 内容区域 -->
    <el-row :gutter="16" class="content-row">
      <!-- 系统信息 -->
      <el-col :xs="24" :sm="24" :md="16" :lg="16" :xl="16">
        <el-card shadow="never" class="info-card">
          <template #header>
            <div class="card-header">
              <el-icon><InfoFilled /></el-icon>
              <span>系统信息</span>
            </div>
          </template>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="系统名称">后台管理系统</el-descriptions-item>
            <el-descriptions-item label="系统版本">v1.0.0</el-descriptions-item>
            <el-descriptions-item label="开发框架">Vue 3 + FastAPI</el-descriptions-item>
            <el-descriptions-item label="UI 框架">Element Plus</el-descriptions-item>
            <el-descriptions-item label="服务器时间" :span="2">{{ currentTime }}</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <!-- 快速操作 -->
        <el-card shadow="never" class="quick-actions-card">
          <template #header>
            <div class="card-header">
              <el-icon><Operation /></el-icon>
              <span>快速操作</span>
            </div>
          </template>
          <div class="quick-actions">
            <el-button type="primary" :icon="User" @click="goToPage('/system/user')">
              用户管理
            </el-button>
            <el-button type="success" :icon="Menu" @click="goToPage('/system/menu')">
              菜单管理
            </el-button>
            <el-button type="warning" :icon="Avatar" @click="goToPage('/system/role')">
              角色管理
            </el-button>
            <el-button type="info" :icon="Setting" @click="goToPage('/system/user')">
              系统设置
            </el-button>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧栏 -->
      <el-col :xs="24" :sm="24" :md="8" :lg="8" :xl="8">
        <!-- 通知公告 -->
        <el-card shadow="never" class="notice-card">
          <template #header>
            <div class="card-header">
              <el-icon><Bell /></el-icon>
              <span>通知公告</span>
            </div>
          </template>
          <el-empty v-if="notices.length === 0" description="暂无通知" :image-size="80" />
          <div v-else class="notice-list">
            <div v-for="(notice, index) in notices" :key="index" class="notice-item">
              <el-icon class="notice-icon"><Bell /></el-icon>
              <div class="notice-content">
                <div class="notice-title">{{ notice.title }}</div>
                <div class="notice-time">{{ notice.time }}</div>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 待办事项 -->
        <el-card shadow="never" class="todo-card">
          <template #header>
            <div class="card-header">
              <el-icon><List /></el-icon>
              <span>待办事项</span>
            </div>
          </template>
          <el-empty v-if="todos.length === 0" description="暂无待办" :image-size="80" />
          <div v-else class="todo-list">
            <div v-for="(todo, index) in todos" :key="index" class="todo-item">
              <el-checkbox v-model="todo.done" />
              <span :class="{ 'todo-done': todo.done }">{{ todo.text }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts" name="home">
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { storeToRefs } from 'pinia';
import { useUserStore } from '/@/stores/user';
import { 
  User, 
  Menu, 
  Avatar, 
  Clock, 
  InfoFilled, 
  Operation, 
  Bell, 
  List,
  Setting 
} from '@element-plus/icons-vue';

const router = useRouter();
const userStore = useUserStore();
const { userInfos: userInfo } = storeToRefs(userStore);

// 统计数据
const stats = ref({
  users: 0,
  menus: 0,
  roles: 0,
  online: 0
});

// 当前时间
const currentTime = ref('');
const currentDate = ref('');

// 通知列表
const notices = ref([
  { title: '系统更新通知', time: '2026-01-16 10:00' },
  { title: '欢迎使用后台管理系统', time: '2026-01-16 09:00' }
]);

// 待办事项
const todos = ref([
  { text: '完善个人信息', done: false },
  { text: '查看系统文档', done: false }
]);

// 问候语
const greetingText = computed(() => {
  const hour = new Date().getHours();
  if (hour < 6) return '凌晨好';
  if (hour < 9) return '早上好';
  if (hour < 12) return '上午好';
  if (hour < 14) return '中午好';
  if (hour < 17) return '下午好';
  if (hour < 19) return '傍晚好';
  if (hour < 22) return '晚上好';
  return '夜深了';
});

// 更新时间
const updateTime = () => {
  const now = new Date();
  currentTime.value = now.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  });
  
  currentDate.value = now.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long'
  });
};

// 定时器
let timer: any = null;

// 跳转页面
const goToPage = (path: string) => {
  router.push(path);
};

// 模拟加载统计数据
const loadStats = () => {
  // 这里后续可以对接真实的API
  stats.value = {
    users: 156,
    menus: 28,
    roles: 5,
    online: 12
  };
};

onMounted(() => {
  updateTime();
  loadStats();
  // 每秒更新时间
  timer = setInterval(updateTime, 1000);
});

onUnmounted(() => {
  if (timer) {
    clearInterval(timer);
  }
});
</script>

<style scoped lang="scss">
.home-container {
  padding: 16px;
  background-color: #f0f2f5;
  min-height: calc(100vh - 50px);

  // 欢迎卡片
  .welcome-card {
    margin-bottom: 16px;
    border-radius: 8px;

    :deep(.el-card__body) {
      padding: 20px;
    }

    .welcome-content {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .welcome-left {
        .welcome-title {
          margin: 0 0 8px 0;
          font-size: 24px;
          font-weight: 500;
          color: #303133;
        }

        .welcome-desc {
          margin: 0;
          font-size: 14px;
          color: #909399;
        }
      }

      .welcome-right {
        .welcome-time {
          font-size: 14px;
          color: #606266;
        }
      }
    }
  }

  // 统计卡片行
  .stats-row {
    margin-bottom: 16px;

    .stat-card {
      margin-bottom: 16px;
      border-radius: 8px;
      transition: all 0.3s;

      &:hover {
        transform: translateY(-4px);
      }

      :deep(.el-card__body) {
        padding: 20px;
      }

      .stat-content {
        display: flex;
        align-items: center;

        .stat-icon {
          width: 56px;
          height: 56px;
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          margin-right: 16px;
          color: white;

          &.user-icon {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          }

          &.menu-icon {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
          }

          &.role-icon {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
          }

          &.online-icon {
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
          }
        }

        .stat-info {
          flex: 1;

          .stat-value {
            font-size: 28px;
            font-weight: 600;
            color: #303133;
            line-height: 1;
            margin-bottom: 8px;
          }

          .stat-label {
            font-size: 14px;
            color: #909399;
          }
        }
      }
    }
  }

  // 内容行
  .content-row {
    .info-card,
    .quick-actions-card,
    .notice-card,
    .todo-card {
      margin-bottom: 16px;
      border-radius: 8px;

      .card-header {
        display: flex;
        align-items: center;
        gap: 8px;
        font-weight: 500;
        font-size: 16px;
      }
    }

    // 快速操作
    .quick-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;

      .el-button {
        flex: 1;
        min-width: 120px;
      }
    }

    // 通知列表
    .notice-list {
      .notice-item {
        display: flex;
        align-items: flex-start;
        padding: 12px 0;
        border-bottom: 1px solid #f0f0f0;

        &:last-child {
          border-bottom: none;
        }

        .notice-icon {
          color: #409eff;
          margin-right: 12px;
          margin-top: 2px;
        }

        .notice-content {
          flex: 1;

          .notice-title {
            font-size: 14px;
            color: #303133;
            margin-bottom: 4px;
          }

          .notice-time {
            font-size: 12px;
            color: #909399;
          }
        }
      }
    }

    // 待办列表
    .todo-list {
      .todo-item {
        display: flex;
        align-items: center;
        padding: 12px 0;
        border-bottom: 1px solid #f0f0f0;

        &:last-child {
          border-bottom: none;
        }

        span {
          margin-left: 12px;
          font-size: 14px;
          color: #303133;

          &.todo-done {
            text-decoration: line-through;
            color: #909399;
          }
        }
      }
    }
  }
}
</style>
