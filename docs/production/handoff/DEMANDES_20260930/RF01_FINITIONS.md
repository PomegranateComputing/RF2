# Demande RF01-FIN-V03 — sang-de-bœuf et décals d'usure

| | |
|---|---|
| ID, version | RF01-FIN-V03 (suite de `02_SOUBASSEMENTS_MATIERES_20260929`, qui reste figé) |
| Priorité | P3 (après le Rapid et la première famille d'ennemis) |
| Base | ligne de production `prod/rf2-campaign` `23808c6` : les six matières du 29/09 y sont (candidate cumulée `RF2_CUMUL_20260929_1801`, sha256 `5115307c…`) ; retour détaillé : `RF2_SUITE_20260929/RETOUR_OPUS_2.md` |
| Cible | RF01 seulement ; les douze entrées conservées, la géométrie et RF02 ne changent pas |

## 1. `RFP_DADR` plus sombre (demande du propriétaire, 29/09)

Constat dans le moteur : au POSTE, sous la forte lumière chaude, la bande lit rose saumon (`#c77d74`, clarté 60) ; à
l'ÉCONOMAT elle reste sang-de-bœuf (`#935646`, clarté 43). La texture est à clarté 42.

Attendu : même motif, même taille monde (8 px/u, XScale/YScale 8), bande peinte plus sombre et moins orangée
(clarté visée 34–38 dans la texture), qui reste sang-de-bœuf au POSTE ; écart de couleur ≥ 15 avec `RFP_DADB` et
`RFP_DADG`. Opus ne compense pas en assombrissant la pièce : la lumière du POSTE éclaire aussi d'autres matières.
Contrôle : cadrages `zone_POSTE` et `RFP_DADR_middle` (liste `evidence/vues/vues_b1.json` de la candidate 1606), même
lumière, avant/après.

## 2. Les quatre décals `RFDSTN1…4` (humidité, crasse, coulure, frottement)

Constat (17 décals de RF01, chacun regardé de face à distance de jeu ; `planche_decals.jpg` de la candidate 1606) :
humidité et frottement presque invisibles sur les nouveaux soubassements et sur le carrelage ; crasse lue comme une
projection de points ; coulure réduite à un trait fin. Les décals d'origine se lisent mieux et restent en place.

Attendu : masses plus larges et plus contrastées, alpha progressif, lisibles à 2–4 m dans la lumière de RF01 sur les
trois soubassements et sur la faïence blanche ; crasse en salissure continue ; coulure plus large avec sa traînée ;
frottement en éraflures horizontales à hauteur de meuble. Mêmes noms, même taille monde (les définitions `DECALDEF`
ne changent pas : dis-le si une échelle doit changer, Opus ajuste l'application, pas ton image). Contrôle : les 17
caméras de `evidence/vues/vues_decals3.json` (8 unités devant le mur marqué, tournées vers lui).

## Fichiers attendus

`incoming/astra/RF01_TEXTURES_1940/03_FINITIONS_<date>/` : `RF2_SA_RFP_DADR.png` et son bloc `TEXTURES` s'il change,
`graphics/decals/RFDSTN1…4.png`, captures avant/après de tes contrôles, manifeste, sommes. Opus intègre dans la
ligne cumulée et exporte une nouvelle candidate datée seulement si le résultat se lit mieux que l'existant.

## Ensuite

Le lot complet (reste de l'inventaire RF01) peut suivre dans le même envoi ou un suivant, aux mêmes règles : 8 px/u
pour ce qui se voit de près, 4 px/u pour les façades ; échelle, géométrie et jeu inchangés ; douze conservations ;
aucune ressource partagée écrasée.
