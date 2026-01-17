#### 🌈 介绍
基于Fastapi框架，结合vue3+elementplus开发的一个开箱即用的纯净后端管理系统，包含完整的用户权限管理系统，旨在帮助企业开发者快速搭建
开发后台脚手，无需关注认证实现，只需要实现自己的业务功能，动态路由注册，配置即可分配权限管控

#### 后端

- 使用软件版本
- python version <= 3.13
- mysql version 8.0.23
- redis version 6.0.9
- node version 18.15.0

#### 后端架构：
 • FastAPI 异步框架 + SQLAlchemy 2.0 异步ORM 
 • Redis 异步连接池（自定义扩展） 
 • Celery 异步任务队列 + Beat 定时任务 
 • 统一异常处理和响应封装 
 • 请求中间件（日志、鉴权、trace_id）
 • 自定义日志系统（Loguru） 
 • 依赖注入和会话管理 
 • 分层架构（apis/services/models/schemas）  

#### 前端架构： 
 • Vue 3 + Vite + TypeScript 
 • Element Plus UI 组件库 
 • Pinia 状态管理 + 持久化 
 • 前后端路由控制 
 • 权限指令系统 
 • Monaco 代码编辑器 
 • 主题配置和暗黑模式 
 • 完整的布局系统
 • 动态路由注册，前端菜单管理添加菜单后，即可分配权限使用
 
 ### 1. 数据库初始化（一键完成）

**推荐方式**：

**前置条件**：
1. 创建数据库：`CREATE DATABASE fastapiwebadmin CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;`
2. 配置 `cp.env.example 重命名为.env` 修改文件中的数据库连接
3. 安装依赖驱动：`pip install requirements`


---

### 2. 使用 Alembic

如果你需要手动管理迁移：

```bash
# 初始化
python cli.py init-db

# 生成迁移文件
alembic revision --autogenerate -m "描述信息"

# 执行迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

#### 前端

- 基于 vite + vue3 + + Pinia + element-plus

#### 💒 平台地址地址
- github 
https://github.com/rebort-hub

- 登录页
  ![](static/img/func.png)
- 首页
  ![](static/img/index.png)
- 路由菜单管理页面
  ![](static/img/report.png)
- 接口管理页面
  ![](static/img/case.png)
  ![](static/img/cass.png)
- 个人中心
  ![](static/img/ge.png)
- 主题自定义切换
  ![](static/img/csssb.png)
  ![](static/img/csssa.png)
  ![](static/img/qy.png)



#### 🚧 项目启动初始化-后端

```bash
# 克隆项目
git clone https://github.com/rebort-hub/fastapiwebadmin.git

# 数据库脚本，需要新建数据库 fastapiwebadmin
backend/script/db_init.sql  

# 修改对应的数据库地址，redis 地址
backend/config.py
# 或者
backend/.env # 环境文件中的地址修改

# 安装依赖
pip install -r  requirements

# 运行项目 /backend 目录下执行
python main.py

# 异步任务依赖 celery 启动命令

#  windows 启动，只能单线程 /backend 目录下执行
celery -A celery_worker.worker.celery worker --pool=solo -l INFO 

# linux 启动
elery -A celery_worker.worker.celery worker --loglevel=INFO -c 10 -P solo -n fastapiwebadmin-celery-worker

# 定时任务启动
celery -A celery_worker.worker.celery beat -S celery_worker.scheduler.schedulers:DatabaseScheduler -l INFO

# 定时任务心跳启动
celery -A celery_worker.worker.celery beat  -l INFO 

```

#### 🚧 项目启动初始化-前端

```bash
# node 版本
node -v 
v18.15.0
```

- 复制代码(桌面 cmd 运行) `npm install -g cnpm --registry=https://registry.npm.taobao.org`
- 复制代码(桌面 cmd 运行) `npm install -g yarn`

```bash
# 克隆项目
git clone https://github.com/rebort-hub/fastapiwebadmin.git

# 进入项目
cd /frontend

# 安装依赖
cnpm install 
# 或者
yarn insatll

# 运行项目
cnpm run dev
# 或者 
yarn dev

# 打包发布
cnpm run build
# 或者 
yarn build
```

#### 💯 学习交流加 微信 群

- 或者添加我的微信，或者你们进入交流群
  ![](static/img/weixin.png)
  ![](static/img/qq.png)


#### 💌 支持作者

如果觉得框架不错，已经在使用了，希望你可以在 <a target="_blank" href="https://github.com/rebort-hub/fastapiwebadmin">
Github</a> 帮我点个 ⭐ Star，平台会持续迭代更新。感谢各位老铁
