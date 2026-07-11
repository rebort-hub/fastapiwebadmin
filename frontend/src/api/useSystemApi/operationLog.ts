import request from '/@/utils/request';

export function useOperationLogApi() {
  return {
    getList: (data: object) => {
      return request({
        url: '/operationLog/list',
        method: 'POST',
        data,
      });
    },
  };
}
