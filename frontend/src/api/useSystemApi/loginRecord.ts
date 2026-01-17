import request from '/@/utils/request';

/**
 * 登录记录接口
 */
export function useLoginRecordApi() {
  return {
    getList: (data?: object) => {
      return request({
        url: '/loginRecord/list',
        method: 'POST',
        data,
      });
    }
  };
}
