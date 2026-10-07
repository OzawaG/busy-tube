<h1 align="center">busy-tube</h1>
<p align="center">
  <strong>The YouTube you have no time to watch, turned into summaries that actually cover the content.</strong>
</p>
<p align="center">
  <a href="../../LICENSE"><img src="https://img.shields.io/github/license/OzawaG/busy-tube?style=flat" alt="License"></a>
</p>

<p align="center">
  <a href="../../README.md" title="日本語" aria-label="日本語">🇯🇵</a> ·
  <strong title="English" aria-label="English">🇬🇧</strong> ·
  <a href="README.zh-CN.md" title="简体中文" aria-label="简体中文">🇨🇳</a> ·
  <a href="README.ko.md" title="한국어" aria-label="한국어">🇰🇷</a> ·
  <a href="README.es.md" title="Español" aria-label="Español">🇪🇸</a> ·
  <a href="README.pt-BR.md" title="Português (Brasil)" aria-label="Português (Brasil)">🇧🇷</a> ·
  <a href="README.fr.md" title="Français" aria-label="Français">🇫🇷</a> ·
  <a href="README.de.md" title="Deutsch" aria-label="Deutsch">🇩🇪</a> ·
  <a href="README.vi.md" title="Tiếng Việt" aria-label="Tiếng Việt">🇻🇳</a>
</p>

busy-tube is a Claude Code plugin that turns new videos from the YouTube channels you follow into Markdown summaries. It is for people who want to keep up but don't have time to watch.

- **Summaries based on what's actually in the video.** Gemini analyzes the audio and on-screen content, Whisper transcribes the audio, or existing captions are used. Videos without captions work too.
- **Free to use.** No paid APIs. Cloud engines run within free tiers, and local engines need no key at all.
- **Only new videos.** Every summarized video is recorded and skipped on later runs.
- **Readable pages, too.** It publishes a page with thumbnails, a diagram of how things work, and timestamp links that jump straight to each scene (when the Artifact tool is available).
- **Choose your summary language.** The default is Japanese; change it with `config --lang`.

## Installation

You need [uv](https://docs.astral.sh/uv/) and Claude Code.

```
/plugin marketplace add OzawaG/busy-tube
/plugin install busy-tube@busy-tube
```

## Usage

Just ask Claude in plain language. You can also invoke it with the slash command `/busy-tube:busy-tube`.

- "Add https://www.youtube.com/@GoogleDevelopers to busy-tube"
- "Summarize my new YouTube videos"
- "Write the summaries in English" / "Only use whisper and captions"

Summaries are shown in the chat and also saved to `~/.busy-tube/digests/YYYY-MM-DD.md`.

If the Artifact tool is available in Claude Code (when it's connected to claude.ai), the summary is also published as a private web page only you can see. The page includes thumbnails, a diagram of the key mechanism in each video, and timestamp links that start playback at the relevant scene.

## Engines (how content is retrieved)

Engines are tried in the configured order. Engines that aren't set up are skipped, and if one fails (for example, by hitting a free-tier limit), the next one is used. The default order is `gemini → groq → mlx-whisper → whisper → captions`.

| engine | Setup | Strengths | Limitations |
|---|---|---|---|
| `gemini` | `export GEMINI_API_KEY=...` ([free key](https://aistudio.google.com/apikey)) | Also picks up slides, code, and on-screen text | Free tier allows roughly 20 requests/day and up to 8 hours of video/day in total; public videos only; inputs are used by Google to improve its products |
| `groq` | `export GROQ_API_KEY=...` ([free key](https://console.groq.com/keys)) and ffmpeg | Very fast with Whisper large-v3 | Up to 8 hours of audio per day |
| `mlx-whisper` | An Apple Silicon Mac and ffmpeg | Fast and local. No key needed | Mac only |
| `whisper` | No setup (faster-whisper) | Local. No key needed. Runs on any OS | Slower. Downloads a ~3GB model on first run |
| `captions` | No setup | Finishes instantly | Only videos that have captions |

Check which engines are available with `uv run skills/busy-tube/scripts/busy_tube.py doctor`.

For videos with only background music, a transcript can come out as meaningless text. busy-tube detects this automatically and moves on to the next engine. Videos that fail on every engine are not marked as seen, so they are retried next time.

## Configuration

```bash
S=skills/busy-tube/scripts/busy_tube.py
uv run $S config --lang en --max 5 --engines groq,whisper,captions
uv run $S config --gemini-model gemini-3.8-flash --whisper-model large-v3
```

`--max` is the maximum number of new videos fetched per channel in a single run. Data is stored in `~/.busy-tube/`. To use a different location, set `BUSY_TUBE_HOME`.

## Security

Video titles, descriptions, and captions are written by other people, so they may contain malicious instructions aimed at the AI. busy-tube guards against this in three ways:

- Video content is read only by a dedicated summarizer agent that can do nothing but read files.
- The content is passed wrapped in markers that flag it as untrusted.
- On published pages, all text is sanitized and any non-YouTube links are removed.

API keys are read only from environment variables and are never saved to files.

## Development

```bash
python3 skills/busy-tube/scripts/test_busy_tube.py   # unit tests (no dependencies)
claude --plugin-dir .                                # try it locally
```

## License

MIT
