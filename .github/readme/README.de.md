<h1 align="center">busy-tube</h1>
<p align="center">
  <strong>YouTube-Videos, für die dir die Zeit fehlt – als Zusammenfassungen, die wirklich auf den Inhalt eingehen.</strong>
</p>
<p align="center">
  <a href="../../LICENSE"><img src="https://img.shields.io/github/license/OzawaG/busy-tube?style=flat" alt="License"></a>
</p>

<p align="center">
  <a href="../../README.md" title="日本語" aria-label="日本語">🇯🇵</a> ·
  <a href="README.en.md" title="English" aria-label="English">🇬🇧</a> ·
  <a href="README.zh-CN.md" title="简体中文" aria-label="简体中文">🇨🇳</a> ·
  <a href="README.ko.md" title="한국어" aria-label="한국어">🇰🇷</a> ·
  <a href="README.es.md" title="Español" aria-label="Español">🇪🇸</a> ·
  <a href="README.pt-BR.md" title="Português (Brasil)" aria-label="Português (Brasil)">🇧🇷</a> ·
  <a href="README.fr.md" title="Français" aria-label="Français">🇫🇷</a> ·
  <strong title="Deutsch" aria-label="Deutsch">🇩🇪</strong> ·
  <a href="README.vi.md" title="Tiếng Việt" aria-label="Tiếng Việt">🇻🇳</a>
</p>

busy-tube ist ein Claude-Code-Plugin, das neue Videos deiner abonnierten YouTube-Kanäle in einer Markdown-Zusammenfassung bündelt. Es richtet sich an alle, die auf dem Laufenden bleiben wollen, aber keine Zeit haben, sich die Videos anzusehen.

- **Es fasst den tatsächlichen Inhalt der Videos zusammen.** Gemini analysiert Ton und Bild, Whisper transkribiert das Audio, oder es werden die Untertitel verwendet. Auch Videos ohne Untertitel werden unterstützt.
- **Es ist kostenlos.** Kostenpflichtige APIs kommen nicht zum Einsatz. Die Cloud-engines laufen im Rahmen ihres Gratiskontingents, die lokalen engines brauchen nicht einmal einen Schlüssel.
- **Es fasst nur Neues zusammen.** Bereits zusammengefasste Videos werden vermerkt und bei späteren Durchläufen übersprungen.
- **Es erstellt auch eine gut lesbare Seite.** Es veröffentlicht eine Seite mit Vorschaubildern, Diagrammen, die die Funktionsweise erklären, und Zeitstempel-Links, die das Video direkt an der jeweiligen Stelle abspielen (sofern das Artifact-Tool verfügbar ist).
- **Die Sprache der Zusammenfassung ist frei wählbar.** Standard ist Japanisch; ändern lässt sie sich mit `config --lang`.

## Installation

Du brauchst [uv](https://docs.astral.sh/uv/) und Claude Code.

```
/plugin marketplace add OzawaG/busy-tube
/plugin install busy-tube@busy-tube
```

## Verwendung

Bitte Claude einfach in deinen eigenen Worten darum. Alternativ kannst du den Slash-Befehl `/busy-tube:busy-tube` verwenden.

- „Füge https://www.youtube.com/@GoogleDevelopers zu busy-tube hinzu“
- „Fasse die neuen YouTube-Videos zusammen“
- „Schreib die Zusammenfassungen auf Englisch“, „Nutze nur whisper und Untertitel“

Die Zusammenfassung erscheint im Chat und wird außerdem unter `~/.busy-tube/digests/YYYY-MM-DD.md` gespeichert.

Ist in Claude Code das Artifact-Tool verfügbar (wenn es mit claude.ai verbunden ist), wird die Zusammenfassung zusätzlich als Webseite veröffentlicht, die nur du sehen kannst. Die Seite enthält Vorschaubilder, Diagramme, die die Kernpunkte jedes Videos erklären, und Zeitstempel-Links, die das Video direkt an der jeweiligen Stelle abspielen.

## engines (wie der Inhalt gewonnen wird)

Die engines werden in der konfigurierten Reihenfolge ausprobiert. Nicht eingerichtete engines werden übersprungen, und schlägt eine fehl (etwa weil das Gratiskontingent erschöpft ist), kommt die nächste an die Reihe. Die Standardreihenfolge ist `gemini → groq → mlx-whisper → whisper → captions`.

| engine | Voraussetzungen | Stärken | Einschränkungen |
|---|---|---|---|
| `gemini` | `export GEMINI_API_KEY=...` ([kostenloser Schlüssel](https://aistudio.google.com/apikey)) | Erfasst auch Text auf Folien, im Code und auf dem Bildschirm | Gratiskontingent etwa 20 Anfragen pro Tag und insgesamt bis zu 8 Stunden Video pro Tag; nur öffentliche Videos; Eingaben werden von Google zur Produktverbesserung genutzt |
| `groq` | `export GROQ_API_KEY=...` ([kostenloser Schlüssel](https://console.groq.com/keys)) und ffmpeg | Sehr schnell mit Whisper large-v3 | Bis zu 8 Stunden Audio pro Tag |
| `mlx-whisper` | Mac mit Apple Silicon und ffmpeg | Schnell und lokal; kein Schlüssel nötig | Nur Mac |
| `whisper` | Keine (faster-whisper) | Lokal; kein Schlüssel nötig; läuft auf jedem Betriebssystem | Langsamer; lädt beim ersten Mal ein Modell von etwa 3 GB herunter |
| `captions` | Keine | Sofort fertig | Nur Videos mit Untertiteln |

Welche engines verfügbar sind, zeigt `uv run skills/busy-tube/scripts/busy_tube.py doctor`.

Bei Videos, die etwa nur aus Hintergrundmusik bestehen, kann die Transkription sinnlosen Text ergeben. Das wird automatisch erkannt, und das Video geht an die nächste engine. Videos, bei denen alle engines scheitern, werden nicht als gesehen markiert und beim nächsten Durchlauf erneut versucht.

## Konfiguration

```bash
S=skills/busy-tube/scripts/busy_tube.py
uv run $S config --lang en --max 5 --engines groq,whisper,captions
uv run $S config --gemini-model gemini-3.8-flash --whisper-model large-v3
```

`--max` legt fest, wie viele neue Videos pro Kanal und Durchlauf höchstens abgerufen werden. Die Daten werden in `~/.busy-tube/` gespeichert. Um den Speicherort zu ändern, setze `BUSY_TUBE_HOME`.

## Sicherheit

Titel, Beschreibungen und Untertitel von Videos stammen von Dritten und können daher bösartige Anweisungen an die KI enthalten. busy-tube schützt sich auf drei Arten davor:

- Den Inhalt der Videos liest ausschließlich ein eigener Zusammenfassungs-Agent, der nichts anderes kann, als Dateien zu lesen.
- Der Inhalt wird ihm in Markierungen eingeschlossen übergeben, die ihn als „nicht vertrauenswürdigen Inhalt“ kennzeichnen.
- Auf der veröffentlichten Seite wird sämtlicher Text entschärft, und Links, die nicht zu YouTube führen, werden entfernt.

API-Schlüssel werden ausschließlich aus Umgebungsvariablen gelesen und nie in Dateien gespeichert.

## Entwicklung

```bash
python3 skills/busy-tube/scripts/test_busy_tube.py   # Unit-Tests (ohne Abhängigkeiten)
claude --plugin-dir .                                # Plugin lokal ausprobieren
```

## Lizenz

MIT
