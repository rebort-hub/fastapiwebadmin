<template>
  <div class="system-project-container app-container">
    <el-card>
      <div class="system-project-search mb15">
        <el-input v-model="state.listQuery.name" placeholder="请输入项目名称" style="max-width: 180px"></el-input>
        <el-button v-auth="'project:query'" type="primary" class="ml10" @click="search">查询</el-button>
        <el-button v-auth="'project:add'" type="success" class="ml10" @click="onOpenSaveOrUpdate('save', null)">新增</el-button>
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
    <EditProject @getList="getList" ref="EditProjectRef"/>
  </div>
</template>

<script lang="ts" setup name="SystemProject">
import {h, onMounted, reactive, ref} from 'vue';
import {ElButton, ElMessage, ElMessageBox} from 'element-plus';
import EditProject from '/@/views/system/project/EditProject.vue';
import {useProjectApi} from '/@/api/useSystemApi/project';
import {auth as authFunction} from '/@/utils/authFunction';

interface TableDataRow {
  id: number;
  name: string;
  description: string;
  created_by_name: string;
  updated_by_name: string;
  creation_date: string;
  updation_date: string;
}

interface listQueryRow {
  page: number;
  pageSize: number;
  name: string;
}

interface StateRow {
  columns: Array<any>;
  listData: Array<TableDataRow>;
  total: number;
  listQuery: listQueryRow;
}

const EditProjectRef = ref()
const tableRef = ref()

const state = reactive<StateRow>({
  columns: [
    {
      key: 'name', label: '项目名称', width: '', align: 'center', show: true,
      render: (row: any) => h(ElButton, {
        link: true,
        type: "primary",
        onClick: () => {
          onOpenSaveOrUpdate("update", row)
        }
      }, () => row.name)
    },
    {key: 'description', label: '项目描述', width: '', align: 'center', show: true},
    {key: 'created_by_name', label: '创建人', width: '120', align: 'center', show: true},
    {key: 'creation_date', label: '创建时间', width: '150', align: 'center', show: true},
    {key: 'updated_by_name', label: '更新人', width: '120', align: 'center', show: true},
    {key: 'updation_date', label: '更新时间', width: '150', align: 'center', show: true},
    {
      label: '操作',
      columnType: 'string',
      fixed: 'right',
      align: 'center',
      width: '180',
      render: (row: any) => h("div", null, [
        h(ElButton, {
          type: "primary",
          size: "small",
          onClick: () => {
            onOpenSaveOrUpdate('update', row)
          },
          style: authFunction('project:edit') ? '' : 'display:none'
        }, () => '编辑'),
        h(ElButton, {
          type: "danger",
          size: "small",
          onClick: () => {
            deleted(row)
          },
          style: authFunction('project:delete') ? '' : 'display:none'
        }, () => '删除')
      ])
    },
  ],
  listData: [],
  total: 0,
  listQuery: {
    page: 1,
    pageSize: 20,
    name: '',
  }
});

const getList = () => {
  tableRef.value.openLoading()
  useProjectApi().getList(state.listQuery)
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

const onOpenSaveOrUpdate = (editType: string, row?: TableDataRow) => {
  EditProjectRef.value.openDialog(editType, row);
};

const deleted = (row: TableDataRow) => {
  ElMessageBox.confirm('是否删除该项目, 是否继续?', '提示', {
    confirmButtonText: '确认',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(() => {
      useProjectApi().deleted({id: row.id})
        .then(() => {
          ElMessage.success('删除成功');
          getList()
        })
    })
    .catch(() => {
    });
};

onMounted(() => {
  getList();
});

</script>
