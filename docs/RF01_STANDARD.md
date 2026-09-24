# Standard de production RF01 (méthode réutilisable)

Ce document décrit comment RF01 est construit et vérifié, pour produire RF02–RF23 de la même
façon sans reprendre sa géométrie. Statut des gates : `PROJECT_STATE.md`.

## 1. Source de la carte

- Une carte de production = un script `scripts/mapkit/rfNN.py` qui écrit `src/maps/RFNN.wad`
  (UDMF, espace de noms zdoom). Le WAD produit reste éditable dans Ultimate Doom Builder, mais la
  source canonique est le script : toute modification passe par lui, puis `python scripts/mapkit/rfNN.py`.
- Le blockout V1 (`campaign/blockouts_v1`) sert de graphe narratif : lieux, ordre, ancres. On ne
  reprend ni ses boîtes, ni ses clés, ni sa population. Le générateur V1 n'est jamais exécuté.
- Grille de 16 unités. Une pièce = des `box()` ; **un mur n'existe que là où il n'y a pas de cellule**.
  Deux pièces voisines doivent donc laisser une rangée vide (16 u) entre elles ; les portes et
  fenêtres occupent cette rangée. Deux boîtes collées fusionnent en une limite ouverte.
- Portes : `door()` de 32 u de profondeur (cadre + vantail) ; verrous par `lock`/`lockside`
  (sens unique possible) et messages dans `LOCKDEFS` + `LANGUAGE`.
- Mobilier bloquant : `raise_block()` (tables, lits, étagères) ; props modèles via `MODELDEF`.
- Déclencheurs : `trigger()` ; réveil d'ennemis `wake_line()` (Thing_Activate), objectif
  `objective_line()` (champ UDMF `user_objective`, codes croissants), sauvegarde auto
  `checkpoint()` (spécial 15) à des moments calmes, avant une rencontre ; fin de niveau par une
  ligne `user_outro` (fondu et texte de sortie joués par `RFDirector`/`RFStatusBar`).
- Deux pièges moteur vérifiés en jeu :
  - une ligne n'est signalée activée (objectifs, fin de niveau) que si son spécial réussit :
    les lignes « signal » font un `Thing_Activate` sur `SIGNAL_TID`, porté par un `RFSignal` ;
  - un verrou `LOCKDEFS` sans clé listée accepte n'importe quelle clé : un verrou qui ne doit
    jamais s'ouvrir à l'usage (grille du porche, grille à sens unique) exige `RFNoKey`.
- Acoustique : chaque `Cell` porte un environnement de réverbération (`env`) ; le kit pose les
  `zoneboundary` et un `SoundEnvironment` par zone. Non auditionné par l'agent.
- Usure située : décalques `wear()` (humidité, crasse de main, coulure, éraflure) contre un mur.

## 2. Rencontres

- 5 à 7 rencontres écrites, 3 familles ennemies maximum.
- Un ennemi « en attente » est posé `dormant` avec un tid : il reste animé et vulnérable, aveugle
  et sourd jusqu'à son signal (ligne, ramassage d'objet avec spécial, lecture de note), ou jusqu'au
  premier dégât. Classe de base `RFEnemy` (`src/zscript/rf/enemies.zs`).
- Il ne doit pas être visible avant son signal : sinon il se fait abattre comme une statue.
  On le cache derrière une porte, hors de la ligne de vue, ou on utilise un `RFWaveSpot`
  (l'ennemi apparaît au signal, hors champ) pour les vagues tardives.
- Vérification : `python scripts/mapkit/encounters.py rfNN` (appelé aussi par le script de carte).
  Il signale ennemis visibles trop tôt, acteurs incrustés dans le décor et trous de mur.

## 3. Lumière et matière

- `lightmode = 8` (atténuation logicielle avec la profondeur) dans le bloc `map` du MAPINFO.
- Lumière de secteur = ambiance du lieu ; lampes chaudes et lumière du jour froide en
  `PointLightAttenuated`, avec gains (`LAMP_GAIN`, `DAY_GAIN`) pour ne pas saturer les plâtres clairs.
- Matériaux : famille cohérente générée par `scripts/mapkit/materials.py` en attendant les lots
  Astra ; on remplace par familles entières, jamais texture par texture.
- Polices : `RFText`, `RFTitle`, `RFMenu`, `RFHud` (Inter, OFL) générées par `scripts/mapkit/fonts.py`.
- HUD : mise en page sur un écran virtuel 640×360. L'échelle HUD du moteur est entière et croît
  moins vite que l'écran (3 en 1080p comme en 1440p, 4 en 4K ; `BeginHUD(..., true, ...)` n'y
  change rien) : le HUD applique le reste (`min(L/640, H/360) / GetHUDScale()`), mêmes proportions
  en 1080p, 1440p et 4K ; `rf_hud_scale` (Options) agit par-dessus.
- Options : page RF (`RFOptionsMenu`) = sous-menus natifs dans l'ordre de la spec UI, réglages RF,
  puis « Tous les réglages du moteur ». Les pages natives gardent la police du moteur
  (`NewSmallFont` est construite depuis les ressources du moteur, un mod ne peut pas la remplacer)
  et suivent la langue du moteur (`language`, « auto » = langue de Windows).

## 4. Assets Astra

- Astra livre dans `incoming/astra/<LOT>` ; validation `scripts/validate_astra_batch.py` ;
  inspection réelle (planches, comparaison avec l'existant) ; promotion uniquement par
  `scripts/promote_astra_batch.ps1` (`-Remap`, `-NameFrom` si les noms proposés ne sont pas des
  noms de lumps valides) ; revue consignée dans `docs/ASTRA_REVIEW_*.md`.
- Un asset n'est considéré intégré qu'après observation dans le moteur.

## 5. Vérifications, dans l'ordre

1. `python scripts/mapkit/rfNN.py` — progression statique (clés, sortie), rencontres, murs.
2. `python scripts/check_runtime.py` — LANGUAGE, sprites, sons, textures.
3. `scripts/build.ps1` puis `python scripts/devrun.py --norun` — compilation ZScript/lumps.
4. `python scripts/devrun.py --map RFNN --tour` — captures des points de revue (`RFTourPoint`).
5. `python scripts/devrun.py --map RFNN --autopilot --speed 4` — parcours complet par commandes
   de joueur ordinaires (portes, clés, combats, sortie) le long des `RFDevWaypoint`.
6. `python scripts/doortest_rf01.py` — chaque ligne de porte, depuis sa pièce, sans puis avec clés.
7. `python scripts/e2e_rf01.py` (à dupliquer par carte) — parcours A et B du gate E.
8. `python scripts/ui_evidence.py --fullscreen 3840x2160` — menu principal, options, crédits, HUD,
   titre du niveau et pause en 1080p/1440p (fenêtre) et 4K (plein écran), persistance d'un réglage.
9. `python scripts/devrun.py --map RFNN --name weapons +rf_dev_weapons 1` — tir et recharge en jeu.
10. Parcours humain : reste indispensable pour la durée de découverte, la lisibilité, le ressenti.

Pièges vérifiés des outils de test :
- `-loadgame` est résolu dans `-savedir` : on passe le nom du fichier, pas son chemin ;
- les CVars `server` sont enregistrées dans les sauvegardes et restaurées au chargement : les
  réglages de test (`rf_dev_*`) sont `nosave`, sinon une sauvegarde de test ramène l'autopilote ;
- en fenêtre, `-width`/`-height` n'ont pas d'effet : la taille vient de `vid_setsize` ;
- `wait` dans les commandes de la ligne de commande s'écoule pendant le démarrage : les captures
  minutées passent par le gestionnaire de dev (`rf_dev_ui`, horloge du niveau puis horloge UI,
  le menu mettant le jeu en pause) ;
- un lump `DEFCVARS` n'est pas lu depuis un pk3 chargé par `-file` (« Cannot load DEFCVARS from a
  wadfile ») : les valeurs par défaut passent par CVARINFO ou par le lanceur ;
- sur le bureau invisible (`RF_DEV_HIDDEN=1`), une erreur fatale ouvre une fenêtre que personne ne
  voit : `devrun.py` la détecte, l'enregistre en PNG à côté du log et arrête le moteur.

Aucune preuve de progression ne repose sur noclip, god, warp ou give. Le tour de captures,
le test des portes et la capture d'arme téléportent le joueur ou donnent des objets : ils
vérifient des éléments isolés, jamais le chemin normal (prouvé par l'autopilote et les parcours A/B).
