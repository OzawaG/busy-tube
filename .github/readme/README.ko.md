<h1 align="center">busy-tube</h1>
<p align="center">
  <strong>볼 시간이 없는 YouTube를, 내용까지 읽히는 요약으로.</strong>
</p>
<p align="center">
  <a href="../../LICENSE"><img src="https://img.shields.io/github/license/OzawaG/busy-tube?style=flat" alt="License"></a>
</p>

<p align="center">
  <a href="../../README.md" title="日本語" aria-label="日本語">🇯🇵</a> ·
  <a href="README.en.md" title="English" aria-label="English">🇬🇧</a> ·
  <a href="README.zh-CN.md" title="简体中文" aria-label="简体中文">🇨🇳</a> ·
  <strong title="한국어" aria-label="한국어">🇰🇷</strong> ·
  <a href="README.es.md" title="Español" aria-label="Español">🇪🇸</a> ·
  <a href="README.pt-BR.md" title="Português (Brasil)" aria-label="Português (Brasil)">🇧🇷</a> ·
  <a href="README.fr.md" title="Français" aria-label="Français">🇫🇷</a> ·
  <a href="README.de.md" title="Deutsch" aria-label="Deutsch">🇩🇪</a> ·
  <a href="README.vi.md" title="Tiếng Việt" aria-label="Tiếng Việt">🇻🇳</a>
</p>

busy-tube는 등록한 YouTube 채널의 새 영상을 Markdown 요약으로 정리해 주는 Claude Code 플러그인입니다. 정보는 놓치고 싶지 않지만 영상을 볼 시간이 없는 분들을 위한 도구입니다.

- **영상의 실제 내용까지 파악해서 요약합니다.** Gemini가 음성과 화면 내용을 분석하거나, Whisper로 음성을 받아쓰거나, 자막을 사용합니다. 자막이 없는 영상도 지원합니다.
- **무료로 사용할 수 있습니다.** 유료 API는 쓰지 않습니다. 클라우드 engine은 무료 할당량 안에서 동작하고, 로컬 engine은 키도 필요 없습니다.
- **새 영상만 요약합니다.** 한 번 요약한 영상은 기록해 두었다가 다음부터는 건너뜁니다.
- **읽기 편한 페이지도 만들어 줍니다.** 썸네일, 작동 원리 다이어그램, 해당 장면부터 재생되는 타임스탬프 링크가 들어간 페이지를 게시합니다(Artifact 도구를 사용할 수 있는 경우).
- **요약 언어를 고를 수 있습니다.** 기본값은 일본어이며, `config --lang`으로 변경할 수 있습니다.

## 설치

[uv](https://docs.astral.sh/uv/)와 Claude Code가 필요합니다.

```
/plugin marketplace add OzawaG/busy-tube
/plugin install busy-tube@busy-tube
```

## 사용법

Claude에게 평소 말투로 부탁하면 됩니다. 슬래시 명령 `/busy-tube:busy-tube`로도 호출할 수 있습니다.

- "https://www.youtube.com/@GoogleDevelopers 를 busy-tube에 추가해 줘"
- "YouTube 새 영상 요약해 줘"
- "요약은 영어로 해 줘" "whisper랑 자막만 써 줘"

요약은 채팅에 표시되고, `~/.busy-tube/digests/YYYY-MM-DD.md`에도 저장됩니다.

Claude Code에서 Artifact 도구를 사용할 수 있는 경우(claude.ai와 연동되어 있을 때)에는 요약을 나만 볼 수 있는 웹 페이지로도 게시합니다. 페이지에는 썸네일, 영상의 핵심 원리를 보여 주는 다이어그램, 해당 장면부터 재생되는 타임스탬프 링크가 들어갑니다.

## engine(내용을 가져오는 방법)

설정한 순서대로 시도합니다. 준비되지 않은 engine은 건너뛰고, 무료 할당량 초과 등으로 실패하면 다음 engine으로 넘어갑니다. 기본 순서는 `gemini → groq → mlx-whisper → whisper → captions`입니다.

| engine | 준비 | 강점 | 제약 |
|---|---|---|---|
| `gemini` | `export GEMINI_API_KEY=...`([무료 키](https://aistudio.google.com/apikey)) | 슬라이드, 코드, 화면 속 글자도 인식 | 무료 할당량은 하루 약 20회 요청, 영상은 하루 합계 8시간까지, 공개 영상만 가능, 입력 내용이 Google의 제품 개선에 사용됨 |
| `groq` | `export GROQ_API_KEY=...`([무료 키](https://console.groq.com/keys))와 ffmpeg | Whisper large-v3로 매우 빠름 | 하루 8시간 분량까지 |
| `mlx-whisper` | Apple Silicon Mac과 ffmpeg | 로컬에서 빠르게 동작. 키 불필요 | Mac 전용 |
| `whisper` | 준비 불필요(faster-whisper) | 로컬 실행. 키 불필요. 어떤 OS에서도 동작 | 다소 느림. 처음 실행 시 약 3GB 모델을 다운로드 |
| `captions` | 준비 불필요 | 순식간에 끝남 | 자막이 있는 영상만 |

어떤 engine을 사용할 수 있는지는 `uv run skills/busy-tube/scripts/busy_tube.py doctor`로 확인할 수 있습니다.

BGM만 나오는 영상 등에서는 받아쓰기 결과가 의미 없는 문자열이 될 수 있습니다. 이 경우 자동으로 감지해 다음 engine으로 넘깁니다. 모든 engine에서 실패한 영상은 읽음으로 처리하지 않으므로 다음에 다시 시도합니다.

## 설정

```bash
S=skills/busy-tube/scripts/busy_tube.py
uv run $S config --lang en --max 5 --engines groq,whisper,captions
uv run $S config --gemini-model gemini-3.8-flash --whisper-model large-v3
```

`--max`는 한 번 실행할 때 채널마다 가져오는 새 영상의 최대 개수입니다. 데이터는 `~/.busy-tube/`에 저장됩니다. 저장 위치를 바꾸려면 `BUSY_TUBE_HOME`을 설정하세요.

## 보안

영상의 제목, 설명, 자막은 다른 사람이 작성한 것이므로 AI를 노린 악의적인 지시가 섞여 있을 수 있습니다. busy-tube는 다음 세 가지로 이를 방어합니다.

- 영상 내용은 파일 읽기만 할 수 있는 전용 요약 에이전트만 읽습니다.
- 내용은 '신뢰할 수 없는 콘텐츠'라는 표시로 감싸서 전달합니다.
- 게시하는 페이지에서는 모든 텍스트를 무해화하고 YouTube 이외의 링크를 제거합니다.

API 키는 환경 변수에서만 읽으며, 파일에는 저장하지 않습니다.

## 개발

```bash
python3 skills/busy-tube/scripts/test_busy_tube.py   # 단위 테스트(의존성 없음)
claude --plugin-dir .                                # 로컬에서 실행해 보기
```

## 라이선스

MIT
