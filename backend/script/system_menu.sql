-- 系统管理相关菜单
-- 请根据你的实际菜单表结构和现有数据调整 ID 和 parent_id

-- 查找"系统管理"的 parent_id（假设系统管理已存在）
-- 如果不存在，需要先创建系统管理菜单

-- 1. 文件管理菜单
INSERT INTO `menu` (`path`, `name`, `component`, `title`, `isLink`, `isHide`, `isKeepAlive`, `isAffix`, `isIframe`, `roles`, `icon`, `parent_id`, `redirect`, `sort`, `menu_type`, `enabled_flag`, `created_by`, `updated_by`, `creation_date`, `updation_date`)
VALUES 
('/system/file', 'systemFile', '/system/file/index', '文件管理', 0, 0, 1, 0, 0, '["admin"]', 'ele-Folder', 
(SELECT id FROM (SELECT id FROM menu WHERE name = 'system' LIMIT 1) AS temp), 
NULL, 50, 1, 1, 1, 1, NOW(), NOW());

-- 2. 系统监控菜单
INSERT INTO `menu` (`path`, `name`, `component`, `title`, `isLink`, `isHide`, `isKeepAlive`, `isAffix`, `isIframe`, `roles`, `icon`, `parent_id`, `redirect`, `sort`, `menu_type`, `enabled_flag`, `created_by`, `updated_by`, `creation_date`, `updation_date`)
VALUES 
('/system/monitor', 'systemMonitor', '/system/monitor/index', '系统监控', 0, 0, 1, 0, 0, '["admin"]', 'ele-Monitor', 
(SELECT id FROM (SELECT id FROM menu WHERE name = 'system' LIMIT 1) AS temp), 
NULL, 60, 1, 1, 1, 1, NOW(), NOW());

-- 注意：
-- 1. 请根据你的实际"系统管理"菜单的 name 调整 parent_id 查询
-- 2. 如果你的系统管理菜单 name 不是 'system'，请修改上面的查询
-- 3. sort 值请根据实际情况调整
-- 4. 如果需要其他角色访问，请修改 roles 字段
