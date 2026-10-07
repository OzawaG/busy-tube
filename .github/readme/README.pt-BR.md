<h1 align="center">busy-tube</h1>
<p align="center">
  <strong>Os vídeos do YouTube que você não tem tempo de assistir, em resumos que contam o que realmente importa.</strong>
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
  <strong title="Português (Brasil)" aria-label="Português (Brasil)">🇧🇷</strong> ·
  <a href="README.fr.md" title="Français" aria-label="Français">🇫🇷</a> ·
  <a href="README.de.md" title="Deutsch" aria-label="Deutsch">🇩🇪</a> ·
  <a href="README.vi.md" title="Tiếng Việt" aria-label="Tiếng Việt">🇻🇳</a>
</p>

O busy-tube é um plugin do Claude Code que reúne os vídeos novos dos canais do YouTube que você cadastrou em um resumo em Markdown. É para quem quer se manter informado, mas não tem tempo de assistir aos vídeos.

- **Resume a partir do conteúdo real do vídeo.** O Gemini analisa o áudio e o que aparece na tela, o Whisper transcreve o áudio ou são usadas as legendas. Funciona também com vídeos sem legenda.
- **É gratuito.** Nenhuma API paga é usada. Os engines na nuvem rodam dentro do plano gratuito, e os locais nem precisam de chave.
- **Resume só o que é novo.** Os vídeos já resumidos ficam registrados e são pulados nas próximas execuções.
- **Também gera uma página fácil de ler.** Publica uma página com miniaturas, diagramas que explicam como as coisas funcionam e links com marcação de tempo que tocam o vídeo a partir de cada cena (quando a ferramenta Artifact está disponível).
- **Você escolhe o idioma do resumo.** O padrão é japonês, e dá para mudar com `config --lang`.

## Instalação

É preciso ter o [uv](https://docs.astral.sh/uv/) e o Claude Code.

```
/plugin marketplace add OzawaG/busy-tube
/plugin install busy-tube@busy-tube
```

## Como usar

Basta pedir ao Claude com suas próprias palavras. Também dá para chamar com o comando `/busy-tube:busy-tube`.

- "Adicione https://www.youtube.com/@GoogleDevelopers ao busy-tube"
- "Resuma os vídeos novos do YouTube"
- "Faça os resumos em inglês", "Use só o whisper e as legendas"

O resumo aparece no chat e também é salvo em `~/.busy-tube/digests/YYYY-MM-DD.md`.

Se a ferramenta Artifact estiver disponível no Claude Code (quando ele está conectado ao claude.ai), o resumo também é publicado como uma página web que só você pode ver. A página traz miniaturas, diagramas que explicam os pontos principais de cada vídeo e links com marcação de tempo que tocam o vídeo a partir de cada cena.

## engines (como o conteúdo é obtido)

Os engines são testados na ordem configurada. Os que não estão prontos são pulados e, se um falhar (por exemplo, ao atingir o limite do plano gratuito), passa-se para o próximo. A ordem padrão é `gemini → groq → mlx-whisper → whisper → captions`.

| engine | Preparação | Pontos fortes | Limitações |
|---|---|---|---|
| `gemini` | `export GEMINI_API_KEY=...` ([chave gratuita](https://aistudio.google.com/apikey)) | Capta também o texto de slides, código e da tela | O plano gratuito permite cerca de 20 solicitações por dia e até 8 horas de vídeo no total por dia; só vídeos públicos; as entradas são usadas pelo Google para melhorar seus produtos |
| `groq` | `export GROQ_API_KEY=...` ([chave gratuita](https://console.groq.com/keys)) e ffmpeg | Muito rápido com o Whisper large-v3 | Até 8 horas de áudio por dia |
| `mlx-whisper` | Mac com Apple Silicon e ffmpeg | Rápido e local; sem chave | Só no Mac |
| `whisper` | Nenhuma (faster-whisper) | Local; sem chave; roda em qualquer sistema operacional | Mais lento; na primeira vez baixa um modelo de cerca de 3 GB |
| `captions` | Nenhuma | Instantâneo | Só vídeos com legenda |

Para ver quais engines estão disponíveis, rode `uv run skills/busy-tube/scripts/busy_tube.py doctor`.

Em vídeos que só têm música de fundo, por exemplo, a transcrição pode virar um texto sem sentido. Quando isso acontece, o problema é detectado automaticamente e o vídeo passa para o próximo engine. Vídeos em que todos os engines falham não são marcados como vistos, então são tentados de novo na próxima execução.

## Configuração

```bash
S=skills/busy-tube/scripts/busy_tube.py
uv run $S config --lang en --max 5 --engines groq,whisper,captions
uv run $S config --gemini-model gemini-3.8-flash --whisper-model large-v3
```

`--max` é o número máximo de vídeos novos buscados por canal em cada execução. Os dados ficam salvos em `~/.busy-tube/`. Para mudar o local, defina `BUSY_TUBE_HOME`.

## Segurança

Títulos, descrições e legendas dos vídeos são escritos por outras pessoas, então podem conter instruções maliciosas direcionadas à IA. O busy-tube se protege de três formas:

- Só um agente de resumo dedicado, que consegue apenas ler arquivos, lê o conteúdo dos vídeos.
- Esse conteúdo é entregue envolto em marcações que o identificam como "conteúdo não confiável".
- Na página publicada, todo o texto é neutralizado e os links que não são do YouTube são removidos.

As chaves de API são lidas apenas de variáveis de ambiente e nunca são salvas em arquivos.

## Desenvolvimento

```bash
python3 skills/busy-tube/scripts/test_busy_tube.py   # testes unitários (sem dependências)
claude --plugin-dir .                                # testar o plugin localmente
```

## Licença

MIT
