<template>
  <div class="system-dept-container app-container">
    <el-card>
      <div class="system-dept-search mb15">
        <el-button v-auth="'dept:add'" type="success" @click="onOpenAddDept('add', null)">新增部门</el-button>
      </div>
      <el-table
        :data="state.tableData.data"
        v-loading="state.tableData.loading"
        style="width: 100%"
        row-key="id"
        default-expand-all
        :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
      >
        <el-table-column prop="name" label="部门名称" show-overflow-tooltip width="300"></el-table-column>
        <el-table-column prop="sort" label="排序" show-overflow-tooltip width="100" align="center"></el-table-column>
        <el-table-column prop="status" label="部门状态" show-overflow-tooltip width="120" align="center">
          <template #default="scope">
            <el-tag type="success" v-if="scope.row.status === 1">启用</el-tag>
            <el-tag type="info" v-else>禁用</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="部门描述" show-overflow-tooltip></el-table-column>
        <el-table-column prop="creation_date" label="创建时间" show-overflow-tooltip width="160" align="center"></el-table-column>
        <el-table-column label="操作" show-overflow-tooltip width="280" align="center" fixed="right">
          <template #default="scope">
            <el-button v-auth="'dept:add'" size="small" type="primary" @click="onOpenAddDept('add', scope.row)">新增</el-button>
            <el-button v-auth="'dept:edit'" size="small" type="primary" @click="onOpenEditDept('edit', scope.row)">编辑</el-button>
            <el-button 
              v-auth="'dept:disable'"
              size="small" 
              :type="scope.row.status === 1 ? 'warning' : 'success'" 
              @click="toggleStatus(scope.row)"
            >
              {{ scope.row.status === 1 ? '禁用' : '启用' }}
            </el-button>
            <el-button v-auth="'dept:delete'" size="small" type="danger" @click="onTabelRowDel(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    <DeptDialog ref="deptDialogRef" @refresh="getTableData()" />
  </div>
</template>

<script setup lang="ts" name="systemDept">
import { defineAsyncComponent, ref, reactive, onMounted } from 'vue';
import { ElMessageBox, ElMessage } from 'element-plus';
import { useDepartmentApi } from '/@/api/useSystemApi/department';
import { auth as authFunction } from '/@/utils/authFunction';

// 引入组件
const DeptDialog = defineAsyncComponent(() => import('/@/views/system/dept/dialog.vue'));

// 定义变量内容
const deptDialogRef = ref();
const state = reactive({
  tableData: {
    data: [],
    total: 0,
    loading: false,
  },
});

// 初始化表格数据
const getTableData = () => {
  state.tableData.loading = true;
  useDepartmentApi().getList()
    .then(res => {
      state.tableData.data = res.data || [];
    })
    .finally(() => {
      state.tableData.loading = false;
    });
};

// 打开新增部门弹窗
const onOpenAddDept = (type: string, row: any) => {
  deptDialogRef.value.openDialog(type, row);
};

// 打开编辑部门弹窗
const onOpenEditDept = (type: string, row: any) => {
  deptDialogRef.value.openDialog(type, row);
};

// 启用/禁用部门
const toggleStatus = (row: any) => {
  const action = row.status === 1 ? '禁用' : '启用';
  ElMessageBox.confirm(`确定要${action}该部门吗？`, '提示', {
    confirmButtonText: '确认',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(() => {
      const updatedRow = {
        ...row,
        status: row.status === 1 ? 0 : 1
      };
      useDepartmentApi().saveOrUpdate(updatedRow)
        .then(() => {
          ElMessage.success(`${action}成功`);
          getTableData();
        })
        .catch((error) => {
          ElMessage.error(error.response?.data?.msg || `${action}失败`);
        });
    })
    .catch(() => {});
};

// 删除当前行
const onTabelRowDel = (row: any) => {
  ElMessageBox.confirm(`此操作将永久删除部门：${row.name}, 是否继续?`, '提示', {
    confirmButtonText: '删除',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(() => {
      useDepartmentApi().deleted({ id: row.id })
        .then(() => {
          ElMessage.success('删除成功');
          getTableData();
        })
        .catch((error) => {
          ElMessage.error(error.response?.data?.msg || '删除失败');
        });
    })
    .catch(() => {});
};

// 页面加载时
onMounted(() => {
  getTableData();
});
</script>
