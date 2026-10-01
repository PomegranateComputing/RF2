# Retour d'Opus sur les sept lots du 01/10 (Codex)

Intégration et contrôles moteur sur le build de développement (UZDoom 5.0.1). **Ce sont des contrôles techniques,
pas des acceptations du propriétaire.** Captures dans `LOTS_20261001/` à côté de ce fichier ; enregistrements d'import
dans `../IMPORT_<lot>.json`.

## Réception

| Point | Constat |
|---|---|
| Empreintes | les sept `SHA256SUMS.txt` vérifient tous les fichiers |
| Fins de ligne | les sept `SHA256SUMS.txt` sont en **CRLF** (le contrat demande LF ; `R2F8_V02/POUR_OPUS.md` dit LF) — à corriger pour les prochains lots |
| Bases | 44 fichiers importés : 27 remplacements conformes à leur `base_sha256`, 17 neufs (les 16 sprites R4V2/R4V3 et la planche) ; aucun refus |
| Générateurs | les images importées sont protégées : `materials_rf04.py` les lit sans les redessiner, `materials_rf02.py` ne redessine plus `RF2_PHVI` |

## Lot par lot

| Lot | Intégration | Contrôle moteur | Suite demandée |
|---|---|---|---|
| `R2F8_V02` | `RFViktorMirror` revenu à `Scale 0.18` | vitrine RF02 à 30/70/130 u : le reflet mesure 56 u, il est à hauteur du joueur (`rf02_reflet_avant_apres.jpg`) | rien |
| `R4V2_R4V3_V01` | deux acteurs de miroir neufs, montrés pendant la scène du badge (l. 533–539) à côté de son reflet : trois panneaux de miroir à l'ouest de la salle, la tenue noire dans celui qu'il regarde, la blouse grise dans le panneau sud, la chemise au badge dans le panneau nord ; ils disparaissent à la fin de la scène (« Le badge disparaît ») | `rf04_miroirs.jpg` : même visage, même hauteur dans les trois panneaux ; hors scène, seul le reflet noir ; aucune figure dans la salle | rien ; le texte du badge reste `LANGUAGE` |
| `RF02_PHARMACIE_01` | définition 512 × 320 à 8 px/u appliquée | posé à 40 u, le panneau couvrait la tête et le buste du reflet (le reflet disparaissait) ; **remonté en haut de la vitrine (72–112 u)** : le reflet se lit sous la tablette, `FORTIFIANT` lisible à 30 et 70 u | si tu préfères une autre composition pour cette place (bocaux en haut, verre vide en bas), dis-le |
| `LOT_CORRECTIONS_01` | `RFDSTN1`, `RF4_NIAG`, `RF4_CLE5`, `RF4_CLE4` | humidité RF01 : visible aux pieds des murs dans 5 des 6 vues d'humidité (la vue 05, escalier, ne la montre ni avant ni après) ; elle se lit encore comme un **moucheté** plutôt qu'une auréole continue (`rf01_humidite_avant_apres.jpg`). Niagara lisible au sommet de la rampe à ~280 u et depuis le fond du bassin ; clefs : les deux états justes (`rf04_niagara_clefs.jpg`) | `RFDSTN1` V05 facultative : masse continue, bord progressif |
| `ORDY_E_V04` | 8 rotations de E | film de la boucle à vitesse de jeu, profil, RF01 avant/après (B-C-D-E, 4 tics par pose) : `build/dev/lots_20261001/ordy_marche_*` (copie des films dans ton dossier `handoff/RETOURS_OPUS/`) | ton avis sur le raccord E→B à partir des films |
| `LUNA_PILOTE_01` | six surfaces ; `RF4_BROO` à 256 × 192 u ; la façade est posée sur une masse de 192 u, son passage (64 × 112 u) sous le décor au centre, la texture continue au-dessus | vues `rf04_pilote_planche_1…5.jpg` (23 caméras de `vues/rf04_pilote.json`) | voir ci-dessous |
| `COMIC_RF01_RF02_01` | `COMICDEF` sur `planche.json` (4 cases, une légende après la 4e, dans la bande noire, composée par le jeu en crème) | lecture case par case, passage rapide, tir maintenu, sauvegarde pendant la planche puis chargement : RF02 atteint à chaque fois ; 16:9, 21:9 et 4:3 : page entière, bandes noires (`planche_rf01_rf02_*.jpg`) | rien de ton côté ; la police du jeu espace le trait d'union (« Sainte - Anne »), je le regarde |

## Zone pilote RF04 : ce qui manque à l'image

1. **`RF4_BOIS` est livré opaque** (RVB sans alpha) alors que la fiche et la carte en font un treillis vu à travers :
   posé sur les contreventements, la charpente se lisait comme des murs de planches. Je l'ai gardé pour les flancs de
   la voie (opaque, c'est juste) et j'ai mis sur les treillis un provisoire masqué **`RF4_TREI`** (64 × 224 u, bois blanc
   écaillé en croix de Saint-André, vides transparents). Demande : `RF4_TREI` à ta main, masqué.
2. **`RF4_BROO`** : la façade fait 256 × 192 u ; le passage praticable occupe u 96–160 depuis le bord nord (gauche
   vu de l'esplanade) et monte à 112 u du sol, soit les lignes 320–768 px de ton image à 4 px/u. Aligne l'arche peinte
   sur cette ouverture ; deux tourelles de pierre se dressent au-dessus des extrémités de la façade (u 0–32 et 224–256).
3. **Provisoires d'Opus à remplacer** (mêmes noms, mêmes tailles) : `RF4_BALU` balustrade masquée 64 × 32 u ;
   `RF4_CHUT` dessus de rampe 64 × 64 u (flat) ; `RF4_CHUS` flancs de rampe 128 × 64 u ; `RF4_TOWR` tour 128 × 256 u ;
   `RF4_POTE` poteau 16 × 128 u ; `RF4_PORT` revers des portes 256 × 256 u (la version actuelle, aux grandes arches,
   ne ressemble pas aux portes à dômes du panorama) ; `RF4_MAST` mât 16 × 512 u ; `RF4_ROCF` dessus de rocher 64 × 64 u
   (flat) ; `RF4_BRBK` revers du décor Brooklyn 256 × 192 u ; `RF4_TREI` ci-dessus.
4. **Façades des attractions** `RF4_FAC1`, `FAC2`, `FAC3` (provisoires du 30/09, 128 × 256 u à 2 px/u) : elles bordent
   maintenant l'esplanade à l'est (masses de 192 u) et habillent la salle de danse (256 u) ; elles sont pauvres à
   l'image. Demande : trois façades de 128 × 256 u, l'essentiel dans les 192 u du haut (la texture est accrochée en haut).
5. Ce qui est construit en géométrie depuis le 01/10 et attend ton regard : la piste du grand huit sur les crêtes de
   rochers (ouest et nord), les piliers à dômes des portes, le pavillon au sommet de la tour de la rampe, les nacelles
   de la tour aérienne, un kiosque à musique et un manège sur l'esplanade.

## Prochaines demandes (rappel du contrat)

Planches RF02→RF04, RF04→RF05, RF05→RF06 ; RF05 (sous-station voûtée, galeries, pompes, parc rallumé, enseignes à
ampoules, train de trois voitures, couples des miroirs : figures visibles seulement dans les miroirs, jamais dans la
salle) ; sons d'armes selon le routage ; familles ennemies suivantes ; boss. Aucune de ces tâches n'est déclarée faite ici.
