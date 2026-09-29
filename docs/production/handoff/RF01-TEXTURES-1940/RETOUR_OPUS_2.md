# RF01-TEXTURES-1940 — retour d'Opus n° 2 sur l'ensemble représentatif du 29/09

Envoi `incoming/astra/RF01_TEXTURES_1940/02_SOUBASSEMENTS_MATIERES_20260929/` (6 matières + 4 décals).
Opus, 29/09/2026. Rien ici ne vaut accord du propriétaire : ce sont les observations d'Opus dans le moteur.

## Reçu et intégré

- 121 fichiers conformes à `SHA256SUMS.txt` (sha256 de la liste `b28372e8…`, manifeste `d015030d…`) ; chaque original
  remplacé était à l'empreinte de la candidate 1745. Fiche : `art/rf01_textures_1940_astra/IMPORT_RECORD_02_SOUBASSEMENTS.json`
  (branche `candidate/rf01-textures-1940`, commit `fadb3d8`).
- Intégrés : `RFP_DADB`, `RFP_DADG`, `RFP_DADR`, `RFP_PLN`, `RFF_CER`, `RFW_TBLS` et leurs six blocs de
  `TEXTURES.six_replacements.txt` (pixels doublés, XScale/YScale 8, même taille monde). Rien d'autre ne change par
  rapport à la candidate 1745 ; RF02 est identique au build accepté.
- Candidate : `dist/candidates/RF2_RF01_TEXTURES_1940_20260929_1606/` (sha256 `67485285…`), lanceur
  `JOUER_RF2_RF01_TEXTURES_1940.cmd`. Traversées RF01 A et B : PASS. Les candidates précédentes restent en place.
- **Décals `RFDSTN1…4` : reçus, contrôlés, non intégrés** (ci-dessous). Les décals actuels restent.

## Vu dans le moteur (cadrages face à face, même lumière ; `evidence/planches/` de la candidate 1606)

1. **Trois soubassements distincts : objectif atteint.** Écart de couleur de la bande peinte (CIE76) : 19,9 / 30,8 /
   29,8 dans les textures (ton premier envoi : 0,2 / 6,7 / 6,7) ; 28,6 / 37,8 / 43,5 vus dans la lumière de RF01. Les
   trois familles se reconnaissent d'une pièce à l'autre.
2. **Le sang-de-bœuf vire au rose sous forte lumière.** Au POSTE, le mur proche se lit rose saumon (`#c77d74`,
   clarté 60) ; à l'ÉCONOMAT, plus sombre, il reste sang-de-bœuf (`#935646`, clarté 43). La texture elle-même est à
   clarté 42 : c'est la lumière chaude de la pièce qui l'éclaircit. Proposition, **à confirmer par le propriétaire
   avant de refaire** : un sang-de-bœuf un peu plus sombre et moins orangé (clarté 36–38 dans la texture), en gardant
   au moins 15 d'écart avec les deux autres. Le bleu (`#647177` en moyenne dans le jeu) et le vert (`#93a17e`) se
   lisent comme prévu.
3. **Gain de matière visible de près** à 8 px/u : grain de l'enduit, carreaux du sol, côté de table plein (il laissait
   voir un vide noir). De très près, les pixels restent carrés : cela vient du filtre de texture de la configuration
   (`gl_texture_filter=6`, agrandissement au plus proche), pas de tes images. Ne pas compenser par du flou.
4. **Décals trop discrets** (17 décals de RF01, chacun regardé de face, `planche_decals.jpg`) : humidité et frottement
   presque invisibles sur les nouveaux soubassements et sur le carrelage ; crasse lue comme une projection de points
   au lieu d'une salissure ; coulure réduite à un trait très fin. Les actuels, plus grossiers, se lisent mieux.

## Ce qu'Opus attend (nouvel envoi, sans réécrire celui du 29/09)

1. Les quatre décals corrigés, mêmes noms et même taille monde : masses plus larges et plus contrastées, alpha
   progressif, lisibles à 2–4 m dans la lumière de RF01 sur les trois soubassements et sur le carrelage blanc ; crasse
   en salissure continue ; coulure plus large avec sa traînée. Vérifie-les dans le moteur sur les 17 cadrages
   (`evidence/vues/vues_decals3.json` de la candidate : caméras 8 unités devant le décal, tournées vers le mur).
2. Le sang-de-bœuf plus sombre **seulement si le propriétaire le demande** ; sinon garder le tien.
3. Puis l'extension au lot complet (reste de l'inventaire), avec les mêmes règles : 8 px/u pour ce qui se voit de
   près, 4 px/u pour les façades ; échelle, géométrie et jeu inchangés ; les 12 conservations restent conservées ;
   RF01 seulement, aucune ressource partagée écrasée, RF02 intact. Opus l'intègre dans une nouvelle candidate datée,
   avec les mêmes contrôles (empreintes, isolement de RF01, cadrages avant/après, traversées A et B).
