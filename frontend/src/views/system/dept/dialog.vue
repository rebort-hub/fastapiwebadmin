<template>
  <div class="system-dept-dialog-container">
    <el-dialog :title="state.dialog.title" v-model="state.dialog.isShowDialog" width="600px">
      <el-form ref="deptDialogFormRef" :model="state.ruleForm" :rules="rules" size="default" label-width="90px">
        <el-row :gutter="35">
          <el-col :xs="24" :sm="24" :md="24" :lg="24" :xl="24" class="mb20">
            <el-form-item label="上级部门">
              <el-tree-select
                v-model="state.ruleForm.parent_id"
                :data="state.deptTreeData"
                :props="{ label: 'name', value: 'id' }"
                placeholder="请选择上级部门"
                clearable
                check-strictly
                :render-after-expand="false"
                class="w100"
              />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="24" :md="24" :lg="24" :xl="24" class="mb20">
            <el-form-item label="部门名称" prop="name">
              <el-input v-model="state.ruleForm.name" placeholder="请输入部门名称" clearable></el-input>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="12" :lg="12" :xl="12" class="mb20">
            <el-form-item label="排序">
              <el-input-number v-model="state.ruleForm.sort" :min="0" :max="999" controls-position="right" placeholder="请输入排序" class="w100" />
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="12" :md="12" :lg="12" :xl="12" class="mb20">
            <el-form-item label="部门状态">
              <el-switch v-model="state.ruleForm.status" :active-value="1" :inactive-value="0" inline-prompt active-text="启" inactive-text="禁"></el-switch>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="24" :md="24" :lg="24" :xl="24" class="mb20">
            <el-form-item label="部门描述">
              <el-input v-model="state.ruleForm.description" type="textarea" placeholder="请输入部门描述" maxlength="500" :rows="4"></el-input>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="onCancel" size="default">取 消</el-button>
          <el-button type="primary" @click="onSubmit" size="default">确 定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts" name="systemDeptDialog">
import { reactive, ref } from 'vue';
import { ElMessage } from 'element-plus';
import { useDepartmentApi } from '/@/api/useSystemApi/department';

// 定义子组件向父组件传值/事件
const emit = defineEmits(['refresh']);

// 定义变量内容
const deptDialogFormRef = ref();
const state = reactive({
  ruleForm: {
    id: null,
    parent_id: 0,
    name: '',
    sort: 0,
    status: 1,
    description: '',
  },
  deptTreeData: [] as any[],
  allDeptData: [] as any[],
  dialog: {
    isShowDialog: false,
    type: '',
    title: '',
  },
});

const rules = reactive({
  name: [{ required: true, message: '请输入部门名称', trigger: 'blur' }],
});

// 打开弹窗
const openDialog = (type: string, row: any) => {
  state.dialog.type = type;
  
  if (type === 'edit') {
    state.ruleForm = {
      id: row.id,
      parent_id: row.parent_id || 0,
      name: row.name,
      sort: row.sort || 0,
      status: row.status,
      description: row.description || '',
    };
    state.dialog.title = '修改部门';
  } else {
    // 新增子部门
    if (row && row.id) {
      state.ruleForm = {
        id: null,
        parent_id: row.id,
        name: '',
        sort: 0,
        status: 1,
        description: '',
      };
    } else {
      // 新增顶级部门
      state.ruleForm = {
        id: null,
        parent_id: 0,
        name: '',
        sort: 0,
        status: 1,
        description: '',
      };
    }
    state.dialog.title = '新增部门';
  }
  
  state.dialog.isShowDialog = true;
  getDeptData();
};

// 关闭弹窗
const closeDialog = () => {
  state.dialog.isShowDialog = false;
};

// 取消
const onCancel = () => {
  closeDialog();
};

// 提交
const onSubmit = () => {
  deptDialogFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return;
    
    try {
      await useDepartmentApi().saveOrUpdate(state.ruleForm);
      ElMessage.success('操作成功');
      closeDialog();
      emit('refresh');
    } catch (error: any) {
      ElMessage.error(error.response?.data?.msg || '操作失败');
    }
  });
};

// 获取部门数据
const getDeptData = () => {
  useDepartmentApi().getList()
    .then(res => {
      state.allDeptData = res.data || [];
      // 添加顶级选项
      state.deptTreeData = [
        {
          id: 0,
          name: '顶级部门',
          children: res.data || []
        }
      ];
    });
};

// 暴露变量
defineExpose({
  openDialog,
});
</script>
