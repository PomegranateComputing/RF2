# RF2 — portrait HUD de Viktor, six états (27/09/2026)

Commande du propriétaire : `RF2_VIKTOR_HUD_OPUS.md` (remise dans la conversation du 27/09, jointe à la planche).
Remplace l'ancien visage du HUD (conservé tel quel dans `art/rf2_hud_viktor_01/`, plus empaqueté).

## Source

| Fichier | Rôle |
|---|---|
| `source/RF2_VIKTOR_HUD_SHEET.png` | planche fournie par le propriétaire, 1536×1024 RGBA, six portraits détourés (canal alpha réel), sha256 `2b7fde2f…d1cc3c` |
| `manifest.json` | état → fichier, position mesurée de chaque tête sur la planche, empreintes des six PNG |
| `scripts/ui/viktor_portraits.py` | découpage reproductible |

La planche a été générée par le propriétaire avec le générateur d'images intégré, à partir de quatre références
(la photographie 11976.png fixe la ressemblance ; 11975, 11977, 11978 l'apparence). Ces références n'ont pas été
transmises au dépôt ; seule la planche l'a été. L'acceptation de la ressemblance reste au propriétaire.

Prompt de la planche (texte du propriétaire) : voir la section « Prompt de la planche source » de la commande ;
résumé : six états du même portrait (intact, légèrement blessé, blessé, grièvement blessé, critique, mort), plaies
cumulées aux mêmes emplacements, cadrage et lumière identiques.

## Découpage

Les portraits ne sont pas sur une grille exacte de 512 px (axes des têtes espacés de 496 à 500 px, sommets du crâne
décalés de 3 à 11 px). Chaque tête est cadrée depuis sa propre silhouette : sommet du crâne à y 9, axe de la tête à
x 256, image 512×512 (taille du logement actuel). Les six têtes ont la même échelle sur la planche (largeur du crâne
237–240 px aux mêmes hauteurs) : aucune mise à l'échelle. Les pixels plus proches d'un portrait voisin sont effacés ;
le même fondu ferme les six silhouettes sur les côtés et en bas. Contrôle : repères des sourcils, yeux, nez, bouche et
menton alignés à quelques pixels (moins d'un pixel à la taille du HUD en 1080p).

## États

| Fichier (`src/graphics/hud/viktor/`) | État | Santé (part de la santé maximale normale, 100) |
|---|---|---|
| `VIKTOR_H100.png` | intact | plus de 80 % (la sur-vie reste ici) |
| `VIKTOR_H080.png` | légèrement blessé | plus de 60 %, jusqu'à 80 % |
| `VIKTOR_H060.png` | blessé | plus de 40 %, jusqu'à 60 % |
| `VIKTOR_H040.png` | grièvement blessé | plus de 20 %, jusqu'à 40 % |
| `VIKTOR_H020.png` | critique | vivant, 20 % ou moins |
| `VIKTOR_DEAD.png` | mort | joueur mort (prioritaire) |

Sélection : `RFPortrait.StateOf()` dans `src/zscript/rf/hud.zs`, partagée par le HUD et les contrôles de
développement ; l'armure n'intervient pas.

## Remarque

Sur la planche, les iris tirent vers le bleu-vert ; la commande dit « yeux bleus ». Non retouché : à juger par le
propriétaire.
