# -*- coding: utf-8 -*-
# @author: rebort
from fastapi.requests import Request

from app.corelibs.codes import CodeEnum
from app.corelibs.custom_router import APIRouter
from app.schemas.system.user import UserLogin, UserQuery, UserIn, UserResetPwd, UserDel, UserUpdateAvatar
from app.services.system.user import UserService
from app.utils.response import HttpResponse

router = APIRouter()


@router.post("/login", description="登录")
async def login(params: UserLogin):
    data = await UserService.login(params)
    return await HttpResponse.success(data, msg="登录成功！")


@router.post("/logout", description="登出")
async def logout():
    await UserService.logout()
    return await HttpResponse.success()


@router.post("/list", description="用户列表")
async def user_list(params: UserQuery):
    data = await UserService.list(params)
    return await HttpResponse.success(data)


@router.post('/saveOrUpdate', description="更新保存用户")
async def save_or_update(user_params: UserIn):
    """
    更新保存用户
    :return:
    """
    await UserService.save_or_update(user_params)
    return await HttpResponse.success()


@router.post('/getUserInfoByToken', description="通过token获取用户信息")
async def get_user_info():
    """
    根据token获取用户信息
    :return:
    """
    user_info = await UserService.get_user_info_by_token()
    return await HttpResponse.success(user_info)


@router.post('/userRegister', description="新增用户")
async def user_register(user_info: UserIn):
    data = await UserService.user_register(user_info)
    return await HttpResponse.success(data)


@router.post('/resetPassword', description="修改密码")
async def reset_password(params: UserResetPwd):
    await UserService.reset_password(params)
    return await HttpResponse.success()


@router.post('/adminResetPassword', description="管理员重置用户密码")
async def admin_reset_password(params: UserDel):
    """
    管理员重置用户密码为默认密码 123456
    :param params: 包含用户 id
    :return:
    """
    await UserService.admin_reset_password(params.id)
    return await HttpResponse.success(msg='密码已重置为：123456')


@router.post('/updateUserAvatar', description="更新用户头像")
async def update_user_avatar(params: UserUpdateAvatar):
    """
    更新用户头像
    :param params: 包含用户 id 和 avatar
    :return:
    """
    await UserService.update_user_avatar(params.id, params.avatar)
    return await HttpResponse.success(msg='头像更新成功')


@router.post('/getUserInfo', description="获取用户信息")
async def get_user_info(params: UserDel):
    """
    根据用户 id 获取用户信息
    :param params: 包含用户 id
    :return:
    """
    user_info = await UserService.get_user_info(params.id)
    return await HttpResponse.success(user_info)


@router.post('/deleted', description="删除用户")
async def deleted(params: UserDel):
    data = await UserService.deleted(params)
    return await HttpResponse.success(data)


@router.post('/authorizeToken', description="校验token是否有效")
async def authorize_token(request: Request):
    token = request.headers.get("token", None)
    user_info = await UserService.check_token(token)
    return await HttpResponse.success(user_info)


@router.post('/getMenuByToken', description="根据token获取菜单数据")
async def get_menu_by_token():
    user_info = await UserService.get_menu_by_token()
    return await HttpResponse.success(user_info)


@router.post('/getButtonPermissions', description="根据token获取按钮权限")
async def get_button_permissions():
    permissions = await UserService.get_button_permissions()
    return await HttpResponse.success(permissions)


@router.post('/debugUserPermissions', description="调试用户权限数据")
async def debug_user_permissions():
    """调试接口：查看用户的完整权限数据"""
    from app.models.system_models import Menu, Roles
    from app.utils.current_user import current_user
    
    # 获取当前用户
    token_user_info = await current_user()
    user_info = await User.get(token_user_info.get("id"))
    
    debug_info = {
        "user": {
            "id": user_info.id,
            "username": user_info.username,
            "user_type": user_info.user_type,
            "user_type_name": "超级管理员" if user_info.user_type == 10 else "普通用户",
            "roles": user_info.roles
        },
        "buttons_in_db": [],
        "user_roles": [],
        "assigned_menu_ids": [],
        "assigned_buttons": [],
        "final_auth_list": []
    }
    
    # 1. 查询数据库中所有按钮权限
    all_buttons = await Menu.get_all_buttons()
    debug_info["buttons_in_db"] = [
        {"id": btn.get("id"), "title": btn.get("title"), "roles": btn.get("roles")}
        for btn in all_buttons
    ]
    debug_info["buttons_in_db_count"] = len(all_buttons)
    
    # 2. 获取用户权限
    if user_info.user_type == 10:
        # 超级管理员
        debug_info["final_auth_list"] = [btn.get('roles') for btn in all_buttons if btn.get('roles')]
    else:
        # 普通用户
        if user_info.roles:
            roles = await Roles.get_roles_by_ids(user_info.roles)
            debug_info["user_roles"] = [
                {"id": r.get("id"), "name": r.get("name"), "menus": r.get("menus")}
                for r in roles
            ]
            
            menu_ids = []
            for role in roles:
                if role.get('menus'):
                    menu_ids += list(map(int, role['menus'].split(',')))
            
            debug_info["assigned_menu_ids"] = list(set(menu_ids))
            
            if menu_ids:
                buttons = await Menu.get_buttons_by_ids(list(set(menu_ids)))
                debug_info["assigned_buttons"] = [
                    {"id": btn.get("id"), "title": btn.get("title"), "roles": btn.get("roles")}
                    for btn in buttons
                ]
                debug_info["final_auth_list"] = [btn.get('roles') for btn in buttons if btn.get('roles')]
    
    # 3. 获取完整的用户信息（包含权限）
    full_user_info = await UserService.get_user_info_by_token()
    debug_info["returned_user_info"] = full_user_info
    
    return await HttpResponse.success(debug_info)
