# -*- coding: utf-8 -*-
"""部门树工具。"""

import typing


def collect_dept_descendants(
    all_depts: typing.Iterable[typing.Dict[str, typing.Any]],
    root_id: int,
) -> set[int]:
    """收集部门及其所有子部门 ID。"""
    children_map: dict[int, list[int]] = {}
    for dept in all_depts:
        parent_id = dept.get("parent_id") or 0
        children_map.setdefault(parent_id, []).append(dept["id"])

    result = {root_id}
    stack = [root_id]
    while stack:
        parent_id = stack.pop()
        for child_id in children_map.get(parent_id, []):
            if child_id not in result:
                result.add(child_id)
                stack.append(child_id)
    return result
