<h1 align="center">busy-tube</h1>
<p align="center">
  <strong>没空看的 YouTube，变成连内容都读得懂的摘要。</strong>
</p>
<p align="center">
  <a href="../../LICENSE"><img src="https://img.shields.io/github/license/OzawaG/busy-tube?style=flat" alt="License"></a>
</p>

<p align="center">
  <a href="../../README.md" title="日本語" aria-label="日本語">🇯🇵</a> ·
  <a href="README.en.md" title="English" aria-label="English">🇬🇧</a> ·
  <strong title="简体中文" aria-label="简体中文">🇨🇳</strong> ·
  <a href="README.ko.md" title="한국어" aria-label="한국어">🇰🇷</a> ·
  <a href="README.es.md" title="Español" aria-label="Español">🇪🇸</a> ·
  <a href="README.pt-BR.md" title="Português (Brasil)" aria-label="Português (Brasil)">🇧🇷</a> ·
  <a href="README.fr.md" title="Français" aria-label="Français">🇫🇷</a> ·
  <a href="README.de.md" title="Deutsch" aria-label="Deutsch">🇩🇪</a> ·
  <a href="README.vi.md" title="Tiếng Việt" aria-label="Tiếng Việt">🇻🇳</a>
</p>

busy-tube 是一个 Claude Code 插件，可以把你订阅的 YouTube 频道的新视频整理成 Markdown 摘要。适合想及时获取信息、却没时间看视频的人。

- **基于视频实际内容进行摘要。** 由 Gemini 分析音频和画面内容，或用 Whisper 转写语音，或直接使用字幕。没有字幕的视频也支持。
- **免费使用。** 不使用任何付费 API。云端 engine 在免费额度内运行，本地 engine 则完全不需要密钥。
- **只摘要新视频。** 已摘要过的视频会被记录，之后的运行中自动跳过。
- **还能生成便于阅读的页面。** 发布包含缩略图、原理示意图，以及可从对应场景直接播放的时间戳链接的页面（在 Artifact 工具可用时）。
- **摘要语言可选。** 默认为日语，可通过 `config --lang` 修改。

## 安装

需要 [uv](https://docs.astral.sh/uv/) 和 Claude Code。

```
/plugin marketplace add OzawaG/busy-tube
/plugin install busy-tube@busy-tube
```

## 使用方法

直接用自然语言告诉 Claude 即可。也可以通过斜杠命令 `/busy-tube:busy-tube` 调用。

- “把 https://www.youtube.com/@GoogleDevelopers 添加到 busy-tube”
- “帮我摘要一下 YouTube 的新视频”
- “摘要改成英文”“只用 whisper 和字幕”

摘要会显示在聊天中，同时保存到 `~/.busy-tube/digests/YYYY-MM-DD.md`。

如果 Claude Code 中可以使用 Artifact 工具（即已与 claude.ai 关联时），摘要还会发布为仅自己可见的网页。页面包含缩略图、视频核心原理的示意图，以及可从对应场景开始播放的时间戳链接。

## engine（内容获取方式）

按设置的顺序依次尝试。未准备好的 engine 会被跳过；若因免费额度上限等原因失败，则转到下一个 engine。默认顺序为 `gemini → groq → mlx-whisper → whisper → captions`。

| engine | 准备工作 | 擅长 | 限制 |
|---|---|---|---|
| `gemini` | `export GEMINI_API_KEY=...`（[免费密钥](https://aistudio.google.com/apikey)） | 能识别幻灯片、代码和画面中的文字 | 免费额度约每天 20 次请求，视频合计每天最多 8 小时，仅限公开视频，输入内容会被 Google 用于改进产品 |
| `groq` | `export GROQ_API_KEY=...`（[免费密钥](https://console.groq.com/keys)）和 ffmpeg | 使用 Whisper large-v3，速度非常快 | 每天最多 8 小时 |
| `mlx-whisper` | Apple Silicon 的 Mac 和 ffmpeg | 本地运行且速度快，无需密钥 | 仅限 Mac |
| `whisper` | 无需准备（faster-whisper） | 本地运行，无需密钥，任何操作系统都能用 | 较慢，首次运行需下载约 3GB 的模型 |
| `captions` | 无需准备 | 瞬间完成 | 仅限有字幕的视频 |

可以通过 `uv run skills/busy-tube/scripts/busy_tube.py doctor` 查看哪些 engine 可用。

对于只有背景音乐的视频等，转写结果可能是毫无意义的文字。此时会自动识别并交给下一个 engine。所有 engine 都失败的视频不会标记为已读，下次会再次尝试。

## 设置

```bash
S=skills/busy-tube/scripts/busy_tube.py
uv run $S config --lang en --max 5 --engines groq,whisper,captions
uv run $S config --gemini-model gemini-3.8-flash --whisper-model large-v3
```

`--max` 是每次运行时每个频道获取新视频的上限。数据保存在 `~/.busy-tube/`。如需更改位置，请设置 `BUSY_TUBE_HOME`。

## 安全

视频的标题、简介和字幕都由他人撰写，其中可能混有针对 AI 的恶意指令。busy-tube 通过以下三点加以防范：

- 只有专用的摘要代理会读取视频内容，而它只能读取文件。
- 内容会用“不可信内容”的标记包裹后再传递。
- 在发布的页面中，所有文字都会经过无害化处理，并移除 YouTube 以外的链接。

API 密钥只从环境变量读取，不会保存到文件中。

## 开发

```bash
python3 skills/busy-tube/scripts/test_busy_tube.py   # 单元测试（无依赖）
claude --plugin-dir .                                # 在本地试用
```

## 许可证

MIT
