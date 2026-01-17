import request from '/@/utils/request';

/**
 * 部门管理接口
 */
export function useDepartmentApi() {
  return {
    getList: (data?: object) => {
      return request({
        url: '/department/list',
        method: 'POST',
        data,
      });
    },
    saveOrUpdate(data?: object) {
      return request({
        url: '/department/saveOrUpdate',
        method: 'POST',
        data
      })
    },
    deleted(data?: object) {
      return request({
        url: '/department/deleted',
        method: 'POST',
        data
      })
    }
  };
}
