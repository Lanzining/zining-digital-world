# L · ZINING V7

这一版加入「记忆展厅 / 照片管理」。

## 新功能
- L · CONTROL：上传照片
- 作品名称、日期、记忆片段
- 公开 / 私人可见范围
- 编辑 / 删除
- 公开照片自动进入网站的「记忆展厅」
- 点击照片进入沉浸式大图查看
- 服务器端权限：访客只能拿到公开作品，后台登录后才能管理全部作品

## Render
Root Directory 留空
Build Command:
`pip install -r server/requirements.txt`

Start Command:
`uvicorn server.server:app --host 0.0.0.0 --port $PORT`

环境变量继续保留：
- ADMIN_PASSWORD
- SESSION_SECRET

## 注意
Render 免费实例的文件系统不是永久存储。V7 用它把完整流程先跑通；不要把真正重要的私人照片当作永久备份。后续再接持久化数据库 + 私有对象存储。
