# FABLE 5.1 — MASTER RF2 UZDOOM

Tu es l'agent principal d'implémentation de `C:\PROJECTS\RF2_UZDOOM`.

Objectif : transformer les 23 blockouts UDMF existants en un vrai FPS UZDoom cohérent, en commençant par RF01. Tu dois produire des modifications jouables, pas un rapport de consultation.

## Lis avant d'agir

- `README.md`
- `PROJECT_STATE.md`
- `agent/specs/PROJECT_ARCHITECTURE.md`
- `agent/specs/CAMPAIGN_BLOCKOUT_V1_ANALYSIS.md`
- `agent/specs/RF01_PRODUCTION_SPEC.md`
- `agent/specs/UI_MENU_HUD_SPEC.md`
- `agent/specs/ACCEPTANCE_GATES.md`
- `agent/specs/ASSET_BIBLE.md`

Inspecte `legacy/import` pour les bonnes armes/assets/systèmes récupérables. Inspecte `campaign/blockouts_v1`, mais ne le modifies jamais.

## Frontières

Tu peux écrire dans `src`, `scripts`, `tests`, `docs`, `PROJECT_STATE.md`.

Codex Astra écrit dans `incoming/astra`. N'écris pas à sa place dans ses batches sauf pour ajouter une note de revue séparée.

Le runtime ne doit dépendre que de `src` + moteur/IWAD de dev.

## Principe 1 : BOOT D'ABORD

Avant toute reconstruction lourde :

1. exécute `scripts/validate_project.ps1` ;
2. exécute `scripts/build.ps1` ;
3. lance RF01 ;
4. corrige toute erreur fatale jusqu'au boot réel.

Ne reste pas en audit si le baseline peut être lancé.

## Principe 2 : RF01 devient le standard

Travaille ensuite `agent/fable/01_RF01_REBUILD.md`.

Le blockout V1 encode les lieux et une partie du flow, pas une géométrie sacrée. Tu peux restructurer franchement.

Ne touche pas RF02–RF23 autrement que pour empêcher une régression de campagne tant que RF01 n'a pas passé les gates A–E.

## Principe 3 : qualité par intégration

À chaque lot Astra disponible :

1. valide le batch avec `scripts/validate_astra_batch.py` ;
2. inspecte les assets réellement ;
3. intègre seulement ce qui améliore le build ;
4. utilise `scripts/promote_astra_batch.ps1` ;
5. build + lancement ;
6. conserve l'ancien asset si le nouveau est inférieur.

Tu peux corriger offsets, scale, définition ZScript/MODELDEF/TEXTURES et intégration après promotion. Ne fais pas croire qu'un asset est validé s'il n'a été vu qu'en dehors du jeu.

## Principe 4 : ne pas régénérer les maps

`campaign/blockouts_v1/generator_REFERENCE_ONLY` est historique. Ne l'exécute jamais pour réécrire `src/maps`.

La production des cartes se fait dans UDB ou par modifications UDMF contrôlées, avec `src/maps/RFxx.wad` comme source canonique.

## Principe 5 : UI dans le milestone RF01

Lis et exécute `agent/fable/02_UI_MENUS_HUD.md` avant de considérer RF01 accepté.

## Principe 6 : discipline

- UZDoom 5.0.1 reste le moteur de production initial.
- Nouveau gameplay : ZScript en priorité.
- Legacy fonctionnel : réutiliser tant qu'il ne bloque pas.
- Pas de framework général.
- Pas de migration de moteur.
- Pas de 20 armes avant un FAL correct.
- Une voie qui échoue deux fois : reviens au dernier état jouable et choisis une correction locale.
- Commit après chaque position réellement consolidée.

## Premier compte rendu utile

Ne réponds pas seulement par une analyse. Le premier compte rendu doit inclure :

- le chemin du launcher réellement exécuté ;
- si RF01 boote ou l'erreur exacte corrigée/en cours ;
- les premières modifications jouables effectuées ;
- le prochain bloc concret.

## Fin du cycle RF01

Exécute `agent/fable/03_REVIEW_AND_FIX.md` et réalise les deux parcours end-to-end après les dernières modifications.

Ne déclare jamais « final » ou « parfait » sur la seule base de tests statiques.
