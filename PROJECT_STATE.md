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

RF01 produced from `scripts/mapkit/rf01.py`. RF02 produced from `scripts/mapkit/rf02.py`. RF04, RF05 (the Luna Park,
novel l. 451-707) recomposed on 01/10 on one shared park (`scripts/mapkit/luna_park.py`, a declared reconstruction, not
a survey); RF06 (the corridor, l. 709-731) recomposed, without combat; RF07 (Jerma, l. 733-765) produced on 01/10,
without combat (owner's mandate of 01/10). Chain: RF01 -> RF02 -> RF04 -> RF05 -> RF06 -> RF07 -> end screen, a comic
page (Codex) between each two chapters. RF03 (Batignolles) stays a V1 blockout for its later place in the novel
(owner's decision of 27/09); RF08-RF12 are broken down (`docs/production/maps/RF07_RF12_DECOUPAGE.md`); RF08-RF23: V1
blockouts until each is produced. Art: Astra's lots (to 30/09), Codex's lots (from 01/10,
`C:\PROJECTS\RF2_UZDOOM_CODEX_ART_20261001\`). Canon fidelity matrix: `docs/production/CANON_FIDELITE.md`.
Everything newer than the accepted RF01 build waits for the owner's review.

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
- `JOUER_RF2_CUMUL.cmd` - the cumulative candidate (every campaign correction kept); `JOUER_RF2_CUMUL_RF0x.cmd`
  direct review starts (RF02, RF04, RF05, RF06, RF07). Current: `RF2_CUMUL_20261001_1605` (`docs/RF2_CUMUL_20261001_1605.md`);
  the earlier candidates (1502 of 01/10, 1821 of 30/09, ...) stay with their dated launchers.
  Re-pointed only after the new build passes its runs (`export_candidate.py --hold`, then `--promote`)
- `JOUER_RF2_PORTES.cmd` (and `_RF01` ... `_RF08`) - the door pass of 02/10 on every map, for review against the
  cumulative candidate (`docs/RF2_PORTES_20261002.md`); the next cumulative candidate is built on it
- `JOUER_RF2_ARSENAL_ESSAI.cmd` - the weapon test bench, separate from the game
- `JOUER_RF2_BOSS_ESSAI.cmd` - the boss bench (the surveillant-chef, a declared adaptation), separate from the game
- `JOUER_RF2_DEV.cmd` - rebuilds from `src/` and runs (development)

Update this file briefly after each consolidated gate. Do not turn it into a diary.
