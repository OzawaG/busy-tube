"""Turn a busy-tube digest (Markdown) into a single HTML page for a Claude artifact.

Pure functions only (no network, no files except the template), so they are tested directly.
Everything in the digest came from untrusted video content: it is escaped, links are limited
to YouTube, and Mermaid diagrams are reduced to plain flowchart syntax.
"""
import html
import re
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "digest-template.html"
# Page chrome per summary language; any language other than Japanese gets English.
UI = {
    "ja": {
        "source": {"gemini": "Gemini で映像ごと解析", "groq": "Groq で音声を文字起こし", "mlx-whisper": "ローカルで文字起こし",
                   "whisper": "ローカルで文字起こし", "captions": "字幕から"},
        "title": "busy-tube {m:02d}/{d:02d}号", "date": "{y}年{m}月{d}日",
        "h1_one": "{channel}<br>新着{n}本のまとめ", "h1_many": "YouTube 新着{n}本のまとめ",
        "lede_diagram": "各動画は「要約 → 図 → 要点」の順に読めます。", "lede_plain": "各動画は「要約 → 要点」の順に読めます。",
        "lede_tail": "要点は折りたたんであり、時刻を押すとその場面から再生できます。",
        "stats": "この号の概要", "videos": "本", "points": "要点", "channels": "チャンネル", "toc": "この号の動画",
        "open": "YouTube で「{title}」を開く", "play_from": "{ts} から再生", "figure": "図：この動画の仕組み・流れ",
        "all_points": "要点をすべて見る", "count": "{n}件・時刻から再生できます",
        "foot": "要約は busy-tube が動画の中身から作成しました。サムネイルの著作権は各チャンネルに帰属します。",
    },
    "en": {
        "source": {"gemini": "Gemini watched the video", "groq": "Transcribed with Groq", "mlx-whisper": "Transcribed locally",
                   "whisper": "Transcribed locally", "captions": "From captions"},
        "title": "busy-tube {m:02d}/{d:02d}", "date": "{y}-{m:02d}-{d:02d}",
        "h1_one": "{channel}<br>{n} new videos", "h1_many": "{n} new YouTube videos",
        "lede_diagram": "Each video reads summary → diagram → key points. ", "lede_plain": "Each video reads summary → key points. ",
        "lede_tail": "Key points are folded; tap a timestamp to play from that moment.",
        "stats": "This issue at a glance", "videos": "videos", "points": "key points", "channels": "channels",
        "toc": "Videos in this issue", "open": "Open “{title}” on YouTube", "play_from": "Play from {ts}",
        "figure": "Diagram: how it works in this video", "all_points": "All key points",
        "count": "{n} points · tap a time to play", "foot": "Summaries written by busy-tube from each video's content. Thumbnails belong to their channels.",
    },
}
YOUTUBE = ("https://youtu.be/", "https://www.youtube.com/")
VIDEO_ID = re.compile(r"[A-Za-z0-9_-]{11}")
TS_POINT = re.compile(r"\[(\d+:\d{2}(?::\d{2})?)\]\((https://youtu\.be/[A-Za-z0-9_-]{11}\?t=\d+)\)\s*(.*)")
MERMAID_HEAD = re.compile(r"(flowchart|graph)\s+(TD|TB|LR|RL|BT)")
MERMAID_DROP = ("click", "style", "classdef", "class ", "linkstyle", "%%", "call ", "href")


def inline(text):
    """Escape, then re-allow `code` and YouTube-only links."""
    t = html.escape(text, quote=False)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)

    def link(m):
        label, url = m.group(1), m.group(2)
        if not url.startswith(YOUTUBE):
            return label
        # text was escaped above with quote=False, so only `"` is left to escape in the attribute
        return f'<a href="{url.replace(chr(34), "&quot;")}" target="_blank" rel="noopener">{label}</a>'

    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, t)


def safe_mermaid(src):
    """Keep only plain flowchart statements; None if it isn't a usable flowchart."""
    lines = [l.rstrip() for l in src.strip().splitlines() if l.strip()]
    if not lines or not MERMAID_HEAD.fullmatch(lines[0].strip()) or len(lines) > 40:
        return None
    if any("%%" in l for l in lines):
        return None  # directives/comments can sit mid-line
    body = []
    for l in lines[1:]:  # ';' chains statements, so filter each one, not just the line start
        kept = [st for st in l.split(";") if st.strip() and not st.strip().lower().startswith(MERMAID_DROP)]
        if kept:
            body.append(";".join(kept))
    if not body or any(re.search(r"<\s*[A-Za-z/!]|&#|`", l) for l in body) or any("://" in l for l in body):
        return None  # html labels or URLs: not worth the risk
    return "\n".join([lines[0].strip()] + body)


def parse_digest(md):
    videos = []
    for block in md.split("\n### ")[1:]:
        lines = block.split("\n")
        if len(lines) < 2:
            continue
        m = re.match(r"\[(.+)\]\((https://www\.youtube\.com/watch\?v=([A-Za-z0-9_-]{11}))\)", lines[0])
        if not m:
            continue
        title, url, vid = m.groups()
        meta = [x.strip() for x in lines[1].rsplit("·", 2)]  # channel names may contain '·' 
        body = "\n".join(lines[2:])
        summary_part = body.split("**Summary**", 1)[-1].split("**Key points**", 1)[0]
        points_part = body.split("**Key points**", 1)[1] if "**Key points**" in body else ""
        diagram = None
        dm = re.search(r"```mermaid\n(.*?)```", points_part, re.S)
        if dm:
            diagram = safe_mermaid(dm.group(1))
            points_part = points_part[:dm.start()] + points_part[dm.end():]
        points, notes = [], []
        for l in points_part.split("\n"):
            if l.startswith("- "):
                points.append([l[2:], []])
            elif l.startswith("⚠"):
                notes.append(l)
            elif points and re.match(r"\s+(?:- |\d+\. )", l):
                points[-1][1].append(re.sub(r"^\s*(?:- |\d+\. )", "", l))
        videos.append({
            "id": vid, "title": title, "url": url,
            "channel": meta[0] if len(meta) > 2 else "",
            "date": meta[-2] if len(meta) > 1 else "",
            "source": meta[-1].replace("source:", "").strip() if meta else "",
            "summary": [s for s in summary_part.strip().split("\n") if s.strip()],
            "points": points, "notes": notes, "diagram": diagram,
        })
    return videos


def render_video(i, v, thumb, t):
    pts = []
    for text, subs in v["points"]:
        sub = ("<ul>" + "".join(f"<li>{inline(s)}</li>" for s in subs) + "</ul>") if subs else ""
        m = TS_POINT.match(text)
        if not m:
            pts.append(f'<li><span></span><div class="pt">{inline(text)}{sub}</div></li>')
            continue
        ts, turl, body = m.groups()
        pts.append(f'<li><a class="ts" href="{turl}" target="_blank" rel="noopener" '
                   f'aria-label="{t["play_from"].format(ts=ts)}">{ts}</a><div class="pt">{inline(body)}{sub}</div></li>')
    lead, rest = (v["summary"] or [""])[0], v["summary"][1:]
    img = (f'<img src="{thumb}" alt="" width="320" height="180">' if thumb else "")
    diagram = (f'<figure class="diagram"><pre class="mermaid">{html.escape(v["diagram"])}</pre>'
               f'<figcaption>{t["figure"]}</figcaption></figure>') if v["diagram"] else ""
    notes = "".join(f'<p class="note">{html.escape(n)}</p>' for n in v["notes"])
    title = html.escape(v["title"])
    date = html.escape(v["date"])
    source = html.escape(t["source"].get(v["source"], v["source"]))
    return f"""
<article class="video" id="v{i + 1}">
  <div class="v-top">
    <a class="thumb" href="{v['url']}" target="_blank" rel="noopener" aria-label="{t['open'].format(title=title)}">{img}
      <span class="play-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg></span></a>
    <div class="v-head">
      <p class="v-meta"><span>{html.escape(v['channel'])}</span><time datetime="{date}">{date[5:].replace('-', '/')}</time><span class="src">{source}</span></p>
      <h2><a href="{v['url']}" target="_blank" rel="noopener">{title}</a></h2>
    </div>
  </div>
  <div class="summary"><p class="lead">{inline(lead)}</p>{''.join(f'<p>{inline(s)}</p>' for s in rest)}</div>
  {notes}{diagram}
  <details>
    <summary><span class="chev" aria-hidden="true"></span>{t['all_points']}<span class="count">{t['count'].format(n=len(v['points']))}</span></summary>
    <ol class="timeline">{''.join(pts)}</ol>
  </details>
</article>"""


def render_page(videos, day, thumbs, lang="ja"):
    """videos from parse_digest; day 'YYYY-MM-DD'; thumbs {video_id: relative path}; lang = summary language."""
    t = UI["ja" if lang == "ja" else "en"]
    channels = list(dict.fromkeys(v["channel"] for v in videos if v["channel"]))
    heading = (t["h1_one"].format(channel=html.escape(channels[0]), n=len(videos)) if len(channels) == 1
               else t["h1_many"].format(n=len(videos)))
    y, m, d = (int(x) for x in day.split("-"))
    toc = "".join(
        f'<li><a href="#v{i + 1}"><span class="n">{i + 1}</span><span class="t">{html.escape(v["title"])}'
        f'<span class="c">{html.escape(v["channel"])}</span></span></a></li>' for i, v in enumerate(videos))
    lede = (t["lede_diagram"] if any(v["diagram"] for v in videos) else t["lede_plain"]) + t["lede_tail"]
    body = f"""<div class="wrap">
<header class="masthead">
  <p class="kicker"><span class="logo" aria-hidden="true"></span>busy-tube ・ {t['date'].format(y=y, m=m, d=d)}</p>
  <h1>{heading}</h1>
  <p class="lede">{lede}</p>
  <ul class="stats" aria-label="{t['stats']}"><li><b>{len(videos)}</b>{t['videos']}</li><li><b>{sum(len(v['points']) for v in videos)}</b>{t['points']}</li><li><b>{len(channels)}</b>{t['channels']}</li></ul>
</header>
<nav class="toc" aria-label="{t['toc']}"><ol>{toc}</ol></nav>
{''.join(render_video(i, v, thumbs.get(v['id']), t) for i, v in enumerate(videos))}
<footer class="foot"><p>{t['foot']}</p></footer>
</div>"""
    page = TEMPLATE.read_text(encoding="utf-8").replace("{{TITLE}}", t["title"].format(m=m, d=d))
    return page.replace("{{BODY}}", body)
