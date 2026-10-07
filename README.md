<h1 align="center">busy-tube</h1>
<p align="center">
  <strong>見る時間がない YouTube を、中身まで読める要約に。</strong>
</p>
<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/github/license/OzawaG/busy-tube?style=flat" alt="License"></a>
</p>

<p align="center">
  <strong title="日本語" aria-label="日本語">🇯🇵</strong> ·
  <a href=".github/readme/README.en.md" title="English" aria-label="English">🇬🇧</a> ·
  <a href=".github/readme/README.zh-CN.md" title="简体中文" aria-label="简体中文">🇨🇳</a> ·
  <a href=".github/readme/README.ko.md" title="한국어" aria-label="한국어">🇰🇷</a> ·
  <a href=".github/readme/README.es.md" title="Español" aria-label="Español">🇪🇸</a> ·
  <a href=".github/readme/README.pt-BR.md" title="Português (Brasil)" aria-label="Português (Brasil)">🇧🇷</a> ·
  <a href=".github/readme/README.fr.md" title="Français" aria-label="Français">🇫🇷</a> ·
  <a href=".github/readme/README.de.md" title="Deutsch" aria-label="Deutsch">🇩🇪</a> ·
  <a href=".github/readme/README.vi.md" title="Tiếng Việt" aria-label="Tiếng Việt">🇻🇳</a>
</p>

登録した YouTube チャンネルの新着動画を、Markdown の要約にまとめる Claude Code プラグインです。情報収集はしたいけれど、動画を見る時間がない人向けです。

- **動画の中身まで把握して要約します。** Gemini が音声と画面の内容を解析するか、Whisper で文字起こしするか、字幕を使います。字幕のない動画にも対応しています。
- **無料で使えます。** 有料の API は使いません。クラウドの engine は無料枠で動き、ローカルの engine はキーも要りません。
- **新着だけを要約します。** 一度要約した動画は記録して、次回からは飛ばします。
- **読みやすいページも作ります。** サムネイル、仕組みの図、その場面から再生できる時刻リンクが入ったページを公開します（Artifact ツールが使える場合）。
- **要約の言語は選べます。** 既定は日本語で、`config --lang` で変更できます。

## インストール

[uv](https://docs.astral.sh/uv/) と Claude Code が必要です。

```
/plugin marketplace add OzawaG/busy-tube
/plugin install busy-tube@busy-tube
```

## 使い方

Claude に普通の言葉で頼んでください。スラッシュコマンド `/busy-tube:busy-tube` でも呼べます。

- 「https://www.youtube.com/@GoogleDevelopers を busy-tube に追加して」
- 「YouTube の新着を要約して」
- 「要約は英語にして」「whisper と字幕だけ使って」

要約はチャットに表示され、`~/.busy-tube/digests/YYYY-MM-DD.md` にも保存されます。

Claude Code で Artifact ツールが使える場合（claude.ai と連携しているとき）は、要約を自分だけが見られる Web ページとしても公開します。ページには、サムネイル、動画の要点となる仕組みの図、その場面から再生できる時刻リンクが入ります。

## engine（中身の取得方法）

設定した順に試します。準備できていない engine は飛ばし、無料枠の上限などで失敗したら次の engine に移ります。既定の順番は `gemini → groq → mlx-whisper → whisper → captions` です。

| engine | 準備 | 得意なこと | 制約 |
|---|---|---|---|
| `gemini` | `export GEMINI_API_KEY=...`（[無料キー](https://aistudio.google.com/apikey)） | スライド・コード・画面の文字も拾える | 無料枠は 1 日 20 リクエスト程度、動画は合計 8 時間/日まで、公開動画のみ、入力は Google の製品改善に使われる |
| `groq` | `export GROQ_API_KEY=...`（[無料キー](https://console.groq.com/keys)）と ffmpeg | Whisper large-v3 で非常に速い | 1 日 8 時間分まで |
| `mlx-whisper` | Apple Silicon の Mac と ffmpeg | ローカルで速い。キー不要 | Mac 専用 |
| `whisper` | 準備不要（faster-whisper） | ローカル。キー不要。どの OS でも動く | 遅め。初回にモデルを約 3GB ダウンロードする |
| `captions` | 準備不要 | 一瞬で終わる | 字幕がある動画だけ |

どの engine が使えるかは `uv run skills/busy-tube/scripts/busy_tube.py doctor` で確認できます。

BGM だけの動画などで、文字起こしが意味のない文字列になることがあります。その場合は自動で見分けて、次の engine に回します。すべての engine で失敗した動画は既読にしないので、次回また試します。

## 設定

```bash
S=skills/busy-tube/scripts/busy_tube.py
uv run $S config --lang en --max 5 --engines groq,whisper,captions
uv run $S config --gemini-model gemini-3.8-flash --whisper-model large-v3
```

`--max` は、1 回の実行でチャンネルごとに取得する新着の上限です。データは `~/.busy-tube/` に保存されます。場所を変えたいときは `BUSY_TUBE_HOME` を設定してください。

## セキュリティ

動画のタイトル・説明文・字幕は他人が書いたものなので、AI への悪い指示が混ざっていることがあります。busy-tube は次の3つでこれを防ぎます。

- 動画の中身を読むのは、ファイルを読むことしかできない専用の要約エージェントだけです。
- 中身は「信頼できない内容」の印で囲んで渡します。
- 公開するページでは、文字をすべて無害化し、YouTube 以外のリンクを取り除きます。

API キーは環境変数からだけ読み、ファイルには保存しません。

## 開発

```bash
python3 skills/busy-tube/scripts/test_busy_tube.py   # 単体テスト（依存なし）
claude --plugin-dir .                                # ローカルで試す
```

## ライセンス

MIT
