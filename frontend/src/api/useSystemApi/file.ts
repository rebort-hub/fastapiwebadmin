import request from '/@/utils/request';

export function useFileApi() {
  return {
    upload: (data: object) => {
      return request({
        url: '/file/upload',
        method: 'POST',
        headers: { 'Content-Type': 'multipart/form-data' },
        data,
      });
    },
    getList: (data: object) => {
      return request({ url: '/file/list', method: 'POST', data });
    },
    getStatistics: () => request({ url: '/file/statistics', method: 'GET' }),
    getStorageConfig: () => request({ url: '/file/storage-config', method: 'GET' }),
    deleted: (data: object) => request({ url: '/file/deleted', method: 'POST', data }),
    deleteList: (data: object) => request({ url: '/file/deleteList', method: 'POST', data }),
    download: (path: string) => request({ url: '/file/download/' + path, method: 'GET' }),
  };
}

export const STORAGE_TYPE_LABELS: Record<string, string> = {
  local: '本地存储',
  aliyun_oss: '阿里云 OSS',
  tencent_cos: '腾讯云 COS',
  qiniu: '七牛云',
  minio: 'MinIO',
};
