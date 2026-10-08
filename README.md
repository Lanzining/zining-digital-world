# L · ZINING V16 — Editorial Digital World

这是一次完整重构，不再沿用 V14/V15 的视觉语言。

## 设计
- 未来数字建筑 × 高级艺术馆 × 编辑杂志
- 暖白 / 石墨 / 雾灰 / 银蓝
- 大留白、衬线花体、建筑构图、极少量动态
- L 是品牌符号，不是巨大圆形按钮
- 动效服务于空间关系，不制造廉价科技噪音
- 响应式桌面 / 平板 / 手机

## 字体与排版（本次修正）
问题：标题字号按拉丁字体设计，中文回落后行高只有 0.78–0.9，且 `.hero h1` 用了 `max-width:7ch`
（`ch` 是拉丁数字宽度），导致中文标题被强行折成 4–5 行并互相重叠。

修正要点：
1. 字体栈补上中文衬线回退：`Songti SC / STSong / Source Han Serif SC / Noto Serif SC / SimSun`，
   拉丁仍用 Cormorant Garamond；`--sans` 同理补 `PingFang SC / Microsoft YaHei / Noto Sans SC`。
2. 字号改为按中文单行字数反推的 `clamp()`：主标题 2 行、章节标题收敛到单行可容纳，
   并去掉 `max-width:7ch`。
3. 行高改为中文安全的 1.16–1.3（原 0.78–1.05），字距去掉负值（原 `-.055em` 会让汉字贴到一起）。
4. `body` 统一 `line-height:1.75`、`line-break:strict`，正文字号 11–12px → 12–13px。
5. 字体加载由 `<style>` 内的 `@import` 改为 `preconnect + <link>`，首屏不再被字体请求阻塞；
   后台表单控件补 `font: inherit`（原来输入框不继承字体）。
6. 弹层（`.sheet h3` / `.item h4`）与 `control.html` 的 `.title`、`.item h3` 同步修正。

> 国内网络若访问不到 `fonts.googleapis.com`，把 head 里的字体 `<link>` 换成镜像
> （如 `https://fonts.loli.net/css2?...`，参数不变）即可，字体栈已保证取不到网络字体时也能正常显示。

## 数据与后台
前台与 L · CONTROL 共用 `/api/public` 与服务器 `site.json`。
后台可直接管理：首页、记忆、思绪、旅途、音乐、收藏、未来、心境、环境声音、昼夜、空间互动。
新增内容保存后立即从公开 API 进入前台，不需要再次修改 HTML。

## 部署
继续使用 Render：
Build: `pip install -r server/requirements.txt`
Start: `uvicorn server.server:app --host 0.0.0.0 --port $PORT`
Root Directory 留空。
