<template>
  <div class="file-management-container">
    <el-card shadow="hover">
      <div class="stats-row" v-if="storageConfig.storage_type">
        <div class="stat-item">
          <div class="stat-value">{{ statistics.total_count || 0 }}</div>
          <div class="stat-label">文件总数</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ formatFileSize(statistics.total_size_kb) }}</div>
          <div class="stat-label">总大小</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ storageConfig.storage_label || storageConfig.storage_type }}</div>
          <div class="stat-label">当前存储</div>
        </div>
        <div class="stat-item">
          <div class="stat-value">{{ storageConfig.max_size }}MB</div>
          <div class="stat-label">单文件上限</div>
        </div>
      </div>

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

        <el-button v-if="selectedIds.length" type="danger" plain @click="batchDelete">
          批量删除 ({{ selectedIds.length }})
        </el-button>

        <el-button :icon="Refresh" @click="refreshAll">刷新</el-button>

        <div class="search-box">
          <el-select v-model="storageType" placeholder="存储类型" clearable style="width: 140px" @change="getFileList">
            <el-option v-for="item in storageConfig.providers || []" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
          <el-input
            v-model="searchText"
            placeholder="搜索文件名"
            :prefix-icon="Search"
            clearable
            style="width: 220px"
            @keyup.enter="getFileList"
          />
          <el-button type="primary" :icon="Search" @click="getFileList">搜索</el-button>
        </div>
      </div>

      <el-table
        v-loading="loading"
        :data="fileList"
        stripe
        style="width: 100%; margin-top: 20px"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="48" />
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="original_name" label="文件名" min-width="200" show-overflow-tooltip />
        <el-table-column prop="storage_type" label="存储" width="120">
          <template #default="{ row }">
            <el-tag size="small">{{ STORAGE_TYPE_LABELS[row.storage_type] || row.storage_type || 'local' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="extend_name" label="类型" width="90">
          <template #default="{ row }">
            <el-tag size="small" type="info">{{ row.extend_name || '-' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="file_size" label="大小" width="110">
          <template #default="{ row }">{{ formatFileSize(row.file_size) }}</template>
        </el-table-column>
        <el-table-column prop="uploader_name" label="上传者" width="110" />
        <el-table-column prop="creation_date" label="上传时间" width="170">
          <template #default="{ row }">{{ formatDate(row.creation_date) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" :icon="Download" link @click="downloadFile(row)">下载</el-button>
            <el-button type="danger" size="small" :icon="Delete" link @click="deleteFile(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

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
import { onMounted, ref } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Upload, Refresh, Search, Download, Delete } from '@element-plus/icons-vue';
import { getBaseApiUrl } from '/@/utils/config';
import { Session } from '/@/utils/storage';
import { STORAGE_TYPE_LABELS, useFileApi } from '/@/api/useSystemApi/file';

const loading = ref(false);
const fileList = ref<any[]>([]);
const searchText = ref('');
const storageType = ref('');
const page = ref(1);
const pageSize = ref(20);
const total = ref(0);
const selectedIds = ref<string[]>([]);
const statistics = ref<any>({});
const storageConfig = ref<any>({});

const uploadUrl = ref(`${getBaseApiUrl()}/api/file/upload`);
const uploadHeaders = ref({ token: Session.get('token') || '' });

const loadMeta = async () => {
  const [statRes, cfgRes] = await Promise.all([
    useFileApi().getStatistics(),
    useFileApi().getStorageConfig(),
  ]);
  statistics.value = statRes.data || {};
  storageConfig.value = cfgRes.data || {};
};

const getFileList = async () => {
  loading.value = true;
  try {
    const res = await useFileApi().getList({
      page: page.value,
      pageSize: pageSize.value,
      name: searchText.value,
      storage_type: storageType.value || undefined,
    });
    fileList.value = res.data.rows || [];
    total.value = res.data.rowTotal || 0;
  } finally {
    loading.value = false;
  }
};

const refreshAll = async () => {
  await loadMeta();
  await getFileList();
};

const handleSelectionChange = (rows: any[]) => {
  selectedIds.value = rows.map((r) => r.id);
};

const beforeUpload = (file: File) => {
  const maxSize = (storageConfig.value.max_size || 100) * 1024 * 1024;
  if (file.size > maxSize) {
    ElMessage.error(`文件大小不能超过 ${storageConfig.value.max_size || 100}MB`);
    return false;
  }
  return true;
};

const handleUploadSuccess = (response: any) => {
  if (response.code === 0) {
    ElMessage.success('上传成功');
    refreshAll();
  } else {
    ElMessage.error(response.msg || '上传失败');
  }
};

const handleUploadError = () => ElMessage.error('上传失败');

const downloadFile = (row: any) => {
  const url = row.file_url?.startsWith('http')
    ? row.file_url
    : `${getBaseApiUrl()}/api/file/download/${row.id}`;
  window.open(url, '_blank');
};

const deleteFile = (row: any) => {
  ElMessageBox.confirm(`确定删除文件 "${row.original_name}" 吗？`, '提示', { type: 'warning' })
    .then(async () => {
      await useFileApi().deleted({ id: row.id });
      ElMessage.success('删除成功');
      refreshAll();
    })
    .catch(() => {});
};

const batchDelete = () => {
  ElMessageBox.confirm(`确定删除选中的 ${selectedIds.value.length} 个文件吗？`, '提示', { type: 'warning' })
    .then(async () => {
      await useFileApi().deleteList({ ids: selectedIds.value });
      ElMessage.success('批量删除成功');
      selectedIds.value = [];
      refreshAll();
    })
    .catch(() => {});
};

const formatFileSize = (size: string | number) => {
  if (!size) return '-';
  const sizeInKB = typeof size === 'string' ? parseFloat(size) : size;
  if (isNaN(sizeInKB)) return '-';
  if (sizeInKB < 1) return (sizeInKB * 1024).toFixed(2) + ' B';
  if (sizeInKB < 1024) return sizeInKB.toFixed(2) + ' KB';
  if (sizeInKB < 1024 * 1024) return (sizeInKB / 1024).toFixed(2) + ' MB';
  return (sizeInKB / 1024 / 1024).toFixed(2) + ' GB';
};

const formatDate = (date: string) => (date ? new Date(date).toLocaleString('zh-CN') : '-');

onMounted(() => refreshAll());
</script>

<style scoped lang="scss">
.file-management-container {
  padding: 20px;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.stat-item {
  padding: 16px;
  border-radius: 8px;
  background: #f8fafc;
  text-align: center;
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
}

.stat-label {
  margin-top: 6px;
  font-size: 13px;
  color: #6b7280;
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.search-box {
  display: flex;
  gap: 10px;
  margin-left: auto;
  flex-wrap: wrap;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
