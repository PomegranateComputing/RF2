# RF01-TEXTURES-1940 — contrat technique d'Opus pour Astra

Mandat du propriétaire du 28/09 (`RF2_RF01_TEXTURES_1940_OPUS.md`) : passe courte sur les textures et matières du
décor existant de RF01, pour un établissement psychiatrique français ancien en 1940, austère, usé, crédible. Astra
produit les ressources ; Opus garde l'inventaire, les définitions, la carte, l'intégration et le build.

## 0. Base et livraison

- **Base** : le build RF01 accepté (tag `rf01-owner-accepted-20260927`, pk3 `04bdd0ae…`, `JOUER_RF2_ART_REVIEW.cmd`
  inchangé). Le lot est une candidate isolée sur la branche `candidate/rf01-textures-1940` (tag + socle), comme
  RF01-PAN : les panneaux (`RFSIGN*`) restent dans leur lot et n'entrent pas ici. La ligne cumulative
  (`prod/rf2-campaign`) reçoit la passe ensuite.
- **Dépôt** : dans ton worktree, `incoming/astra/RF01_TEXTURES_1940/<envoi>/` (`01_premier_ensemble/`, puis
  `02_ensemble/`…), sans réécrire un envoi précédent. Par envoi : `manifest.json` (pour chaque fichier :
  `target_relpath`, `sha256`, taille en px, taille dans le monde en unités, px/unité, `base_sha256` de l'original
  qu'il remplace ou dont il est la variante, source, méthode, références consultées, crédits), `SHA256SUMS.txt`,
  preuves (planches, rendus au bon tuilage).
- Tu ne modifies ni carte, ni `TEXTURES.*`, ni `MODELDEF`, ni code, ni sons. Opus pose les échelles, les variantes et
  les affectations.

## 1. Inventaire

`INVENTAIRE.md` (tableau) et `inventaire.json` (empreintes, dimensions, usages par zone, autres cartes, dépendances),
générés par `scripts/production/rf01_texture_inventory.py` depuis la carte construite. 60 entrées : 35 textures
murales, 15 plats, 6 modèles d'accessoires (un atlas commun), 4 décalques d'usure. Hors lot : `F_SKY1` (ciel),
`RFSIGN0…9` (plaques, lot RF01-PAN). Les objets ramassables, notes, clés, ennemis, armes, HUD et menus ne font pas
partie de la passe.

`captures/` : une vue de chaque entrée sur le build accepté (personnages masqués pour la prise de vue) et les zones
demandées aux réglages normaux (1920×1080, FOV 90, même rendu) : chambre de départ, couloir du pavillon ouest,
admissions, lingerie (pièce d'eau et buanderie), poste (mobilier proche), économat, cour des hommes.

## 2. Règles par famille

**Taille dans le monde conservée.** Chaque entrée garde la taille de la colonne « Monde » : un carreau ne grossit pas
parce que le fichier grandit. La taille en pixels est libre ; Opus règle `XScale`/`YScale` = px par unité.
Densité conseillée : **8 px/u** pour ce qui se voit de près (murs, sols, plafonds, portes, côtés de meubles : un mur
de 256 u → 2048 px, un sol de 128 u → 1024 px) ; **4 px/u** pour les façades vues de loin (`RFS_FACD`,
`RFS_HOSP`). Au plus 2048 px par côté ; pas de 4K. Opus mesure la mémoire dans les scènes chargées.

**Raccords.** Tout se répète sans couture dans les deux sens. Les plats sont alignés sur la grille du monde (128 u,
64 u pour `RFT_BED` et `RFM_TOP`) : carreaux de `RFF_CER` de 32 u (quatre par plat), dalles de `RFF_SLAB` de 64 u,
joints à taille crédible.

**Murs à soubassement** (`RFP_DADB`, `RFP_DADG`, `RFP_DADR`, 256×256 u) : la carte les cale **par le bas**
(le bas de l'image = le sol). Garder le soubassement peint sur les **44 u du bas** et la moulure juste au-dessus ;
l'enduit au-dessus. Les trois familles servent aussi à s'orienter (bleu : admissions et couloirs ; vert : salles et
chambres ; sang-de-boeuf : registres et loge) : les rendre plus anciennes et désaturées, mais distinctes.
`RFP_TILE` : faïence de 16 u jusqu'à 48 u, enduit au-dessus, même calage.

**Portes** (`RFD_SGL` 64×128, `RFD_DBL` 128×128, `RFM_DOOR` 64×128) : portes qui montent dans le linteau ; l'image
entière est le vantail et son cadre. Poignée ou serrure entre 36 et 44 u du sol, du côté de l'ouverture habituelle ;
`RFD_DBL` a deux vantaux avec montant central. Pas de vitrage peint sur une porte pleine.

**Transparences.** `RFG_WIN` : vitrage à alpha progressif (garder la lecture du verre) ; `RFG_VITR` : vitrail
masqué **et sa brightmap** `RFG_VITR_BM` (même taille, blanc = lumière qui passe) ; `RFM_GRIL` : grille opaque (barreaux
et fond sombre), ne pas la rendre transparente.

**Interrupteur** : `RFM_SW0` (éteint) et `RFM_SW1` (allumé) forment une paire (ANIMDEFS) : même cadrage, seul l'état
change.

**Côtés de meubles** (blocs de la carte) : `RFT_BEDS` 64×32, `RFT_HEAD` 64×48, `RFW_TBLS` 64×32, `RFW_SHLF`
64×64, `RFM_VATS` 64×48 ; l'image est le côté entier du bloc, bas = sol, haut = arête du dessus (`RFT_BED`,
`RFW_TOP`, `RFM_TOP`). Ne pas dessiner de pieds ou d'ouvertures incompatibles avec le bloc plein.

**Accessoires** (`models/props/*.obj`) : les six modèles de RF01 et ceux des autres cartes partagent
`models/props/atlas.png` (2048²). Livrer **`atlas_rf01.png`**, même disposition UV exacte (mêmes îlots), 2048² ;
Opus l'attache aux seuls accessoires de RF01. Maillages, silhouettes, dimensions et collisions inchangés.

**Décalques d'usure** (`graphics/decals/RFDSTN1…4`, humidité, crasse, coulure, frottement) : masques à alpha
progressif, propres à RF01 : remplacement direct possible. L'usure se concentre aux passages, bas de murs, abords des
équipements ; pas de moisissure uniforme.

**Noms.** Chaque fichier porte l'identifiant de sa cible. Pour une ressource partagée avec RF02 ou les écrans de
l'interface, livrer la **variante RF01** nommée dans la colonne « Action » (`RFx4…` : les trois premières lettres
sont conservées, le moteur en déduit le matériau d'impact des balles : RFW/RFD bois, RFM métal, autres plâtre).
Aucun autre renommage.

**Textes.** Aucune inscription, signalétique médicale ou date inventée. Ne pas neutraliser les anomalies narratives
présentes. Les plaques restent au lot RF01-PAN.

## 3. Direction artistique

Celle du mandat : enduit crème jauni, soubassements anciens gris-vert ou gris chaud, reprises et frottements à hauteur
de mobilier ; faïence ivoire aux joints grisés, calcaire près des points d'eau ; grès, ciment ou dallage, passages
polis, bords ternes, parquet seulement où il est cohérent ; plâtre mat ivoire/gris aux fissures et auréoles localisées ;
bois sombre ou peint ancien, vernis usé aux contacts ; fer et fonte peints, émail fatigué, rouille seulement aux
endroits plausibles ; toile écrue, couvertures ternes ; pierre, enduit et soubassements extérieurs patinés selon
l'exposition. Surfaces de repos visuel conservées ; ni sang ajouté, ni capitonnage générique, ni asile américain
abandonné. Aucune couleur n'est présentée comme attestée à Sainte-Anne en 1940 : références françaises datées,
citées dans le manifeste. L'éclairage, le brouillard, le gamma et le ciel du niveau ne changent pas : ne pas assombrir
les textures pour faire lugubre.

## 4. Ordre

1. **Premier ensemble** (en gras dans l'inventaire), chambre de départ et couloir du pavillon ouest :
   `RFP_DADG`, `RFP_DADB`, `RFP_PLN`, `RFF4WOOD` (variante de `RFF_WOOD`), `RFF4CER` (de `RFF_CER`), `RFP4CEIL`
   (de `RFP_CEIL`), `RFD4SGL` (de `RFD_SGL`), `RFT_BEDS`, `RFT_HEAD`, `RFT_BED`, `atlas_rf01.png` (au moins les
   îlots du radiateur). Opus l'intègre, l'examine dans le moteur (près, à distance, en mouvement) et renvoie ses
   remarques de palette, d'échelle et de raccords.
2. **Le reste** des entrées « dans le lot », en un ou deux envois cohérents par zone.

Opus livre ensuite la candidate `JOUER_RF2_RF01_TEXTURES_1940.cmd` (dossier daté), les comparaisons aux mêmes
cadrages, la liste remplacé / conservé / problème résiduel et une courte visite en moteur.
