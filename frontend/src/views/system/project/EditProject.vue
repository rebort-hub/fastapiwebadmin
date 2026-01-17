<template>
  <div class="system-project-dialog-container">
    <el-dialog :title="state.dialog.title" v-model="state.dialog.isShowDialog" width="700px">
      <el-form ref="projectFormRef" :model="state.ruleForm" :rules="rules" label-width="90px">
        <el-row :gutter="35">
          <el-col :xs="24" :sm="24" :md="24" :lg="24" :xl="24" class="mb20">
            <el-form-item label="项目名称" prop="name">
              <el-input v-model="state.ruleForm.name" placeholder="请输入项目名称" clearable></el-input>
            </el-form-item>
          </el-col>
          <el-col :xs="24" :sm="24" :md="24" :lg="24" :xl="24" class="mb20">
            <el-form-item label="项目描述" prop="description">
              <el-input
                  v-model="state.ruleForm.description"
                  type="textarea"
                  placeholder="请输入项目描述"
                  :rows="4"
                  clearable
              ></el-input>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
				<span class="dialog-footer">
					<el-button @click="onCancel">取 消</el-button>
					<el-button type="primary" @click="onSubmit">确 定</el-button>
				</span>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup name="EditProject">
import {reactive, ref} from 'vue';
import {ElMessage} from 'element-plus';
import {useProjectApi} from '/@/api/useSystemApi/project';

const projectFormRef = ref();
const emit = defineEmits(['getList']);

const state = reactive({
  ruleForm: {
    id: null,
    name: '',
    description: '',
  },
  dialog: {
    isShowDialog: false,
    type: '',
    title: '',
  },
});

const rules = reactive({
  name: [{required: true, message: '请输入项目名称', trigger: 'blur'}],
});

const openDialog = (type: string, row?: any) => {
  state.dialog.type = type;
  if (type === 'save') {
    state.dialog.title = '新增项目';
    state.ruleForm = {
      id: null,
      name: '',
      description: '',
    };
  } else {
    state.dialog.title = '编辑项目';
    state.ruleForm = {
      id: row.id,
      name: row.name,
      description: row.description,
    };
  }
  state.dialog.isShowDialog = true;
};

const onCancel = () => {
  state.dialog.isShowDialog = false;
};

const onSubmit = () => {
  projectFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return;
    
    try {
      await useProjectApi().saveOrUpdate(state.ruleForm);
      ElMessage.success('操作成功');
      state.dialog.isShowDialog = false;
      emit('getList');
    } catch (error) {
      console.error(error);
    }
  });
};

defineExpose({
  openDialog,
});
</script>
