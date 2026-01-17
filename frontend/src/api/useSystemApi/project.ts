import request from '/@/utils/request';

/**
 * 项目管理接口
 */
export function useProjectApi() {
  return {
    getList: (data?: object) => {
      return request({
        url: '/project/list',
        method: 'POST',
        data,
      });
    },
    saveOrUpdate(data?: object) {
      return request({
        url: '/project/saveOrUpdate',
        method: 'POST',
        data
      })
    },
    deleted(data?: object) {
      return request({
        url: '/project/deleted',
        method: 'POST',
        data
      })
    }
  };
}
