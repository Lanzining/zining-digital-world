# L · ZINING — V14 · Spatial Liquid Glass

V14 是第一阶段 **Spatial Core**：把首页从“网页”改成一个可进入的数字空间。

### 本版重点
- 深灰/冷银/雾蓝基底，降低纯黑与廉价霓虹感
- L 作为空间核心，而不是普通按钮
- 8 个模块成为空间中的 Glass Objects
- 鼠标/触控成为 Light Field：玻璃高光、雾层、空间位移随观察者变化
- Frost / glass / edge light / shadow / depth 多层材质
- MEMORY 与现有后端记忆数据直接连接
- L · CONTROL 保留原有后台入口
- 移动端触摸适配
- prefers-reduced-motion 支持

### Render
继续使用原 V11 的部署方式：
- Root Directory：留空
- Build Command：`pip install -r server/requirements.txt`
- Start Command：`uvicorn server.server:app --host 0.0.0.0 --port $PORT`

本版没有修改已有后台认证和 Memory API。
