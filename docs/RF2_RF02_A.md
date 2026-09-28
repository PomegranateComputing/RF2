# RF02-A — tranche de rue de référence (en cours)

**Statut : IN_PRODUCTION.** Mandat du 27/09 soir, lot RF02-A (« une portion de rue finalisée avec façade, sol, objet
proche et lumière, servant de référence pour toute la carte »). Rien ici ne vaut accord du propriétaire.

## 1. Ancrage des enseignes (erreur commune testée, puis corrigée)

Le mandat demande d'auditer les ancrages du générateur, « particulièrement les plaques de rue, tableau d'horaires »,
et de tester l'erreur commune suspectée avant d'appliquer un correctif général (captures V05 et V06 du
propriétaire : plaque Port-Royal sans support, tableau des départs projeté devant la façade).

**Relevé** (`scripts/production/sign_survey.py scripts/mapkit/rf02.py`, même contrôle que pour RF01) : sur les
23 enseignes de RF02 (plaques de rue, enseignes peintes, affiches, pochoirs, tableau des départs, ERREUR Ø, Luna
Park), **aucune** n'était correctement accrochée :

- toutes à 4 unités de leur mur (le générateur les plaçait volontairement ainsi), 3 pour ERREUR Ø, 2 pour
  FERMETURE DÉFINITIVE ;
- la plaque BOULEVARD DE PORT-ROYAL pendait au-dessus de l'embouchure du boulevard du Montparnasse, sans aucun mur à
  moins de 32 unités (V05) ;
- les 4 dernières unités de chaque texture étaient coupées (lignes de décor raccourcies de 2 unités à chaque bout),
  bordure droite et dernière lettre comprises.

**Test dans le moteur avant correction** : 18 vues (face, biais, rasante) de six enseignes sur le build HUD-02 :
plaque Port-Royal flottant dans le ciel au-dessus de la rue, tableau des départs visiblement décollé de la façade.

**Correction à la source** (`scripts/mapkit/rf02.py`) :

- `sign()` et `use_decor()` prennent les extrémités sur la face du mur qui porte l'enseigne ; la ligne est posée à
  1 unité devant ; la texture entière est ajustée entre les extrémités (`texwidth=`, même option que RF01-PAN) ;
- 22 appels ramenés sur leur mur ; les bocaux de la vitrine de la pharmacie restent volontairement à 6 unités devant
  le miroir (l. 157 : « un miroir derrière les bocaux ») ;
- BOULEVARD DE PORT-ROYAL reposée sur l'angle du bâtiment de la pharmacie, face au boulevard, à la hauteur de la
  plaque BOULEVARD DU MONTPARNASSE de l'autre face (comme les plaques d'angle parisiennes) ;
- enseignes ÉPICERIE - VINS et LIBRAIRIE régénérées à la largeur de leur boutique (112 unités au lieu de 128) ;
- `materials_rf02.py` : le grain des plaques et enseignes dépendait de `hash()` de Python, qui change à chaque
  exécution ; remplacé par une empreinte stable (deux générations successives donnent les mêmes octets).

**Résultat** : relevé 21/23 tenues, lisibles et entières ; restent les bocaux (anomalie voulue, sourcée) et
LUNA PARK, dont les 48 unités du haut dépassent la palissade de 256 : l'enseigne monumentale demande la structure de
l'entrée en volume (V10, lot RF02-C). `RF02.wad` : lignes, secteurs et objets identiques ; seuls changent les
46 côtés et 46 sommets des 23 enseignes. Contrôle statique inchangé (14 153 cellules, sortie atteinte).

**Vues avant/après** : 66 vues (face, biais, rasante des 23 enseignes), build HUD-02 et build de développement, mêmes
caméras, personnages masqués.

Limite : le tableau des départs est désormais plaqué contre le mur mais n'a toujours pas de fixation visible ; son
support d'époque (cadre, consoles) est commandé à Astra (contrat, point 2 : `models/rf02/board_departures.obj`).

## 2. Lot Astra `RF2_MAP_02` en présentation HD

Première remise de reprise d'Astra (27/09, OWNER_REVIEW_REQUIRED), dans la variante qu'Astra recommande : quatre
façades (`RF2_FAC1/2/3/FACU`, 948×1659), vitrine TSF et Amiga (`RF2_TSFS`, `RF2_AMIG`, 1774×887) à leur définition
native, cinq accessoires sur une toile ×4 (seau, sacoche, radio éteinte/allumée, téléphone de campagne), avec le patch
d'échelles qui garde leur taille dans le monde (`TEXTURES.rf02`, `paris.zs`), importés ensemble (`7ceaf38`).

`scripts/production/import_astra_rf2_map_02.py` vérifie avant d'écrire : chaque cible encore à l'empreinte de base
d'Astra, chaque image livrée à son empreinte et à sa taille, le patch applicable. `paris.zs` sort identique au résultat
d'Astra ; `TEXTURES.rf02` n'en diffère que par les deux largeurs d'enseignes du §1. Registre :
`art/rf2_map_02_astra/IMPORT_RECORD.json` ; manifestes, notes, proposition HD, provenance, scripts, comparaisons et
validations archivés (41 fichiers). Non importés : les masters 3D (RF02-B), les 19 propositions sonores (COMBAT-02,
jamais écoutées par Astra), la variante de compatibilité, les builds de revue.

Contrôles : build, `check_runtime` PASS, RF02 A et B PASS. Une première traversée A a manqué la sacoche du ticket
(l'autopilote est arrivé par un autre chemin ; le test d'orientation de la sacoche est étroit) ; la seconde a déclenché
les 27 scènes. L'import ne change aucune donnée de collision, d'usage ou de visibilité.

## 3. Les dix captures du propriétaire (V01–V10), mêmes cadrages

Caméras reconstruites en trois passes sur le build que le propriétaire a joué (`RF2_MAP-02_20260927_1543`, même
résolution 1786×1011, FOV 90) jusqu'à retrouver ses cadrages ; puis mêmes caméras sur le build de développement du
commit `9510b39` (enseignes, lot HD d'Astra, figures), sans HUD (art) et avec HUD (lisibilité). Les ennemis
éveillés et les messages de la capture d'origine ne sont pas reproduits (ils dépendent du moment de la partie).
Preuves hors dépôt : `dist/evidence_wip/RF02_V01-V10_20260928/` (40 captures, deux planches, caméras, build).

| ID | État au commit `9510b39` | Reste |
|---|---|---|
| V01 | seau galvanisé HD (sprite d'Astra), l'uniforme qui brûle les formulaires à côté | objet en volume (master 3D d'Astra, RF02-B) ; combustion |
| V02 | la femme est à la poignée | poussette réelle (modèle d'Astra testé, RF02-B) ; registres ficelés ; approche des deux côtés |
| V03 | façades HD | tram complet et rails (RF02-B) ; durée du message précédent (UI) |
| V04 | vieil homme assis, yeux qui s'ouvrent | intérieur du tram (RF02-B), inspection du ticket |
| V05 | **plaque Port-Royal accrochée** à l'angle ; façades HD | profondeur et matières de la pharmacie (bocaux) |
| V06 | tableau plaqué contre la façade | support d'époque (modèle commandé à Astra) |
| V07 | **vitrine TSF HD** (postes crédibles) | grille, éclairage, cycle de fondu du texte à vérifier |
| V08 | façades HD | variantes d'ennemis, messages hors zone de combat et relecture (UI), livres de la barricade |
| V09 | **téléphone de campagne identifiable** (HD) | table, sacs de sable, câblage ; compteur du Browning ; attribution des répliques |
| V10 | façades HD | entrée et abords de Luna Park en volume (RF02-C) |

Aucun ID n'est déclaré corrigé sans son état chargé en jeu ; aucun n'est accepté par le propriétaire.
