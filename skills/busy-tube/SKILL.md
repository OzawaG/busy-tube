---
name: busy-tube
description: Summarize new videos from a saved list of YouTube channels into a Markdown digest, using the full video content (Gemini video understanding, Whisper transcription, or captions) — free, no paid APIs. Use when the user wants to add/remove/list YouTube channels to follow, or asks for a digest/summary of new videos from their channels ("新着を要約して", "summarize my YouTube channels").
---

# busy-tube

Turns new uploads from the user's YouTube channels into a Markdown digest they can read instead of watching.

`S` below means: `uv run -q <this skill's base directory>/scripts/busy_tube.py`.
`uv` is required (https://docs.astral.sh/uv/). If missing, tell the user how to install it and stop.

## Manage channels

- Add: `S add <channel URL or @handle> [...]` (a video URL also works)
- Remove: `S remove <channel id | title | URL>`
- List: `S list`
- Settings: `S config --lang ja --max 3 --engines gemini,groq,mlx-whisper,whisper,captions`

## Make a digest

1. Fetch. Local Whisper packages are added only when needed, via `flags`:
   ```bash
   uv run -q $(S flags) <base dir>/scripts/busy_tube.py fetch
   ```
   - This can take minutes: audio is downloaded and transcribed per video. Use a long Bash timeout (10 min). With many channels, run it in the background.
   - The script prints JSON:
     - `lang`
     - `digest_path`
     - `videos[]` (`id`, `title`, `channel`, `published`, `url`, `source`, `path`, `chars`)
     - `failed[]`
   - If `videos` is empty, say there is nothing new (and show `failed`, if any). Then stop.
2. Summarize each video from its file at `path`. The file holds the description plus the full content (Gemini notes or a timestamped transcript).
   - If `chars` > 30000, delegate that video to a subagent. Give it the file path and the format below, and have it return only the finished section, so the long transcript stays out of the main context.
   - Never summarize from the title or description alone.
3. Write the digest in the language `lang`, using the format below. Show it in chat, and write it to `digest_path`. If that file already exists, append to it.
4. Mark only the summarized videos as seen: `S mark-seen <id> <id> ...`. Videos listed in `failed` stay unseen and are retried next run.
5. If `failed` is non-empty, list each title with a one-line reason. If every engine was skipped, run `S doctor` and point to the setup below.

## Digest format

```markdown
# YouTube digest — YYYY-MM-DD

## <Channel name>

### [<Video title>](<url>)
<published> · source: <source>

**Summary**
<3 lines that capture what the video is about and its conclusion>

**Key points**
- [M:SS](https://youtu.be/<id>?t=<seconds>) <point>
- ...
```

Key points have no fixed count. Add a point whenever:
- the topic, theme or genre changes;
- something important is said or shown;
- the speaker clearly wants to get something across.

Each point needs the timestamp link where it starts, and concrete details: names, numbers, steps, conclusions. Group videos under their channel.

## Engines (how the full content is obtained)

They are tried in the configured order. An engine that is unavailable (missing key or package) is skipped, and a failure (e.g. a free-quota 429) falls through to the next one.

| engine | needs | notes |
|---|---|---|
| `gemini` | `GEMINI_API_KEY` (free at https://aistudio.google.com/apikey) | Watches audio **and** visuals. Free tier: about 20 requests/day on Flash models, 8 h of YouTube video/day, public videos only. Free-tier inputs may be used by Google to improve products. |
| `groq` | `GROQ_API_KEY` (free at https://console.groq.com/keys) + ffmpeg | Whisper large-v3, very fast. Free tier is about 8 h of audio/day. |
| `mlx-whisper` | Apple Silicon Mac + ffmpeg | Local and free. Downloads the model on first use. |
| `whisper` | nothing extra (faster-whisper is pulled in by `flags`) | Local and free, works on any OS, slower. Downloads about 3 GB on first use. |
| `captions` | nothing | YouTube captions. Only works when the video has them. |

First-time users: run `S doctor`, show the result, and explain which keys they can add for better results. API keys are read from environment variables only, so never write them to files.
