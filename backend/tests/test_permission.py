# -*- coding: utf-8 -*-
import pytest

from app.core.permission import PermissionService


def test_expand_permission_aliases():
    codes = PermissionService.expand_permission_codes(["user:resetpwd"])
    assert "user:resetpwd" in codes
    assert "user:resetPwd" in codes


def test_has_any_permission_with_alias():
    user_codes = ["user:query", "user:resetpwd", "user:resetPwd"]
    assert PermissionService.has_any_permission(user_codes, ["user:resetPwd"])
    assert PermissionService.has_any_permission(user_codes, ["user:resetpwd"])
    assert not PermissionService.has_any_permission(user_codes, ["user:delete"])


def test_is_super_admin():
    assert PermissionService.is_super_admin(10)
    assert not PermissionService.is_super_admin(20)
