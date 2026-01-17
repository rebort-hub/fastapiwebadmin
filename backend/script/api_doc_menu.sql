-- API 文档菜单数据
-- 请根据你的实际菜单表结构和现有数据调整 ID 和 parent_id

-- 1. 插入一级菜单：接口管理
INSERT INTO `menu` (`id`, `path`, `name`, `component`, `title`, `isLink`, `isHide`, `isKeepAlive`, `isAffix`, `isIframe`, `roles`, `icon`, `parent_id`, `redirect`, `sort`, `menu_type`, `lookup_id`, `active_menu`, `views`, `enabled_flag`, `created_by`, `updated_by`, `created_at`, `updated_at`)
VALUES 
(1000, '/apiDoc', 'apiDoc', 'Layout', '接口管理', 0, 0, 1, 0, 0, '["admin"]', 'ele-Document', 0, '/apiDoc/swagger', 90, 1, NULL, NULL, 0, 1, 1, 1, NOW(), NOW());

-- 2. 插入二级菜单：Swagger文档
INSERT INTO `menu` (`id`, `path`, `name`, `component`, `title`, `isLink`, `isHide`, `isKeepAlive`, `isAffix`, `isIframe`, `roles`, `icon`, `parent_id`, `redirect`, `sort`, `menu_type`, `lookup_id`, `active_menu`, `views`, `enabled_flag`, `created_by`, `updated_by`, `created_at`, `updated_at`)
VALUES 
(1001, '/apiDoc/swagger', 'apiDocSwagger', '/system/apiDoc/swagger', 'Swagger文档', 0, 0, 1, 0, 0, '["admin"]', 'ele-Postcard', 1000, NULL, 1, 1, NULL, NULL, 0, 1, 1, 1, NOW(), NOW());

-- 3. 插入二级菜单：Redoc文档
INSERT INTO `menu` (`id`, `path`, `name`, `component`, `title`, `isLink`, `isHide`, `isKeepAlive`, `isAffix`, `isIframe`, `roles`, `icon`, `parent_id`, `redirect`, `sort`, `menu_type`, `lookup_id`, `active_menu`, `views`, `enabled_flag`, `created_by`, `updated_by`, `created_at`, `updated_at`)
VALUES 
(1002, '/apiDoc/redoc', 'apiDocRedoc', '/system/apiDoc/redoc', 'Redoc文档', 0, 0, 1, 0, 0, '["admin"]', 'ele-Reading', 1000, NULL, 2, 1, NULL, NULL, 0, 1, 1, 1, NOW(), NOW());

-- 注意：
-- 1. 请根据你的实际菜单表最大 ID 调整上面的 ID (1000, 1001, 1002)
-- 2. 如果你的角色配置不同，请调整 roles 字段
-- 3. 如果你的图标库不同，请调整 icon 字段
-- 4. created_by 和 updated_by 请根据实际管理员 ID 调整
