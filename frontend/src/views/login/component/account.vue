<template>
  <el-form ref="loginFormRef" :model="state.ruleForm" :rules="state.rules" size="large" class="login-content-form">
    <el-form-item class="login-animation1" prop="userName">
      <el-input text placeholder="请输入用户名" v-model="state.ruleForm.userName" clearable
                autocomplete="off" @keyup.enter="onSignIn">
        <template #prefix>
          <el-icon class="el-input__icon">
            <ele-User/>
          </el-icon>
        </template>
      </el-input>
    </el-form-item>
    <el-form-item class="login-animation2" prop="password">
      <el-input :type="state.isShowPassword ? 'text' : 'password'" placeholder="请输入登录密码"
                v-model="state.ruleForm.password" autocomplete="off" @keyup.enter="onSignIn">
        <template #prefix>
          <el-icon class="el-input__icon">
            <ele-Unlock/>
          </el-icon>
        </template>
        <template #suffix>
          <i
              class="iconfont el-input__icon login-content-password"
              :class="state.isShowPassword ? 'icon-yincangmima' : 'icon-xianshimima'"
              @click="state.isShowPassword = !state.isShowPassword"
          >
          </i>
        </template>
      </el-input>
    </el-form-item>
    <el-form-item class="login-animation3">
      <el-button type="primary" class="login-content-submit" round v-waves @click="onSignIn"
                 :loading="state.loading.signIn">
        <span>登 录</span>
      </el-button>
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts" name="loginAccount">
import {computed, reactive, ref} from 'vue';
import {useRoute, useRouter} from 'vue-router';
import {ElMessage} from 'element-plus';
import {initBackEndControlRoutes} from '/@/router/backEnd';
import {Session} from '/@/utils/storage';
import {formatAxis} from '/@/utils/formatTime';
import {NextLoading} from '/@/utils/loading';
import {useUserApi} from "/@/api/useSystemApi/user";
import {useUserStore} from "/@/stores/user";

const loginFormRef = ref();
const route = useRoute();
const router = useRouter();

const state = reactive({
  isShowPassword: false,
  ruleForm: {
    userName: '',
    password: '',
  },
  rules: {
    userName: [
      { required: true, message: '请输入用户名', trigger: 'blur' },
      { min: 2, max: 20, message: '用户名长度在 2 到 20 个字符', trigger: 'blur' }
    ],
    password: [
      { required: true, message: '请输入密码', trigger: 'blur' },
      { min: 6, max: 20, message: '密码长度在 6 到 20 个字符', trigger: 'blur' }
    ],
  },
  loading: {
    signIn: false,
  },
});

const currentTime = computed(() => {
  return formatAxis(new Date());
});

const onSignIn = async () => {
  if (!loginFormRef.value) return;

  try {
    await loginFormRef.value.validate();
  } catch {
    ElMessage.error('请检查输入信息');
    return;
  }

  state.loading.signIn = true;
  try {
    const res = await useUserApi().signIn({
      username: state.ruleForm.userName,
      password: state.ruleForm.password,
    });
    Session.set('token', res.data.token);
    await useUserStore().setUserInfos();
    await initBackEndControlRoutes();
    signInSuccess(false);
  } catch (e) {
    console.error('登录失败：', e);
    state.loading.signIn = false;
  }
};

const signInSuccess = (isNoPower: boolean) => {
  if (isNoPower) {
    ElMessage.warning('抱歉，您没有登录权限');
    Session.clear();
  } else {
    const currentTimeInfo = currentTime.value;
    const params = route.query!.params || {}
    if (route.query?.redirect) {
      router.push({
        path: route.query?.redirect as string,
        query: Object.keys(params).length > 0 ? JSON.parse(params as string) : '',
      });
    } else {
      router.push('/home');
    }
    ElMessage.success(`${currentTimeInfo}，欢迎回来！`);
    NextLoading.start();
  }
  state.loading.signIn = false;
};
</script>

<style scoped lang="scss">
.login-content-form {
  margin-top: 20px;

  :deep(.el-input__wrapper) {
    border-radius: 10px;
  }

  .login-content-submit {
    border-radius: 25px;
  }

  @for $i from 1 through 3 {
    .login-animation#{$i} {
      opacity: 0;
      animation-name: error-num;
      animation-duration: 0.5s;
      animation-fill-mode: forwards;
      animation-delay: calc($i/10) + s;
    }
  }

  .login-content-password {
    display: inline-block;
    width: 20px;
    cursor: pointer;

    &:hover {
      color: #909399;
    }
  }

  .login-content-submit {
    width: 100%;
    letter-spacing: 2px;
    font-weight: 300;
    margin-top: 15px;
  }
}
</style>
