export function getEnv() {
	return import.meta.env.ENV;
}

/** axios baseURL = 后端地址 + API 前缀 */
export function getApiBaseUrl() {
	const base = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');
	const prefix = import.meta.env.VITE_API_PREFIX || '/api';
	return `${base}${prefix}`;
}

export function getWebSocketUrl() {
	const host = import.meta.env.VITE_WBE_SOCKET_URL || window.location.host;
	return `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${host}`;
}

/** 文件上传等需要完整后端根地址时使用 */
export function getBaseApiUrl() {
	const base = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');
	if (base) {
		return base;
	}
	// 开发代理模式下，上传走当前站点 + /api
	return window.location.origin;
}
