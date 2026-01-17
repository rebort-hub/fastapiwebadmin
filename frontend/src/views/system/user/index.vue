<template>
  <div class="system-user-container app-container">
    <el-card>
      <div class="system-user-search mb15">
        <el-input v-model="state.listQuery.username" placeholder="请输入用户名称" style="max-width: 180px"></el-input>
        <el-button type="primary" class="ml10" @click="search">查询
        </el-button>
        <el-button type="success" class="ml10" @click="onOpenSaveOrUpdate('save', null)">
          新增
        </el-button>
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
    <SaveOrUpdateUser @getList="getList" :roleList="state.roleList" ref="SaveOrUpdateUserRef"/>
  </div>
</template>

<script lang="ts" setup name="SystemUser">
import {h, onMounted, reactive, ref} from 'vue';
import {ElButton, ElMessage, ElMessageBox, ElTag} from 'element-plus';
import SaveOrUpdateUser from '/@/views/system/user/EditUser.vue';
import {useUserApi} from '/@/api/useSystemApi/user';
import {useRolesApi} from "/@/api/useSystemApi/roles";

// 定义接口来定义对象的类型
interface TableDataRow {
  id: number;
  username: string;
  email: string;
  roles: string;
  status: boolean;
  nickname: string;
  user_type: number;
  created_by: number;
  updated_by: number;
  creation_date: string;
  updation_date: string;
}

interface listQueryRow {
  page: number;
  pageSize: number;
  username: string;

}

interface StateRow {
  columns: Array<any>;
  fieldData: Array<any>;
  listData: Array<TableDataRow>;
  total: number;
  listQuery: listQueryRow;
  roleList: Array<any>;
  roleQuery: listQueryRow;
}


const SaveOrUpdateUserRef = ref()
const tableRef = ref()

const state = reactive<StateRow>({
  columns: [
    {
      key: 'username', label: '账户名称', width: '', align: 'center', show: true,
      render: (row: any) => h(ElButton, {
        link: true,
        type: "primary",
        onClick: () => {
          onOpenSaveOrUpdate("update", row)
        }
      }, () => row.username)
    },
    {key: 'nickname', label: '用户昵称', width: '', align: 'center', show: true},
    {
      key: 'roles', label: '关联角色', width: '', align: 'center', show: true,
      render: (row: any) => handleRoles(row.roles)
    },
    {key: 'email', label: '邮箱', width: '', align: 'center', show: true},
    {
      key: 'status', label: '用户状态', width: '', align: 'center', show: true,
      render: (row: any) => h(ElTag, {
        type: row.status ? "success" : "info",
      }, () => row.status ? "启用" : "禁用",)
    },
    {key: 'remarks', label: '备注', width: '', align: 'center', show: true},
    {key: 'creation_date', label: '创建时间', width: '150', align: 'center', show: true},
    {
      label: '操作', 
      columnType: 'string', 
      fixed: 'right', 
      align: 'center', 
      width: '280',
      render: (row: any) => h("div", null, [
        h(ElButton, {
          type: "primary",
          size: "small",
          onClick: () => {
            onOpenSaveOrUpdate('update', row)
          }
        }, () => '编辑'),
        h(ElButton, {
          type: row.status ? "warning" : "success",
          size: "small",
          onClick: () => {
            toggleStatus(row)
          }
        }, () => row.status ? '禁用' : '启用'),
        h(ElButton, {
          type: "info",
          size: "small",
          onClick: () => {
            resetPassword(row)
          }
        }, () => '重置密码'),
        h(ElButton, {
          type: "danger",
          size: "small",
          onClick: () => {
            deleted(row)
          }
        }, () => '删除')
      ])
    },
  ],
  // list
  listData: [],
  total: 0,
  listQuery: {
    page: 1,
    pageSize: 20,
    username: '',
  },
  //rule
  roleList: [],
  roleQuery: {
    page: 1,
    pageSize: 100,
  }
});
// 获取用户数据
const getList = () => {
  tableRef.value.openLoading()
  useUserApi().getList(state.listQuery)
    .then(res => {
      state.listData = res.data.rows
      state.total = res.data.rowTotal
    })
    .finally(() => {
      tableRef.value.closeLoading()
    })
};

const getRolesList = () => {
  useRolesApi().getList(state.roleQuery)
    .then((res: any) => {
      state.roleList = res.data.rows
    })
};

// 查询
const search = () => {
  state.listQuery.page = 1
  getList()
}

// 新增或修改用户
const onOpenSaveOrUpdate = (editType: string, row?: TableDataRow) => {
  SaveOrUpdateUserRef.value.openDialog(editType, row);
};

// 删除用户
const deleted = (row: TableDataRow) => {
  ElMessageBox.confirm('是否删除该条数据, 是否继续?', '提示', {
    confirmButtonText: '确认',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(() => {
      useUserApi().deleted({id: row.id})
        .then(() => {
          ElMessage.success('删除成功');
          getList()
        })
    })
    .catch(() => {
    });
};

// 启用/禁用用户
const toggleStatus = (row: TableDataRow) => {
  const action = row.status ? '禁用' : '启用';
  ElMessageBox.confirm(`确定要${action}该用户吗？`, '提示', {
    confirmButtonText: '确认',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(() => {
      const updatedRow = {
        ...row,
        status: row.status ? 0 : 1
      };
      useUserApi().saveOrUpdate(updatedRow)
        .then(() => {
          ElMessage.success(`${action}成功`);
          getList()
        })
    })
    .catch(() => {
    });
};

// 重置密码
const resetPassword = (row: TableDataRow) => {
  ElMessageBox.confirm(`确定要重置用户"${row.nickname}"的密码吗？密码将重置为：123456`, '提示', {
    confirmButtonText: '确认',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(() => {
      useUserApi().adminResetPassword({id: row.id})
        .then(() => {
          ElMessage.success('密码已重置为：123456');
        })
    })
    .catch(() => {
    });
};

// 处理角色名称
const handleRoles = (roles: any) => {
  let roleTagList: any[] = []
  roles = roles ? roles : []
  roles.forEach((role: any) => {
    let roleName = state.roleList.find(e => e.id == role)?.name
    roleTagList.push(h(ElTag, null, () => roleName))
  })
  return h('div', null, roleTagList)
}
// 页面加载时
onMounted(() => {
  getList();
  getRolesList()
});

</script>
