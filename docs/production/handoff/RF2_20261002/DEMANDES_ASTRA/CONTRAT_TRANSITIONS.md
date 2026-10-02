# Planches de transition — le système en place

Code : `src/zscript/rf/comics.zs`, `director.zs`, `hud.zs` ; scènes : `src/COMICDEF` ; légendes : `src/LANGUAGE`.
En jeu depuis le 01/10 avec cinq planches de Codex (`CONTRATS/T01_PLANCHES_FICHIERS.csv`). Toute planche d'Astra
remplace un fichier existant au même nom, ou ouvre une nouvelle transition que je déclare.

## Format d'une planche

| Point | Contrat |
|---|---|
| Fichier | `graphics/comics/<DE>_<VERS>.png`, **1920 × 1080 px**, sRGB, art sans aucun texte de légende (les inscriptions du décor appartiennent à l'image) |
| Cases | 3 à 5 rectangles, donnés en pixels de la page (x, y, largeur, hauteur) dans l'ordre de lecture ; les cases pas encore atteintes sont assombries par le jeu, puis révélées une à une |
| Légende | texte séparé (UTF-8), composé par le jeu ; deux placements : `band` = en crème, centré dans une zone de la bande noire de la page (les cinq planches actuelles : bande basse, zone x 105–120, y 955–960, largeur 1680–1710, hauteur 65–120) ; sans `band` = cartouche crème posé sur l'art dans la zone donnée |
| Bande | si la légende va dans la bande : réserver une bande noire d'au moins 126 px en bas (ou en haut) de la page |
| `planche.json` | `{id, image, dimensions:[1920,1080], cases:[{id, rect:[x,y,w,h]}…], legendes:[{id, texte, zone:[x,y,w,h], apres_case:"<id de case>"}]}` : c'est le format lu pour les cinq planches en place |

Scènes déclarées : `RF01_RF02`, `RF02_RF04`, `RF04_RF05`, `RF05_RF06`, `RF06_RF07`. Une scène ne joue que si son image
est dans le build ; sinon le chapitre finit sur son texte de sortie.

## Comportement vérifié (candidate 1605, puis build des portes)

- La page entière reste à 16:9 dans l'écran ; bandes noires sur les côtés en 21:9, en haut et en bas en 4:3.
- `Utiliser` : case suivante, puis chapitre suivant ; `Utiliser` maintenu : passer la planche ; `Tirer` avance aussi et
  **ne tire pas** à l'arrivée dans la carte suivante.
- Sauvegarde pendant la planche, puis chargement : la planche reprend et mène au chapitre suivant.
- **À l'arrivée, Viktor est libre** : le cas du gel au début de RF02 (drapeaux de fin de chapitre portés à la carte
  suivante, corrigé le 30/09) est rejoué à chaque candidate, pour chaque transition (`scripts/production/chain_test.py`,
  `comic_flow_probe.py`).

## Pour une nouvelle planche

Livrer le PNG, `planche.json` et la légende. Je contrôle : lecture case par case, passage rapide, tir maintenu,
sauvegarde et chargement, trois formats d'écran, arrivée libre. Le maître peut être plus grand (3200 × 1800) : l'export
de jeu reste 1920 × 1080. Les interludes T06–T16 du pack correspondent à des cartes qui ne sont pas encore produites
(RF08 et suivantes) : planche et déclaration au moment où la carte existe.
