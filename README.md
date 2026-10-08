# L · ZINING V16 — Editorial Digital World

这是一次完整重构，不再沿用 V14/V15 的视觉语言。

## 设计
- 未来数字建筑 × 高级艺术馆 × 编辑杂志
- 暖白 / 石墨 / 雾灰 / 银蓝
- 大留白、衬线花体、建筑构图、极少量动态
- L 是品牌符号，不是巨大圆形按钮
- 动效服务于空间关系，不制造廉价科技噪音
- 响应式桌面 / 平板 / 手机

## 数据与后台
前台与 L · CONTROL 共用 `/api/public` 与服务器 `site.json`。
后台可直接管理：首页、记忆、思绪、旅途、音乐、收藏、未来、心境、环境声音、昼夜、空间互动。
新增内容保存后立即从公开 API 进入前台，不需要再次修改 HTML。

## 部署
继续使用 Render：
Build: `pip install -r server/requirements.txt`
Start: `uvicorn server.server:app --host 0.0.0.0 --port $PORT`
Root Directory 留空。
