# L · ZINING V6

这是为 Render 免费方案整理的“最省事部署版”。

## 结构
- `index.html`：公开世界
- `control.html`：L · CONTROL 管理后台
- `server/server.py`：FastAPI 后端
- `server/requirements.txt`：依赖
- `data/site.json`：当前网站内容
- `render.yaml`：Render 部署配置

## Render
推荐 Root Directory 留空。
Build Command:
`pip install -r server/requirements.txt`

Start Command:
`uvicorn server.server:app --host 0.0.0.0 --port $PORT`

计划选择 Free。

环境变量：
- `ADMIN_PASSWORD`：你自己设置的后台密码
- `SESSION_SECRET`：随机密钥（Render 可自动生成）

## 说明
V6 已把前台、后台和 API 放到同一个网站地址，避免 GitHub Pages 与 Render 之间的跨域/地址配置问题。
后台认证改为服务器端，不再使用 V5 的 `123456` 客户端密码。

Render 免费实例的文件系统不是持久存储，因此当前版本适合先上线、测试和搭建后台；如果以后要真正长期保存私人照片/私人档案，需要再接数据库和私有对象存储。
