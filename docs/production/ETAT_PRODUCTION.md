# RF2 — état de production actif

Document d'état de la production de campagne ouverte le 27 septembre 2026. Il remplace les priorités des mandats du
23, 25 et 26 septembre lorsqu'elles demandaient de refaire un élément désormais accepté. Mis à jour à chaque jalon ;
ce n'est pas un journal.

## 1. Verdict du propriétaire (27 septembre 2026)

Retour explicite du propriétaire, transmis par le pack `RF2_PRODUCTION_20260927` :

- **RF01 accepté** : carte, parcours et rencontres ; armes ; bras de Viktor en sweat noir ; sons améliorés.
- **Seule retouche demandée sur RF01 : les visuels des ennemis** (plus sombres, plus beaux, plus aboutis), sans
  changer leur gameplay.
- Nouveau travail autorisé : menus artistiques (RF2-UI-01), puis RF02–RF23 au standard RF01, un peu plus sombres,
  sales et étranges dans la suite, sans noircir RF01.
- Même bras et même manche de sweat noir pour tout l'arsenal. Musique : plus tard (aucune musique nouvelle).
- Sans Destination : arrêté. Fable : relais ponctuel seulement.

Portée de cette acceptation : c'est le jugement du propriétaire sur le build joué. Elle ne prouve ni une audition
exhaustive de chaque ressource ni une revue indépendante par l'agent. Le rapport `docs/RF2_ART_01_REVUE.md` (« aucune
écoute ») est antérieur à ce retour. Les nouvelles candidates (ennemis retouchés, menus, RF02…) **ne sont pas
approuvées** tant que le propriétaire ne l'a pas dit.

## 2. Référence acceptée (ne pas modifier)

| Élément | Valeur |
|---|---|
| Tag | `rf01-owner-accepted-20260927` → `5b53d9eaaaf088f49ae98f667fc1d575779dc74e` (branche `art/rf2-art-01-integration`) |
| Build | `dist\review\RF2_ART_REVIEW_20260926_1451\RF2_ART_REVIEW.pk3`, SHA-256 `04bdd0ae918761370c7620318f6e2add8bd1e1ac0acf88d55741c8be1883544f` |
| Construit depuis | `e1d007c` ; `5b53d9e` ne diffère que par `docs/RF2_ART_01_REVUE.md`. Contenu du pk3 = `src/` à `5b53d9e`, 1 146 fichiers, 0 écart (vérifié le 27/09) : aucune dépendance non suivie |
| Lanceur | `JOUER_RF2_ART_REVIEW.cmd` → `dist\review\LATEST.txt` → ce build ; config `user\uzdoom_art_review.ini`, sauvegardes `user\savegames_art_review` |
| Protection | pk3, `BUILD_INFO.json` et `LATEST.txt` en lecture seule ; `scripts/export_review.py` refuse désormais de réécrire `LATEST.txt` |
| Moteur | UZDoom 5.0.1 `uzdoom.exe` SHA-256 `1c76e2d1…1f49`, `uzdoom.pk3` `f1a1d319…eb82a`, OpenAL `soft_oal.dll` `4e2d830d…e0e8` |
| IWAD | Freedoom 0.13.0 `freedoom2.wad` SHA-256 `a8772e08…cd4b` |
| Renderer / config | configuration de revue copiée de `user\uzdoom.ini` ; aucun autoload (sections vides, pas d'`autoexec.cfg`) |

`main` reste à `6e1a31b` (base ancienne, non déplacée). La production part de la branche `prod/rf2-campaign`, issue du
tag. Chaque candidate reçoit son build et son lanceur (`scripts/export_candidate.py`, `JOUER_RF2_<LOT>.cmd`).

## 3. Rôles

| Zone | Écrivain |
|---|---|
| Maps, acteurs, scripts, audio en jeu, UI runtime, builds, rapports | Opus 5.5 (unique intégrateur de `C:\PROJECTS\RF2_UZDOOM`) |
| Sources et exports artistiques des lots attribués | Astra, dans son worktree `C:\PROJECTS\RF2_UZDOOM_ASTRA_20260927` (branche `art/rf2-art-02-astra`, base `5b53d9e`) |
| Acceptation artistique | Propriétaire |
| Fable | Tâche bornée attribuée explicitement, puis relais |

Contrats de transmission : `docs/production/handoff/`.

## 4. Ordres historiques (ne plus exécuter)

Clos par le verdict du 27/09 : refaire le pistolet, le son ou le parcours RF01 (mandats du 25 et du 26), relancer les
prompts du pack `RF2_ART_PASS_20260925`, reprendre les priorités Fable/RF01 du 23/09. Les deux captures du 25/09 sont
des preuves d'un ancien défaut, pas une cible. Les rapports et preuves RF01 existants restent valables pour ce qu'ils
mesurent.

## 5. Lots

| Lot | Contenu | Statut |
|---|---|---|
| Socle | Référence figée, branche de production, contrats, renvois réparés | fait (27/09) |
| RF2-ART-02 | Ennemis RF01, visuel seulement (Astra) | IN_PRODUCTION chez Astra |
| RF2-UI-01 | Menus artistiques et parcours fonctionnel | voir §6 |
| RF2-MAP-02 | RF02 complet | voir §6 |
| Campagne | RF03–RF23 dans l'ordre | après RF02 |

## 6. Matrice de couverture réelle

Statuts : `INVENTORIED`, `IN_PRODUCTION`, `INTEGRATED`, `RUNTIME_VERIFIED_OWNER_REVIEW_REQUIRED`, `OWNER_ACCEPTED`.
Un statut vaut pour un périmètre et une version.

### Cartes

| Carte | Titre (repère V1) | État | Preuve / build | Verdict |
|---|---|---|---|---|
| RF01 | Sainte-Anne - Les portes ouvertes | OWNER_ACCEPTED (carte, armes, bras, sons) ; ennemis : retouche en cours | build 20260926_1451 | accepté 27/09 hors ennemis |
| RF02 | Paris - Rue de service | INVENTORIED (blockout V1) | — | — |
| RF03–RF23 | voir `agent/specs/MAPS_V1_INVENTORY.md` | INVENTORIED (blockouts V1, ennemis Freedoom) | — | — |

### Arsenal (liste du dossier maître, `legacy/import/RF2_DOSSIER_MAITRE.md` §10)

| Arme | État |
|---|---|
| Browning Hi-Power | OWNER_ACCEPTED (RF01) — master du bras et de la manche |
| FN FAL | OWNER_ACCEPTED (RF01) |
| Fusil à pompe type riot | INVENTORIED (première tranche historique, modèle exact ouvert) |
| FAMAS | INVENTORIED |
| Scie Black & Decker Skorpion, Browning M2 .50, pistolet taser | INVENTORIED (seconde vague) |
| Lance-flammes | INVENTORIED, demande à reconfirmer |

### Ennemis

| Famille | Utilisée par | État |
|---|---|---|
| Infirmier `RFOrderly` (ORDY) | RF01 | gameplay accepté ; visuel : RF2-ART-02 en cours |
| Brancardier `RFBrancardier` (BRCD) | RF01 | idem |
| Porte-Registre `RFPorteRegistre` (PREG, liasse PRGS) | RF01 | idem |
| Rifleman, Shotgunner, Custodian (roster du dossier maître §14) | — | INVENTORIED |
| Monstres Freedoom des blockouts RF02–RF22 | blockouts | provisoires, à remplacer carte par carte |

### Audio

| Élément | État |
|---|---|
| Sons RF01 (66 fichiers, mix) | OWNER_ACCEPTED — référence sonore |
| Lit `RFAMB01` (déclaré comme musique dans MAPINFO, joué en fond d'ambiance) | existant, inventorié ; traitement musical différé |
| `$MUSIC_RUNNIN` (Freedoom) en `defaultmap` pour RF02–RF22, `$MUSIC_READ_M` à la fin | existant, inventorié ; non supprimé, traitement différé |

### UI

| Écran | État |
|---|---|
| Menu principal, pause, options RF, crédits, HUD, titre de niveau, fin de niveau | fonctionnels (gate D) ; direction artistique : RF2-UI-01 |

## 7. Reprise

Voir la dernière section « Reprise » de ce fichier après chaque jalon : commit, lot en cours, dépendance, prochaine
action.

- 27/09 — socle posé sur `prod/rf2-campaign`. Prochaine action : RF2-UI-01 (structure) et RF2-MAP-02 (fiche, carte).
