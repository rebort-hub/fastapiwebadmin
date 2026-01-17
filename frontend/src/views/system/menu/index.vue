<template>
  <div class="system-menu-container app-container">
    <el-card>
      <div class="system-menu-search mb15">
        <el-input v-model="state.listQuery.name" placeholder="请输入菜单名称" style="max-width: 180px"></el-input>
        <el-button type="primary" class="ml10" @click="getList">查询
        </el-button>
        <el-button type="success" class="ml10" @click="onOpenSaveOrUpdate('save', null)">新增
        </el-button>
      </div>

      <z-table
          :columns="state.columns"
          :data="state.menuList"
          ref="tableRef"
          :row-key="'id'"
          :showPage="false"
          v-model:page-size="state.listQuery.pageSize"
          v-model:page="state.listQuery.page"
          :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
          @pagination-change="getList"
      />

    </el-card>
    <EditMenu :menuList="state.menuList"
              :allMenuList="state.allMenuList"
              @getList="getList"
              ref="EditRef"/>
  </div>
</template>

<script lang="ts" setup name="SystemMenu">
import {h, onMounted, reactive, ref} from 'vue';
import {useMenuApi} from '/@/api/useSystemApi/menu';
import {RouteRecordRaw} from 'vue-router';
import {ElButton, ElMessage, ElMessageBox} from 'element-plus';
import EditMenu from '/@/views/system/menu/EditMenu.vue';


const EditRef = ref();
const tableRef = ref();
const state = reactive({
  columns: [
    {
      key: 'title', label: '菜单名称', width: '', align: 'left', show: true, render: (row: any) =>
          h(ElButton, {
            link: true,
            type: "primary",
            onClick: () => {
              onOpenSaveOrUpdate('update', row)
            }
          }, () => row.title),
    },
    {key: 'path', label: '路由路径', width: '', align: 'left', show: true},
    {key: 'component', label: '组件路径', width: '', align: 'left', show: true},
    {
      key: 'roles', 
      label: '权限标识', 
      width: '', 
      align: 'left', 
      show: true,
      render: (row: any) => {
        // 处理 roles 为 0、false、null 或空字符串的情况
        const roles = row.roles;
        if (!roles || roles === '0' || roles === 0 || roles === 'False') {
          return '-';
        }
        return roles;
      }
    },
    {key: 'name', label: '路由名称', width: '', align: 'left', show: true},
    {key: 'sort', label: '排序', width: '', align: 'left', show: true},
    {key: 'menu_type', label: '类型', width: '', align: 'left', show: true}, {
      label: '操作', columnType: 'string', fixed: 'right', align: 'center', width: '140',
      render: (row: any) => h("div", null, [
        h(ElButton, {
          type: "primary",
          onClick: () => {
            onOpenSaveOrUpdate('update', row)
          }
        }, () => '编辑'),
        h(ElButton, {
          type: "danger",
          onClick: () => {
            deleted(row)
          }
        }, () => '删除')
      ])
    },
  ],
  // list
  menuList: [],
  allMenuList: null,
  listQuery: {
    page: 1,
    pageSize: 200,
    name: '',
  },
});

// 递归组装菜单
const menuAssembly = (parent_menu: Array<object>, all_menu: Array<object>) => {
  parent_menu.forEach((parent: any) => {
    all_menu.forEach((menu: any) => {
      if (menu.parent_id == parent.id) {
        parent.children = parent.children ? parent.children : [];
        parent.children.push(menu);
      }
    })
    if (parent.children) menuAssembly(parent.children, all_menu);
  })
  state.menuList = parent_menu
};

// 获取菜单列表
const getList = async () => {
  tableRef.value.openLoading()
  let res = await useMenuApi().allMenu({})
  console.log('原始菜单数据:', res.data)
  state.allMenuList = res.data
  
  // 深拷贝数据，避免引用问题
  const allMenuData = JSON.parse(JSON.stringify(res.data))
  
  let parent_menu: any = []
  allMenuData.forEach((menu: any) => {
    console.log(`菜单 ${menu.title} 的 roles:`, menu.roles, typeof menu.roles)
    if (!menu.parent_id) {
      parent_menu.push(menu)
    }
  })
  
  menuAssembly(parent_menu, allMenuData)
  
  // 强制更新 menuList，触发响应式
  state.menuList = []
  setTimeout(() => {
    state.menuList = parent_menu
    console.log('最终菜单列表:', state.menuList)
  }, 0)
  
  tableRef.value.closeLoading()
};
// 打开新增菜单弹窗
// const onOpenAddMenu = () => {
//   addMenuRef.value.openDialog();
// };
// 打开编辑菜单弹窗
const onOpenSaveOrUpdate = (editType: string, row: RouteRecordRaw) => {
  EditRef.value.openDialog(editType, row);
};
// 删除当前行
const deleted = (row: RouteRecordRaw) => {
  ElMessageBox.confirm('是否删除该条数据, 是否继续?', '提示', {
    confirmButtonText: '删除',
    cancelButtonText: '取消',
    type: 'warning',
  })
      .then(() => {
        useMenuApi().deleted({id: row.id})
          .then(() => {
            ElMessage.success('删除成功');
            getList(); // 刷新列表
          })
      })
      .catch(() => {
      });
};
onMounted(() => {
  getList()
})

</script>

