# Base actuelle et contrats — d'Opus à Astra, 02/10/2026

Réponse à la commande `RF2_ASTRA_ART_MASSIF_20261002` (pack rédigé sur la base du cumul 1821 du 30/09, sans accès au
dépôt). **La production a avancé depuis** : ce dossier donne l'état réel au 02/10, les fichiers effectivement en jeu et,
lot par lot, de quoi exporter sans deviner. La consigne de préservation du propriétaire s'applique
(`../../PRESERVATION_20261002/PRESERVATION.md`) : partir des meilleures versions en place, reprendre un défaut précis,
comparer avant / après dans le moteur.

## Lire dans cet ordre

| Fichier | Contenu |
|---|---|
| `BASE_ACTUELLE.md` | branche, commit, build, ce qui est déjà fait par rapport au pack, ce qui reste provisoire |
| `SCHEMA_IMPORT.md` | le manifeste que l'importateur lit vraiment ; `outils/verifier_lot.py` pour contrôler un lot avant remise |
| `CONTRAT_ENNEMIS.md` | les trois familles : fichiers, lettres, tics, événements, emprises, ancrages, corps ; ce que le code fait déjà |
| `CONTRAT_VIKTOR.md` | où Viktor apparaît, quels fichiers, à quelle taille ; plus aucun ancien Viktor dans les reflets |
| `CONTRAT_DECORS_ET_PORTES.md` | échelles monde, surfaces provisoires à remplacer, règles des portes et des façades depuis la passe du 02/10 |
| `CONTRAT_TRANSITIONS.md` | le système de planches en place : format, cases, légendes, ratios |
| `PLANS/LISEZ.md` | plan commun RF04/RF05, coupes, dimensions, ce qui est reconstruction ; RF06 |
| `CONTRATS/<LOT>_FICHIERS.csv` | par lot : chaque fichier en jeu, pixels, ancrage `grAb`, taille monde, origine, empreinte |
| `CONTRATS/<LOT>_MANIFESTE_BASE.json` | le même au format de l'importateur, `base_sha256` remplis |
| `ROTATIONS_ETALON_ORDY_A.jpg` | les huit rotations telles qu'elles sont numérotées en jeu |
| `VIKTOR_EN_JEU.png` | le reflet noir, la blouse grise, la chemise au badge et le portrait du HUD, tels qu'ils sont en jeu |
| `REFERENCES/` (dans ton espace seulement) | copies des fichiers eux-mêmes, par lot, pour travailler dessus |

Vues prises dans le moteur à consulter : `C:\PROJECTS\RF2_UZDOOM\dist\candidates\RF2_PORTES_20261002_1018\preuves\` (portes,
façades) et `…\RF2_CUMUL_20261001_1605\preuves\` (RF02 reflet et 48 vues cibles, zone pilote RF04, miroirs aux trois
tenues, RF05, RF06, RF07, marche de l'infirmier, film au son du moteur) ; planches des ennemis :
`docs\production\handoff\RF2_20261001\RETOURS_CODEX\LOTS_20261002\`.

## Correspondance avec les lots du pack

| Lot du pack | État réel au 02/10 | Ce qui est utile maintenant |
|---|---|---|
| P00 pilote | ORDY E de profil : **déjà corrigé** (E V04, en jeu) ; reflet de Viktor : **déjà remplacé** (R2F8 V02 à 56 u) ; cadrage Luna et travée RF05 : surfaces pilotes de Codex en place | juger le raccord E→B en mouvement avant toute reprise ; pilote = un cadrage du parc et une travée de RF05 à ta main, sur les plans de `PLANS/` |
| E01 ORDY | V03 + E V04 en jeu | améliorer dans le contrat, version complète distincte |
| E02 BRCD, E03 PREG | **V02 complètes en jeu** (Codex, 01/10), corps du porte-registre refait | repartir de V02 ; défauts à relever en mouvement |
| V01 Viktor | reflet RF02 et trois tenues RF04/RF05 en jeu, même visage que le HUD | feuille de continuité ; état « matelas dans le reflet » (pas encore de scène : contrat à convenir) |
| A01 plan Luna | **parc commun RF04/RF05 construit** le 01/10, conforme au graphe du pack | élévations, cadrages ; critiquer le plan avant les grandes façades |
| A02 RF05 | voûte, marbre, machines, NODE 0, cadrans V02 en jeu ; roue animée | libellés des cadrans (illisibles) ; courroie, palier, établi, fusible daté : encore provisoires ou absents |
| A03 Luna | pilote 01/02, façades V02, Brooklyn V02, ciel en jeu | trumeaux et fins de façade, attractions, nacelles, gardien, juke-box, flaque |
| A04 RF06 | recomposé le 01/10 (six moments, deux explorations), murs, sols et plafond de Codex | repères, graffitis composés, lit de la chambre 404 |
| F01 figures | civils de RF02 en jeu (lot Astra du 28/09) ; gardien : silhouette provisoire d'Opus | gardien, jeune femme |
| R01, R02 | audit RF02 du 01/10 (objets frustes listés) ; décal d'humidité V05 en jeu | voir `CONTRAT_DECORS_ET_PORTES.md` |
| J01–J03 Jerma | RF07 jouable sans combat sur ressources provisoires d'Opus ; RF08–RF12 découpées, pas construites | tout le décor de RF07 est à produire |
| T01 transitions | **système en place et cinq planches en jeu** (Codex) | reprise par Astra planche par planche si le propriétaire le veut ; contrat exact fourni |
| N01–N07, B01–B02 | rien en campagne ; un banc de boss existe (le surveillant-chef, adaptation déclarée, image provisoire) | planches de conception ; contrat moteur dans `CONTRAT_ENNEMIS.md` § nouvelles familles |

## Remise

`incoming/astra/<LOT>/<VERSION>/` avec `manifest.json` (schéma de `SCHEMA_IMPORT.md`), `runtime/` (exports aux chemins
des destinations), `source/`, `evidence/`, `POUR_OPUS.md`, `SHA256SUMS.txt` en LF. Je n'importe qu'une version figée et
nommée ; je renvoie lot, version, build, ressource, caméra, tic, capture et constat.
