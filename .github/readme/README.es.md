<h1 align="center">busy-tube</h1>
<p align="center">
  <strong>Los vídeos de YouTube que no tienes tiempo de ver, convertidos en resúmenes que de verdad cuentan su contenido.</strong>
</p>
<p align="center">
  <a href="../../LICENSE"><img src="https://img.shields.io/github/license/OzawaG/busy-tube?style=flat" alt="License"></a>
</p>

<p align="center">
  <a href="../../README.md" title="日本語" aria-label="日本語">🇯🇵</a> ·
  <a href="README.en.md" title="English" aria-label="English">🇬🇧</a> ·
  <a href="README.zh-CN.md" title="简体中文" aria-label="简体中文">🇨🇳</a> ·
  <a href="README.ko.md" title="한국어" aria-label="한국어">🇰🇷</a> ·
  <strong title="Español" aria-label="Español">🇪🇸</strong> ·
  <a href="README.pt-BR.md" title="Português (Brasil)" aria-label="Português (Brasil)">🇧🇷</a> ·
  <a href="README.fr.md" title="Français" aria-label="Français">🇫🇷</a> ·
  <a href="README.de.md" title="Deutsch" aria-label="Deutsch">🇩🇪</a> ·
  <a href="README.vi.md" title="Tiếng Việt" aria-label="Tiếng Việt">🇻🇳</a>
</p>

busy-tube es un plugin de Claude Code que reúne los vídeos nuevos de los canales de YouTube que sigues en un resumen en Markdown. Está pensado para quienes quieren mantenerse informados pero no tienen tiempo de ver los vídeos.

- **Resume a partir del contenido real del vídeo.** Gemini analiza el audio y lo que aparece en pantalla, Whisper transcribe el audio o se usan los subtítulos. También funciona con vídeos sin subtítulos.
- **Es gratuito.** No usa ninguna API de pago. Los engines en la nube funcionan dentro de su nivel gratuito y los locales ni siquiera necesitan clave.
- **Solo resume lo nuevo.** Registra los vídeos ya resumidos y los omite en las siguientes ejecuciones.
- **También genera una página fácil de leer.** Publica una página con miniaturas, diagramas que explican el funcionamiento y enlaces con marca de tiempo para reproducir cada escena (si la herramienta Artifact está disponible).
- **Puedes elegir el idioma del resumen.** Por defecto es japonés y se cambia con `config --lang`.

## Instalación

Necesitas [uv](https://docs.astral.sh/uv/) y Claude Code.

```
/plugin marketplace add OzawaG/busy-tube
/plugin install busy-tube@busy-tube
```

## Uso

Pídeselo a Claude con tus propias palabras. También puedes invocarlo con el comando `/busy-tube:busy-tube`.

- «Añade https://www.youtube.com/@GoogleDevelopers a busy-tube»
- «Resume los vídeos nuevos de YouTube»
- «Haz los resúmenes en inglés», «Usa solo whisper y los subtítulos»

El resumen aparece en el chat y también se guarda en `~/.busy-tube/digests/YYYY-MM-DD.md`.

Si la herramienta Artifact está disponible en Claude Code (cuando está conectado a claude.ai), el resumen también se publica como una página web que solo tú puedes ver. La página incluye miniaturas, diagramas del funcionamiento que explican las ideas clave de cada vídeo y enlaces con marca de tiempo para reproducir cada escena.

## engines (cómo se obtiene el contenido)

Se prueban en el orden configurado. Los engines que no están preparados se omiten y, si uno falla (por ejemplo, al alcanzar el límite del nivel gratuito), se pasa al siguiente. El orden por defecto es `gemini → groq → mlx-whisper → whisper → captions`.

| engine | Requisitos | Puntos fuertes | Limitaciones |
|---|---|---|---|
| `gemini` | `export GEMINI_API_KEY=...` ([clave gratuita](https://aistudio.google.com/apikey)) | Capta también el texto de diapositivas, código y pantalla | El nivel gratuito permite unas 20 solicitudes al día y hasta 8 horas de vídeo en total al día; solo vídeos públicos; Google usa las entradas para mejorar sus productos |
| `groq` | `export GROQ_API_KEY=...` ([clave gratuita](https://console.groq.com/keys)) y ffmpeg | Muy rápido con Whisper large-v3 | Hasta 8 horas de audio al día |
| `mlx-whisper` | Mac con Apple Silicon y ffmpeg | Rápido y en local; sin clave | Solo Mac |
| `whisper` | Nada (faster-whisper) | En local; sin clave; funciona en cualquier sistema operativo | Más lento; la primera vez descarga un modelo de unos 3 GB |
| `captions` | Nada | Instantáneo | Solo vídeos con subtítulos |

Para ver qué engines están disponibles, ejecuta `uv run skills/busy-tube/scripts/busy_tube.py doctor`.

En vídeos que solo tienen música de fondo, por ejemplo, la transcripción puede acabar siendo texto sin sentido. Cuando ocurre, se detecta automáticamente y se pasa al siguiente engine. Los vídeos en los que fallan todos los engines no se marcan como vistos, así que se vuelven a intentar en la siguiente ejecución.

## Configuración

```bash
S=skills/busy-tube/scripts/busy_tube.py
uv run $S config --lang en --max 5 --engines groq,whisper,captions
uv run $S config --gemini-model gemini-3.8-flash --whisper-model large-v3
```

`--max` es el número máximo de vídeos nuevos que se obtienen por canal en cada ejecución. Los datos se guardan en `~/.busy-tube/`. Para cambiar la ubicación, define `BUSY_TUBE_HOME`.

## Seguridad

Los títulos, descripciones y subtítulos de los vídeos los escriben otras personas, así que pueden contener instrucciones maliciosas dirigidas a la IA. busy-tube se protege de tres formas:

- Solo un agente de resumen dedicado, que únicamente puede leer archivos, lee el contenido de los vídeos.
- Ese contenido se le pasa envuelto en marcas que lo señalan como «contenido no fiable».
- En la página publicada, todo el texto se neutraliza y se eliminan los enlaces que no son de YouTube.

Las claves de API se leen únicamente de variables de entorno y nunca se guardan en archivos.

## Desarrollo

```bash
python3 skills/busy-tube/scripts/test_busy_tube.py   # pruebas unitarias (sin dependencias)
claude --plugin-dir .                                # probar el plugin en local
```

## Licencia

MIT
