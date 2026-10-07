<h1 align="center">busy-tube</h1>
<p align="center">
  <strong>Les vidéos YouTube que vous n'avez pas le temps de regarder, en résumés qui vont au fond des choses.</strong>
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
  <strong title="Français" aria-label="Français">🇫🇷</strong> ·
  <a href="README.de.md" title="Deutsch" aria-label="Deutsch">🇩🇪</a> ·
  <a href="README.vi.md" title="Tiếng Việt" aria-label="Tiếng Việt">🇻🇳</a>
</p>

busy-tube est un plugin Claude Code qui rassemble les nouvelles vidéos des chaînes YouTube que vous suivez dans un résumé au format Markdown. Il s'adresse à celles et ceux qui veulent rester informés sans avoir le temps de regarder les vidéos.

- **Il résume à partir du contenu réel de la vidéo.** Gemini analyse le son et ce qui s'affiche à l'écran, Whisper transcrit l'audio, ou bien les sous-titres sont utilisés. Les vidéos sans sous-titres sont aussi prises en charge.
- **Il est gratuit.** Aucune API payante n'est utilisée. Les engines cloud tournent dans les limites de leur offre gratuite, et les engines locaux ne demandent même pas de clé.
- **Il ne résume que les nouveautés.** Les vidéos déjà résumées sont enregistrées et ignorées lors des exécutions suivantes.
- **Il produit aussi une page agréable à lire.** Il publie une page avec les miniatures, des schémas qui expliquent le fonctionnement et des liens horodatés pour lancer la lecture à chaque passage (si l'outil Artifact est disponible).
- **Vous choisissez la langue du résumé.** Le japonais est la langue par défaut ; vous pouvez la changer avec `config --lang`.

## Installation

Vous avez besoin de [uv](https://docs.astral.sh/uv/) et de Claude Code.

```
/plugin marketplace add OzawaG/busy-tube
/plugin install busy-tube@busy-tube
```

## Utilisation

Demandez simplement à Claude, avec vos propres mots. Vous pouvez aussi l'appeler avec la commande `/busy-tube:busy-tube`.

- « Ajoute https://www.youtube.com/@GoogleDevelopers à busy-tube »
- « Résume les nouvelles vidéos YouTube »
- « Fais les résumés en anglais », « N'utilise que whisper et les sous-titres »

Le résumé s'affiche dans la conversation et est également enregistré dans `~/.busy-tube/digests/YYYY-MM-DD.md`.

Si l'outil Artifact est disponible dans Claude Code (lorsqu'il est connecté à claude.ai), le résumé est aussi publié sous forme de page web visible par vous seul. La page contient les miniatures, des schémas qui expliquent les points clés de chaque vidéo et des liens horodatés pour lancer la lecture à chaque passage.

## engines (comment le contenu est récupéré)

Les engines sont essayés dans l'ordre configuré. Ceux qui ne sont pas prêts sont ignorés et, si l'un d'eux échoue (par exemple parce que la limite de l'offre gratuite est atteinte), on passe au suivant. L'ordre par défaut est `gemini → groq → mlx-whisper → whisper → captions`.

| engine | Prérequis | Points forts | Limites |
|---|---|---|---|
| `gemini` | `export GEMINI_API_KEY=...` ([clé gratuite](https://aistudio.google.com/apikey)) | Capte aussi le texte des slides, du code et de l'écran | L'offre gratuite autorise environ 20 requêtes par jour et 8 heures de vidéo au total par jour ; vidéos publiques uniquement ; les entrées servent à Google pour améliorer ses produits |
| `groq` | `export GROQ_API_KEY=...` ([clé gratuite](https://console.groq.com/keys)) et ffmpeg | Très rapide avec Whisper large-v3 | Jusqu'à 8 heures d'audio par jour |
| `mlx-whisper` | Mac Apple Silicon et ffmpeg | Rapide et local ; pas de clé | Mac uniquement |
| `whisper` | Aucun (faster-whisper) | Local ; pas de clé ; fonctionne sur tous les systèmes | Plus lent ; télécharge un modèle d'environ 3 Go la première fois |
| `captions` | Aucun | Instantané | Vidéos sous-titrées uniquement |

Pour savoir quels engines sont disponibles, lancez `uv run skills/busy-tube/scripts/busy_tube.py doctor`.

Pour une vidéo qui ne contient que de la musique de fond, par exemple, la transcription peut produire un texte dénué de sens. Ce cas est détecté automatiquement et la vidéo passe à l'engine suivant. Les vidéos pour lesquelles tous les engines échouent ne sont pas marquées comme vues : elles seront retentées à la prochaine exécution.

## Configuration

```bash
S=skills/busy-tube/scripts/busy_tube.py
uv run $S config --lang en --max 5 --engines groq,whisper,captions
uv run $S config --gemini-model gemini-3.8-flash --whisper-model large-v3
```

`--max` fixe le nombre maximal de nouvelles vidéos récupérées par chaîne à chaque exécution. Les données sont stockées dans `~/.busy-tube/`. Pour changer d'emplacement, définissez `BUSY_TUBE_HOME`.

## Sécurité

Les titres, descriptions et sous-titres des vidéos sont rédigés par des tiers ; ils peuvent donc contenir des instructions malveillantes destinées à l'IA. busy-tube s'en protège de trois façons :

- Seul un agent de résumé dédié, qui ne peut que lire des fichiers, lit le contenu des vidéos.
- Ce contenu lui est transmis encadré par des balises qui le signalent comme « contenu non fiable ».
- Sur la page publiée, tout le texte est neutralisé et les liens qui ne pointent pas vers YouTube sont supprimés.

Les clés d'API sont lues uniquement depuis les variables d'environnement et ne sont jamais enregistrées dans des fichiers.

## Développement

```bash
python3 skills/busy-tube/scripts/test_busy_tube.py   # tests unitaires (sans dépendances)
claude --plugin-dir .                                # essayer le plugin en local
```

## Licence

MIT
