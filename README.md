# busy-tube

[日本語](README.ja.md)

busy-tube is a Claude Code plugin that summarizes new videos from your YouTube channels into a Markdown digest. It's meant for when you want what's in the videos but don't have time to watch them.

- **Full content, not just titles.** Gemini watches the video (audio and on-screen content), or Whisper transcribes it, or the captions are used. Videos without captions are covered too.
- **Free.** It needs no paid API. The cloud engines run on free tiers, and the local engines need no key at all.
- **Only what's new.** The plugin remembers which videos it has already summarized.
- **Your language.** Japanese is the default; you can change it with `config --lang`.

## Install

You need [uv](https://docs.astral.sh/uv/) and Claude Code.

```
/plugin marketplace add OzawaG/busy-tube
/plugin install busy-tube@busy-tube
```

## Use

Ask Claude in plain language:

- "Add https://www.youtube.com/@GoogleDevelopers to busy-tube"
- "Summarize my new YouTube videos"
- "Switch busy-tube to English" / "Use only whisper and captions"

The digest appears in chat and is also saved to `~/.busy-tube/digests/YYYY-MM-DD.md`.

## Engines

The plugin tries the engines in order and skips any that aren't set up. If one fails, for example because a free quota ran out, it moves on to the next. The default order is `gemini → groq → mlx-whisper → whisper → captions`.

| engine | setup | good at | limits |
|---|---|---|---|
| `gemini` | `export GEMINI_API_KEY=...` ([get a free key](https://aistudio.google.com/apikey)) | sees slides, code and on-screen text | about 20 requests/day on the free tier, 8 h of video/day, public videos only, free-tier inputs may be used by Google |
| `groq` | `export GROQ_API_KEY=...` ([get a free key](https://console.groq.com/keys)) + ffmpeg | very fast Whisper large-v3 | about 8 h of audio/day |
| `mlx-whisper` | Apple Silicon Mac + ffmpeg | fast, local, no key | Mac only |
| `whisper` | nothing (faster-whisper) | local, no key, any OS | slower, and needs a ~3 GB model download on first use |
| `captions` | nothing | instant | only works if the video has captions |

Run `uv run skills/busy-tube/scripts/busy_tube.py doctor` to see which engines are ready.

If a video fails on every engine, it isn't marked as seen, so it's retried on the next run.

## Settings

```bash
S=skills/busy-tube/scripts/busy_tube.py
uv run $S config --lang en --max 5 --engines groq,whisper,captions
uv run $S config --gemini-model gemini-3.8-flash --whisper-model large-v3
```

`--max` sets how many new videos to take per channel on each run. Your data lives in `~/.busy-tube/`; set `BUSY_TUBE_HOME` to put it somewhere else.

## Development

```bash
python3 skills/busy-tube/scripts/test_busy_tube.py   # unit tests, no deps
claude --plugin-dir .                                # try the plugin locally
```

## License

MIT
