# busy-tube

[English](README.md)

登録した YouTube チャンネルの新着動画を、Markdown の要約にまとめる Claude Code プラグインです。情報収集はしたいけれど、動画を見る時間がない人向けです。

- **動画の中身まで把握して要約します。** Gemini が音声と画面の内容を解析するか、Whisper で文字起こしするか、字幕を使います。字幕のない動画にも対応しています。
- **無料で使えます。** 有料の API は使いません。クラウドの engine は無料枠で動き、ローカルの engine はキーも要りません。
- **新着だけを要約します。** 一度要約した動画は記録して、次回からは飛ばします。
- **要約の言語は選べます。** 既定は日本語で、`config --lang` で変更できます。

## インストール

[uv](https://docs.astral.sh/uv/) と Claude Code が必要です。

```
/plugin marketplace add OzawaG/busy-tube
/plugin install busy-tube@busy-tube
```

## 使い方

Claude に普通の言葉で頼んでください。

- 「https://www.youtube.com/@GoogleDevelopers を busy-tube に追加して」
- 「YouTube の新着を要約して」
- 「要約は英語にして」「whisper と字幕だけ使って」

要約はチャットに表示され、`~/.busy-tube/digests/YYYY-MM-DD.md` にも保存されます。

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

すべての engine で失敗した動画は既読にしないので、次回また試します。

## 設定

```bash
S=skills/busy-tube/scripts/busy_tube.py
uv run $S config --lang en --max 5 --engines groq,whisper,captions
uv run $S config --gemini-model gemini-3.8-flash --whisper-model large-v3
```

`--max` は、1 回の実行でチャンネルごとに取得する新着の上限です。データは `~/.busy-tube/` に保存されます。場所を変えたいときは `BUSY_TUBE_HOME` を設定してください。

## 開発

```bash
python3 skills/busy-tube/scripts/test_busy_tube.py   # 単体テスト（依存なし）
claude --plugin-dir .                                # ローカルで試す
```

## ライセンス

MIT
