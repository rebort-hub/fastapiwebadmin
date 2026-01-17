<template>
  <div class="file-management-container">
    <el-card shadow="hover">
      <!-- 操作栏 -->
      <div class="toolbar">
        <el-upload
          :action="uploadUrl"
          :headers="uploadHeaders"
          :on-success="handleUploadSuccess"
          :on-error="handleUploadError"
          :before-upload="beforeUpload"
          :show-file-list="false"
          multiple
        >
          <el-button type="primary" :icon="Upload">上传文件</el-button>
        </el-upload>
        
        <el-button :icon="Refresh" @click="getFileList">刷新</el-button>
        
        <div class="search-box">
          <el-input
            v-model="searchText"
            placeholder="搜索文件名"
            :prefix-icon="Search"
            clearable
            @clear="getFileList"
            @keyup.enter="getFileList"
            style="width: 300px"
          />
          <el-button type="primary" :icon="Search" @click="getFileList">搜索</el-button>
        </div>
      </div>

      <!-- 文件列表 -->
      <el-table
        v-loading="loading"
        :data="fileList"
        stripe
        style="width: 100%; margin-top: 20px"
      >
        <el-table-column type="index" label="序号" width="60" />
        
        <el-table-column prop="original_name" label="文件名" min-width="200">
          <template #default="{ row }">
            <el-tooltip :content="row.original_name" placement="top">
              <span class="file-name">{{ row.original_name }}</span>
            </el-tooltip>
          </template>
        </el-table-column>
        
        <el-table-column prop="extend_name" label="类型" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ row.extend_name || '-' }}</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="file_size" label="大小" width="120">
          <template #default="{ row }">
            {{ formatFileSize(row.file_size) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="creation_date" label="上传时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.creation_date) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              :icon="Download"
              @click="downloadFile(row)"
              link
            >
              下载
            </el-button>
            <el-button
              type="danger"
              size="small"
              :icon="Delete"
              @click="deleteFile(row)"
              link
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="getFileList"
          @current-change="getFileList"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts" name="fileManagement">
import { ref, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Upload, Refresh, Search, Download, Delete } from '@element-plus/icons-vue';
import { getBaseApiUrl } from '/@/utils/config';
import { Session } from '/@/utils/storage';
import request from '/@/utils/request';

// 数据
const loading = ref(false);
const fileList = ref<any[]>([]);
const searchText = ref('');
const page = ref(1);
const pageSize = ref(20);
const total = ref(0);

// 上传配置
const uploadUrl = ref(`${getBaseApiUrl()}/api/file/upload`);
const uploadHeaders = ref({
  token: Session.get('token') || '',
});

// 获取文件列表
const getFileList = async () => {
  loading.value = true;
  try {
    const res = await request({
      url: '/file/list',
      method: 'post',
      data: {
        page: page.value,
        pageSize: pageSize.value,
        name: searchText.value,
      },
    });
    
    if (res.code === 0) {
      fileList.value = res.data.rows || [];
      total.value = res.data.rowTotal || 0;
      console.log('文件列表数据:', fileList.value); // 调试用
    }
  } catch (error) {
    console.error('获取文件列表失败:', error);
  } finally {
    loading.value = false;
  }
};

// 上传前检查
const beforeUpload = (file: File) => {
  const maxSize = 100 * 1024 * 1024; // 100MB
  if (file.size > maxSize) {
    ElMessage.error('文件大小不能超过 100MB');
    return false;
  }
  return true;
};

// 上传成功
const handleUploadSuccess = (response: any) => {
  if (response.code === 0) {
    ElMessage.success('上传成功');
    getFileList();
  } else {
    ElMessage.error(response.msg || '上传失败');
  }
};

// 上传失败
const handleUploadError = () => {
  ElMessage.error('上传失败');
};

// 下载文件
const downloadFile = (row: any) => {
  const url = `${getBaseApiUrl()}/api/file/download/${row.id}`;
  const link = document.createElement('a');
  link.href = url;
  link.download = row.original_name;
  link.click();
};

// 删除文件
const deleteFile = (row: any) => {
  ElMessageBox.confirm(`确定要删除文件 "${row.original_name}" 吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    try {
      const res = await request({
        url: '/file/deleted',  // 移除 /api 前缀
        method: 'post',
        data: { id: row.id },
      });
      
      if (res.code === 0) {
        ElMessage.success('删除成功');
        getFileList();
      } else {
        ElMessage.error(res.msg || '删除失败');
      }
    } catch (error) {
      ElMessage.error('删除失败');
    }
  }).catch(() => {});
};

// 格式化文件大小
const formatFileSize = (size: string | number) => {
  if (!size) return '-';
  // 如果是字符串，转换为数字（KB）
  const sizeInKB = typeof size === 'string' ? parseFloat(size) : size;
  if (isNaN(sizeInKB)) return '-';
  
  if (sizeInKB < 1) return (sizeInKB * 1024).toFixed(2) + ' B';
  if (sizeInKB < 1024) return sizeInKB.toFixed(2) + ' KB';
  if (sizeInKB < 1024 * 1024) return (sizeInKB / 1024).toFixed(2) + ' MB';
  return (sizeInKB / 1024 / 1024).toFixed(2) + ' GB';
};

// 格式化日期
const formatDate = (date: string) => {
  if (!date) return '-';
  return new Date(date).toLocaleString('zh-CN');
};

// 初始化
onMounted(() => {
  getFileList();
});
</script>

<style scoped lang="scss">
.file-management-container {
  padding: 20px;

  .toolbar {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;

    .search-box {
      display: flex;
      gap: 10px;
      margin-left: auto;
    }
  }

  .file-name {
    display: inline-block;
    max-width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .pagination {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>
