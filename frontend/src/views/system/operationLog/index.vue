<template>
  <div class="system-operation-log-container app-container">
    <el-card>
      <div class="search-bar mb15">
        <el-input v-model="state.listQuery.username" placeholder="用户名" style="max-width: 160px" clearable />
        <el-input v-model="state.listQuery.request_path" placeholder="请求路径" style="max-width: 180px" class="ml10" clearable />
        <el-input v-model="state.listQuery.request_ip" placeholder="请求IP" style="max-width: 160px" class="ml10" clearable />
        <el-button type="primary" class="ml10" @click="search">查询</el-button>
      </div>
      <synrebort-table
        :columns="state.columns"
        :data="state.listData"
        ref="tableRef"
        v-model:page-size="state.listQuery.pageSize"
        v-model:page="state.listQuery.page"
        :total="state.total"
        @pagination-change="getList"
      />
    </el-card>
  </div>
</template>

<script lang="ts" setup>
defineOptions({ name: 'SystemOperationLog' })
import { h, onMounted, reactive, ref } from 'vue';
import { ElTag } from 'element-plus';
import { useOperationLogApi } from '/@/api/useSystemApi/operationLog';

const tableRef = ref();

const state = reactive({
  columns: [
    { key: 'username', label: '用户', width: '120', align: 'center', show: true },
    { key: 'request_method', label: '方法', width: '90', align: 'center', show: true },
    { key: 'request_path', label: '请求路径', width: '220', align: 'left', show: true },
    { key: 'request_ip', label: 'IP', width: '130', align: 'center', show: true },
    { key: 'location', label: '操作地址', width: '180', align: 'center', show: true },
    { key: 'browser', label: '浏览器', width: '120', align: 'center', show: true },
    { key: 'os_name', label: '系统', width: '120', align: 'center', show: true },
    {
      key: 'status', label: '状态', width: '90', align: 'center', show: true,
      render: (row: any) => h(ElTag, { type: row.status === 1 ? 'success' : 'danger' }, () => row.status === 1 ? '成功' : '失败'),
    },
    { key: 'process_time', label: '耗时', width: '90', align: 'center', show: true },
    { key: 'description', label: '描述', width: '160', align: 'center', show: true },
    { key: 'creation_date', label: '时间', width: '', align: 'center', show: true },
  ],
  listData: [] as any[],
  total: 0,
  listQuery: {
    page: 1,
    pageSize: 20,
    username: '',
    request_path: '',
    request_ip: '',
  },
});

const getList = () => {
  tableRef.value.openLoading();
  useOperationLogApi()
    .getList(state.listQuery)
    .then((res) => {
      state.listData = res.data.rows;
      state.total = res.data.rowTotal;
    })
    .finally(() => tableRef.value.closeLoading());
};

const search = () => {
  state.listQuery.page = 1;
  getList();
};

onMounted(() => getList());
</script>

<style scoped>
.search-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
}
.ml10 {
  margin-left: 10px;
}
.mb15 {
  margin-bottom: 15px;
}
</style>
