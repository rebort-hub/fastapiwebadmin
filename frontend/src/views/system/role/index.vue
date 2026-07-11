<template>
  <div class="system-role-container app-container">
    <el-card>
      <div class="system-user-search mb15">
        <el-input v-model="state.listQuery.name" placeholder="请输入角色名称" style="max-width: 180px"></el-input>
        <el-button v-auth="'role:query'" type="primary" class="ml10" @click="search">查询
        </el-button>
        <el-button v-auth="'role:add'" type="success" class="ml10" @click="onOpenSaveOrUpdate('save', null)">新增
        </el-button>
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
    <SaveOrUpdateRole ref="SaveOrUpdateRoleRef" @getList="getList"/>
    <PermissionDrawer
      v-model="state.permissionDrawer.visible"
      :role-id="state.permissionDrawer.roleId"
      :role-name="state.permissionDrawer.roleName"
      @saved="getList"
    />
  </div>
</template>

<script lang="ts" setup>
defineOptions({ name: 'SystemRole' })
import {h, onMounted, reactive, ref} from 'vue';
import {ElButton, ElMessage, ElMessageBox, ElTag} from 'element-plus';
import SaveOrUpdateRole from '/@/views/system/role/EditRole.vue';
import PermissionDrawer from '/@/views/system/role/PermissionDrawer.vue';
import {useRolesApi} from "/@/api/useSystemApi/roles";
import {auth as authFunction} from '/@/utils/authFunction';

const DATA_SCOPE_MAP: Record<number, { type: string; label: string }> = {
  1: { type: 'primary', label: '仅本人数据权限' },
  2: { type: 'info', label: '本部门数据权限' },
  3: { type: 'warning', label: '本部门及以下数据权限' },
  4: { type: 'success', label: '全部数据权限' },
  5: { type: 'danger', label: '自定义数据权限' },
};

const SaveOrUpdateRoleRef = ref();
const tableRef = ref();
const state = reactive({
  permissionDrawer: {
    visible: false,
    roleId: 0,
    roleName: '',
  },
  columns: [
    {
      key: 'name', label: '角色名称', width: '', align: 'center', show: true,
      render: (row: any) => h(ElButton, {
        link: true,
        type: "primary",
        onClick: () => {
          onOpenSaveOrUpdate("update", row)
        }
      }, () => row.name)
    },
    {
      key: 'data_scope', label: '数据权限', width: '180', align: 'center', show: true,
      render: (row: any) => {
        const item = DATA_SCOPE_MAP[row.data_scope] || DATA_SCOPE_MAP[4];
        return h(ElTag, { type: item.type }, () => item.label);
      },
    },
    {key: 'role_type', label: '权限类型', width: '', align: 'center', show: true},
    {key: 'dept_name', label: '所属部门', width: '150', align: 'center', show: true},
    {
      key: 'status', label: '角色状态', width: '', align: 'center', show: true,
      render: (row: any) => h(ElTag, {
        type: row.status == 10 ? "success" : "info",
      }, () => row.status == 10 ? "启用" : "禁用",)
    },
    {key: 'description', label: '角色描述', width: '', align: 'center', show: true},
    {key: 'updation_date', label: '更新时间', width: '150', align: 'center', show: true},
    {key: 'updated_by_name', label: '更新人', width: '100', align: 'center', show: true},
    {
      label: '操作', fixed: 'right', width: '220', align: 'center',
      render: (row: any) => h("div", null, [
        h(ElButton, {
          type: "warning",
          onClick: () => openPermissionDrawer(row),
          style: authFunction('role:permission') ? '' : 'display:none'
        }, () => '分配权限'),
        h(ElButton, {
          type: "primary",
          onClick: () => {
            onOpenSaveOrUpdate("update", row)
          },
          style: authFunction('role:edit') ? '' : 'display:none'
        }, () => '编辑'),
        h(ElButton, {
          type: "danger",
          onClick: () => {
            deleted(row)
          },
          style: authFunction('role:delete') ? '' : 'display:none'
        }, () => '删除')
      ])
    },
  ],
  listData: [],
  tableLoading: false,
  total: 0,
  listQuery: {
    page: 1,
    pageSize: 20,
    name: '',
  },
});

const getList = () => {
  tableRef.value.openLoading()
  useRolesApi().getList(state.listQuery)
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

const onOpenSaveOrUpdate = (editType: string, row: any) => {
  SaveOrUpdateRoleRef.value.openDialog(editType, row);
};

const openPermissionDrawer = (row: any) => {
  if (row.id === 1) {
    ElMessage.warning('系统默认角色，不可操作');
    return;
  }
  state.permissionDrawer.roleId = row.id;
  state.permissionDrawer.roleName = row.name;
  state.permissionDrawer.visible = true;
};

const deleted = (row: any) => {
  ElMessageBox.confirm('是否删除该条数据, 是否继续?', '提示', {
    confirmButtonText: '确认',
    cancelButtonText: '取消',
    type: 'warning',
  })
      .then(() => {
        useRolesApi().deleted({id: row.id})
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
