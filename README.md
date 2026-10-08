# L · ZINING V10

这一版把「记忆展厅」升级为更完整的私人数字美术馆视觉。

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

## V10 视觉升级
- 不规则美术馆式作品排布
- 悬浮、月光、玻璃、金属感光影
- 作品 hover 光影与空间反馈
- 沉浸式作品查看器
- 作品编号 / 标题 / 文字 / 日期
- 移动端专门布局


## V10 更新

- 修复记忆展厅在部分桌面浏览器出现横向滚动条的问题
- 强化响应式宽度约束，避免图片和网格撑破页面
- 保留 V10 的私人数字美术馆视觉与照片管理功能
- 移动端与桌面端的展厅边界更稳定


## V10
新增 L · ZINING 世界入口导航：MEMORY、THOUGHTS、MOOD、JOURNEY、MUSIC、COLLECTION、FUTURE 与 L · CONTROL。记忆展厅继续保留 V9 的私人数字美术馆体验，其余房间先建立空间骨架，后续逐个开启。
