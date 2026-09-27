# RF2 PROJECT STATE

Active production state (27/09/2026 onward): `docs/production/ETAT_PRODUCTION.md` - owner verdict, accepted
reference, roles, coverage matrix, resume point. This file keeps the gate summary.

## Engine

UZDoom 5.0.1 / Freedoom 0.13.0 dev IWAD.

## Owner verdict (27/09/2026)

RF01 accepted by the owner: map, weapons, Viktor's arm in the black sweatshirt, sounds. Only its enemies get a visual
retouch (RF2-ART-02, Astra), gameplay unchanged. Accepted build: `dist\review\RF2_ART_REVIEW_20260926_1451\`
(`JOUER_RF2_ART_REVIEW.cmd`, tag `rf01-owner-accepted-20260927` = `5b53d9e`), kept intact and read-only.
Production continues on `prod/rf2-campaign`: menus (RF2-UI-01), RF02, then RF03-RF23 in order. Opus integrates,
Astra produces assets in its own worktree. Music later. Sans Destination stopped.

## Campaign

RF01 produced from `scripts/mapkit/rf01.py`. RF02-RF23: V1 blockouts until each is produced as a complete level.

## Gates (RF01)

- [x] A baseline boots
- [x] B RF01 architecture complete (`scripts/doortest_rf01.py`)
- [x] C RF01 combat/art/audio - RF2-ART-01 integrated 26/09, owner accepted 27/09 except the enemy visuals
- [x] D UI/menus/HUD functional (art direction: RF2-UI-01)
- [x] E save/death/reload/exit end-to-end (`scripts/e2e_rf01.py`)
- [x] F owner play - verdict of 27/09
- [x] G RF01 standard documented - `docs/RF01_STANDARD.md`

## Launchers

- `JOUER_RF2_ART_REVIEW.cmd` - accepted RF01 build (reference, never re-pointed)
- `JOUER_RF2_<LOT>.cmd` - each new candidate (`scripts/export_candidate.py`)
- `JOUER_RF2_DEV.cmd` - rebuilds from `src/` and runs (development)

Update this file briefly after each consolidated gate. Do not turn it into a diary.
