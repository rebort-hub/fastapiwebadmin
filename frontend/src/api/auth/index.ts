import request from '/@/utils/request';

export interface CaptchaResponse {
	enable?: boolean;
	img_base?: string;
	key?: string;
	register_enabled?: boolean;
}

export interface EmailCodeParams {
	username: string;
	title: string;
	mail: string;
}

export interface RegisterParams {
	username: string;
	password: string;
	email: string;
	code?: string;
	nickname?: string;
}

export interface ForgetPasswordParams {
	username: string;
	email: string;
	code: string;
	new_password: string;
}

export function useAuthApi() {
	return {
		getCaptcha: () => {
			return request({
				url: '/auth/captcha/get',
				method: 'GET',
			});
		},
		sendEmailCode: (data: EmailCodeParams) => {
			return request({
				url: '/auth/code',
				method: 'POST',
				data,
			});
		},
		register: (data: RegisterParams) => {
			return request({
				url: '/auth/register',
				method: 'POST',
				data,
			});
		},
		forgetPassword: (data: ForgetPasswordParams) => {
			return request({
				url: '/auth/forget-password',
				method: 'POST',
				data,
			});
		},
	};
}
