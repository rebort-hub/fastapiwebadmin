export type OAuthProvider = 'wechat' | 'qq' | 'github' | 'gitee';

import { getApiBaseUrl } from '/@/utils/config';

function getLoginRedirectUri() {
	const base = import.meta.env.VITE_PUBLIC_PATH || '/';
	const normalizedBase = base.endsWith('/') ? base.slice(0, -1) : base;
	return `${window.location.origin}${normalizedBase}/login`;
}

/** 跳转至后端 OAuth 入口 */
export function startOAuthLogin(provider: OAuthProvider) {
	const apiBase = getApiBaseUrl().replace(/\/$/, '');
	const redirectUri = encodeURIComponent(getLoginRedirectUri());
	window.location.href = `${apiBase}/auth/oauth/${provider}/login?redirect_uri=${redirectUri}`;
}

export interface OAuthCallbackParams {
	accessToken: string | null;
	oauthError: string | null;
	redirect: string | null;
}

export function parseOAuthCallbackParams(query: Record<string, unknown>): OAuthCallbackParams {
	const get = (key: string) => {
		const value = query[key];
		return typeof value === 'string' ? value : null;
	};
	return {
		accessToken: get('access_token'),
		oauthError: get('oauth_error'),
		redirect: get('redirect'),
	};
}

export function stripOAuthCallbackParams(query: Record<string, string | string[] | undefined | null>) {
	const next = { ...query };
	delete next.oauth_error;
	delete next.access_token;
	delete next.refresh_token;
	delete next.token_type;
	return next;
}

export function resolveOAuthRedirectTarget(redirect?: string | null) {
	const defaultPath = '/home';
	if (!redirect) return defaultPath;
	const normalized = redirect.startsWith('/') ? redirect : `/${redirect}`;
	if (!normalized.startsWith('/') || normalized.startsWith('//')) return defaultPath;
	return normalized;
}
