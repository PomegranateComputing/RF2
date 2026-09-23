# RF2_UZDOOM

Projet vivant du FPS Red Flags 2 sous UZDoom.

- Runtime source : `src/`
- Maps de production : `src/maps/RF01.wad` ... `RF23.wad`
- Blockouts V1 intangibles : `campaign/blockouts_v1/`
- Legacy récupéré : `legacy/import/`
- Assets Codex Astra : `incoming/astra/` (staging uniquement)
- Prompts : `agent/`
- Build dev : `dist/RF2_DEV.pk3`
- Launcher : `JOUER_RF2_DEV.cmd`

Règle absolue : le runtime ne dépend jamais directement de `legacy`, `campaign` ou `incoming`.
