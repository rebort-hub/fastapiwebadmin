import request from '/@/utils/request';

export interface RolePermissionData {
  role_id: number;
  menu_ids: number[];
  data_scope: number;
  dept_ids: number[];
}

export function useRolesApi() {
  return {
    getList: (data?: object) => {
      return request({
        url: '/roles/list',
        method: 'POST',
        data,
      });
    },
    detail(data: { id: number }) {
      return request({
        url: '/roles/detail',
        method: 'POST',
        data,
      });
    },
    saveOrUpdate(data?: object) {
      return request({
        url: '/roles/saveOrUpdate',
        method: 'POST',
        data,
      });
    },
    setPermission(data: RolePermissionData) {
      return request({
        url: '/roles/permission/setting',
        method: 'POST',
        data,
      });
    },
    getRoleUsers(data: { role_id: number }) {
      return request({
        url: '/roles/users',
        method: 'POST',
        data,
      });
    },
    getCandidateUsers() {
      return request({
        url: '/roles/candidateUsers',
        method: 'POST',
        data: {},
      });
    },
    setRoleUsers(data: { role_id: number; user_ids: number[] }) {
      return request({
        url: '/roles/setUsers',
        method: 'POST',
        data,
      });
    },
    deleted(data?: object) {
      return request({
        url: '/roles/deleted',
        method: 'POST',
        data,
      });
    },
  };
}
