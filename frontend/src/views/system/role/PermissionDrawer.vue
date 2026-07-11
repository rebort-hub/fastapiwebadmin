<template>
  <el-drawer
    v-model="visible"
    :title="`【${roleName}】权限分配`"
    size="780px"
    destroy-on-close
    class="role-permission-drawer"
    @close="handleClose"
  >
    <div class="drawer-body">
      <el-tabs v-model="activeTab" class="permission-tabs">
        <el-tab-pane label="数据权限" name="data">
          <div class="section-title">数据授权</div>
          <el-form label-width="0">
            <el-form-item>
              <el-select v-model="permissionState.data_scope" class="w100">
                <el-option :value="1" label="仅本人数据权限" />
                <el-option :value="2" label="本部门数据权限" />
                <el-option :value="3" label="本部门及以下数据权限" />
                <el-option :value="4" label="全部数据权限" />
                <el-option :value="5" label="自定义数据权限" />
              </el-select>
            </el-form-item>
          </el-form>
          <div v-if="permissionState.data_scope === 5" class="dept-tree-wrap">
            <el-input v-model="deptFilterText" placeholder="搜索部门" clearable class="mb10" />
            <el-tree
              ref="deptTreeRef"
              :data="deptTreeData"
              node-key="id"
              show-checkbox
              check-strictly
              default-expand-all
              :props="{ label: 'name', children: 'children' }"
              :filter-node-method="filterDeptNode"
              class="dept-tree"
            />
          </div>
        </el-tab-pane>

        <el-tab-pane label="菜单权限" name="menu">
          <div class="section-title">菜单授权</div>
          <el-tree
            ref="menuTreeRef"
            :data="menuTreeData"
            :props="menuProps"
            node-key="id"
            show-checkbox
            default-expand-all
            class="menu-tree"
          />
        </el-tab-pane>

        <el-tab-pane label="分配用户" name="users">
          <div class="section-title">关联用户</div>
          <el-transfer
            v-model="selectedUserIds"
            :data="allUsers"
            :titles="['可选用户', '已关联用户']"
            :props="{ key: 'id', label: 'label' }"
            filterable
            filter-placeholder="搜索用户"
            class="user-transfer"
          />
        </el-tab-pane>
      </el-tabs>
    </div>

    <template #footer>
      <div class="drawer-footer">
        <el-button @click="handleClose">取 消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">确 定</el-button>
      </div>
    </template>
  </el-drawer>
</template>

<script lang="ts" setup>
defineOptions({ name: 'RolePermissionDrawer' })
import { computed, nextTick, reactive, ref, watch } from 'vue';
import { ElMessage } from 'element-plus';
import { useRolesApi } from '/@/api/useSystemApi/roles';
import { useMenuApi } from '/@/api/useSystemApi/menu';
import { useDepartmentApi } from '/@/api/useSystemApi/department';

const props = defineProps<{
  modelValue: boolean;
  roleId: number;
  roleName: string;
}>();

const emit = defineEmits<{
  'update:modelValue': [value: boolean];
  saved: [];
}>();

const visible = computed({
  get: () => props.modelValue,
  set: (value: boolean) => emit('update:modelValue', value),
});

const activeTab = ref('data');
const saving = ref(false);
const deptFilterText = ref('');
const deptTreeRef = ref();
const menuTreeRef = ref();
const deptTreeData = ref<any[]>([]);
const menuTreeData = ref<any[]>([]);
const allUsers = ref<{ id: number; label: string }[]>([]);
const selectedUserIds = ref<number[]>([]);

const permissionState = reactive({
  data_scope: 4,
  dept_ids: [] as number[],
  menu_ids: [] as number[],
});

const menuProps = {
  children: 'children',
  label: 'title',
};

const filterDeptNode = (value: string, data: any) => {
  if (!value) return true;
  return data.name?.includes(value);
};

watch(deptFilterText, (val) => {
  deptTreeRef.value?.filter(val);
});

const expandMenuIdsWithAncestors = (checkedIds: number[], roots: any[]): number[] => {
  const parentById = new Map<number, number | undefined>();
  const walk = (nodes: any[], parent?: number) => {
    nodes.forEach((node) => {
      parentById.set(node.id, parent);
      if (node.children?.length) walk(node.children, node.id);
    });
  };
  walk(roots);
  const result = new Set<number>();
  checkedIds.forEach((id) => {
    let current: number | undefined = id;
    while (current !== undefined) {
      result.add(current);
      current = parentById.get(current);
    }
  });
  return [...result];
};

const loadData = async () => {
  if (!props.roleId) return;
  const [deptRes, menuRes, roleRes, userRes] = await Promise.all([
    useDepartmentApi().getList(),
    useMenuApi().getAllMenus(),
    useRolesApi().detail({ id: props.roleId }),
    useRolesApi().getCandidateUsers(),
  ]);

  deptTreeData.value = deptRes.data || [];
  menuTreeData.value = menuRes.data || [];
  const roleData = roleRes.data || {};
  permissionState.data_scope = roleData.data_scope || 4;
  permissionState.dept_ids = roleData.dept_ids || [];
  permissionState.menu_ids = roleData.menus || [];
  selectedUserIds.value = roleData.user_ids || [];

  const rows = userRes.data || [];
  allUsers.value = rows.map((user: any) => ({
    id: user.id,
    label: `${user.nickname || user.username} (${user.username})`,
  }));

  await nextTick();
  menuTreeRef.value?.setCheckedKeys(permissionState.menu_ids, false);
  if (permissionState.data_scope === 5) {
    deptTreeRef.value?.setCheckedKeys(permissionState.dept_ids, false);
  }
};

watch(
  () => props.modelValue,
  (open) => {
    if (open) {
      activeTab.value = 'data';
      loadData().catch((error) => {
        ElMessage.error(`加载权限数据失败: ${error?.message || error}`);
      });
    }
  }
);

const handleClose = () => {
  visible.value = false;
};

const handleSave = async () => {
  if (props.roleId === 1) {
    ElMessage.warning('系统默认角色，不可操作');
    return;
  }
  saving.value = true;
  try {
    const checkedMenuIds = menuTreeRef.value?.getCheckedKeys(false) || [];
    const halfCheckedMenuIds = menuTreeRef.value?.getHalfCheckedKeys() || [];
    const menuIds = expandMenuIdsWithAncestors(
      [...new Set([...checkedMenuIds, ...halfCheckedMenuIds])],
      menuTreeData.value
    );
    const deptIds =
      permissionState.data_scope === 5
        ? (deptTreeRef.value?.getCheckedKeys(false) || []).map((id: number) => Number(id))
        : [];

    await useRolesApi().setPermission({
      role_id: props.roleId,
      menu_ids: menuIds,
      data_scope: permissionState.data_scope,
      dept_ids: deptIds,
    });
    await useRolesApi().setRoleUsers({
      role_id: props.roleId,
      user_ids: selectedUserIds.value,
    });
    ElMessage.success('权限分配成功');
    emit('saved');
    handleClose();
  } finally {
    saving.value = false;
  }
};
</script>

<style scoped lang="scss">
.role-permission-drawer {
  :deep(.el-drawer__header) {
    margin-bottom: 0;
    padding: 16px 20px 12px;
    border-bottom: 1px solid var(--el-border-color-lighter);
  }

  :deep(.el-drawer__body) {
    padding: 0;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }

  :deep(.el-drawer__footer) {
    padding: 0;
    border-top: 1px solid var(--el-border-color-lighter);
  }
}

.drawer-body {
  flex: 1;
  min-height: 0;
  padding: 16px 20px;
  overflow-y: auto;
}

.drawer-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 14px 20px 18px;
}

.permission-tabs {
  :deep(.el-tabs__header) {
    margin-bottom: 12px;
  }

  :deep(.el-tabs__content) {
    padding: 0;
  }
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 12px;
}

.dept-tree-wrap {
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 4px;
  padding: 12px;
  margin-top: 4px;
}

.dept-tree,
.menu-tree {
  max-height: calc(100vh - 320px);
  overflow: auto;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 4px;
  padding: 10px;
}

.user-transfer {
  display: flex;
  justify-content: center;
  padding: 8px 0 4px;

  :deep(.el-transfer-panel) {
    width: 280px;
  }
}

.w100 {
  width: 100%;
}

.mb10 {
  margin-bottom: 10px;
}
</style>
