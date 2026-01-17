<template>
  <div class="system-login-record-container app-container">
    <el-card>
      <div class="system-login-record-search mb15">
        <el-input v-model="state.listQuery.code" placeholder="请输入账号" style="max-width: 180px"></el-input>
        <el-input v-model="state.listQuery.user_name" placeholder="请输入用户名称" style="max-width: 180px" class="ml10"></el-input>
        <el-input v-model="state.listQuery.login_ip" placeholder="请输入登录IP" style="max-width: 180px" class="ml10"></el-input>
        <el-button v-auth="'loginRecord:query'" type="primary" class="ml10" @click="search">查询</el-button>
      </div>
      <z-table
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

<script lang="ts" setup name="SystemLoginRecord">
import {h, onMounted, reactive, ref} from 'vue';
import {ElTag} from 'element-plus';
import {useLoginRecordApi} from '/@/api/useSystemApi/loginRecord';

interface TableDataRow {
  id: number;
  token: string;
  code: string;
  user_id: number;
  user_name: string;
  logout_type: string;
  login_type: string;
  login_time: string;
  logout_time: string;
  login_ip: string;
  ret_msg: string;
  ret_code: string;
  address: string;
  source_type: string;
}

interface listQueryRow {
  page: number;
  pageSize: number;
  code: string;
  user_name: string;
  login_ip: string;
}

interface StateRow {
  columns: Array<any>;
  listData: Array<TableDataRow>;
  total: number;
  listQuery: listQueryRow;
}

const tableRef = ref()

const state = reactive<StateRow>({
  columns: [
    {key: 'code', label: '账号', width: '150', align: 'center', show: true},
    {key: 'user_name', label: '用户名称', width: '150', align: 'center', show: true},
    {key: 'login_ip', label: '登录IP', width: '180', align: 'center', show: true},
    {key: 'login_type', label: '登录方式', width: '120', align: 'center', show: true},
    {
      key: 'ret_code', label: '登录状态', width: '120', align: 'center', show: true,
      render: (row: any) => {
        const isSuccess = row.ret_code === '0' || row.ret_code === 0 || row.ret_code === null;
        return h(ElTag, {
          type: isSuccess ? "success" : "danger",
        }, () => isSuccess ? "成功" : "失败")
      }
    },
    {key: 'login_time', label: '登录时间', width: '', align: 'center', show: true},
    {key: 'logout_time', label: '登出时间', width: '', align: 'center', show: true},
  ],
  listData: [],
  total: 0,
  listQuery: {
    page: 1,
    pageSize: 20,
    code: '',
    user_name: '',
    login_ip: '',
  }
});

const getList = () => {
  tableRef.value.openLoading()
  useLoginRecordApi().getList(state.listQuery)
    .then(res => {
      state.listData = res.data.rows
      state.total = res.data.rowTotal
    })
    .finally(() => {
      tableRef.value.closeLoading()
    })
};

const search = () => {
  state.listQuery.page = 1
  getList()
}

onMounted(() => {
  getList();
});

</script>
