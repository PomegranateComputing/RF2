# RF2 PROJECT STATE

## Engine

UZDoom 5.0.1 / Freedoom 0.13.0 dev IWAD.

## Campaign

23 blockouts V1 imported. Production focus: RF01, built from `scripts/mapkit/rf01.py`
(writes `src/maps/RF01.wad`). RF02-RF23 remain V1 blockouts, untouched.

## Gates

- [x] A baseline boots
- [x] B RF01 architecture complete - static checks, autopilot route, every door from both sides
      (`scripts/doortest_rf01.py`)
- [ ] C RF01 combat/art/audio integrated - FAL and 3 enemy families in game; materials, props,
      audio and UI art are stand-ins until the Astra P0 batches; enemy art needs an Astra rework
- [x] D UI/menus/HUD complete - main menu, options (native pages per the UI spec), credits, HUD,
      level title, pause, death screen; captured at 1080p, 1440p and native 4K; a setting survives
      a restart (`scripts/ui_evidence.py --fullscreen 3840x2160`). Native option pages keep the
      engine font and the engine language (`language`, auto = Windows language)
- [x] E save/death/reload/exit end-to-end - runs A and B pass: new game to RF02; save, quit, load,
      death, resume, exit (`scripts/e2e_rf01.py`, ordinary player commands)
- [ ] F two final full runs - human runs by the owner
- [x] G RF01 standard documented - `docs/RF01_STANDARD.md`

## Current playable launcher

`JOUER_RF2_DEV.cmd`

## Notes

End of RF01: in-level ending (fade + exit text), then RF02 (blockout V1).
Method, checks and engine pitfalls: `docs/RF01_STANDARD.md`; encounters: `docs/RF01_ENCOUNTERS.md`;
Astra review: `docs/ASTRA_REVIEW_RF01.md`.
Update this file briefly after each consolidated gate. Do not turn it into a diary.
