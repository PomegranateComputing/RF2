# Arsenal — un contrat par arme (Opus, 01/10/2026)

Lus avant d'écrire : la bible (`legacy/import/RF2_DOSSIER_MAITRE.md` §10 « Arsenal : périmètre et priorités »), le
pack arsenal du 28/09 (`C:\PROJECTS\RF2_ARSENAL_20260928\01_ARSENAL_ET_MODELES.md`, repères W01–W10), le contrat
moteur v2 (`CONTRAT.md`, seul en vigueur), l'état de production. Les deux sources ne disent pas la même chose pour
toutes les armes : **ce tableau distingue ce qui est décidé, ce qui est éprouvé au banc et ce qui reste à décider par
le propriétaire.** Les dégâts, cadences et réserves restent des valeurs de prototype (bible §10). Aucune arme n'est
attribuée à une carte par ce document.

## État et décision par arme

| Repère | Arme | Bible §10 | Pack 28/09 | État au 01/10 | Ce qui manque pour avancer |
|---|---|---|---|---|---|
| W01 | Browning Hi-Power | première tranche | référence acceptée | **en campagne** (`RFBrowning`) ; image acceptée | sons (Codex, `ROUTAGE_SON_ARMES.md`) |
| W02 | FN FAL | arme-signature | référence acceptée | **en campagne** (`RFFAL`) ; image acceptée | sons |
| W03 | Manufrance Rapid (fusil de chasse à pompe, cal. 12) | « fusil à pompe de type riot », première tranche | choix d'adaptation | **banc** (V02) ; fonctionnement 4+1 **figé** | sons ; date d'entrée dans le parcours (postérieur à 1940) |
| W04 | Manurhin MR73 Gendarmerie 4" | (absent de la bible) | choix proposé, complète le Browning | **banc** (V02) ; barillet six chambres **figé** | sons ; date d'entrée (postérieur à 1940) |
| W05 | FAMAS F1 | après validation de la tranche | variante F1 proposée | **banc** (V01, images d'essai) | images finales ; sons |
| W09 | Scie Black & Decker Scorpion | seconde vague | KS890EK-QS proposée | **banc** (V01) ; cadence réparée **figée** | **alimentation à décider** (filaire réelle : convention de jeu à nommer) ; sons |
| W10 | Pied-de-biche d'atelier | — | proposition | **en campagne** (`RFCrowbar`), réemployé au banc | sons |
| W06 | Browning M2 .50 (M2HB) | seconde vague, « mode d'emploi en jeu à arbitrer » | présentation portable ou montée à fixer | références préparatoires seulement | **présentation à décider** : arme montée (poste fixe, point d'appui) ou portée ; ne pas en faire un décor en silence |
| W07 | RPG (RPG-7V proposé) | **« n'est pas une demande validée »** | proposé | références préparatoires seulement | **confirmation du propriétaire** avant toute production |
| W08 | Lance-flammes (M2-2 proposé) | « demande antérieure à reconfirmer » | modèle à déterminer | références seulement | **reconfirmation du propriétaire**, puis modèle |
| — | Pistolet taser | seconde vague, « contrôle rapproché ou interruption ciblée » | **absent du pack (pas de repère W)** | rien | **repère à attribuer** (W11 proposé), modèle et époque à fixer |

## Contrat commun (toutes les armes)

Le contrat moteur v2 s'applique : toile 1536 × 1024, mêmes bras et manche de sweat noir, fichier d'animation
`rf2-bench-animation/1`, événements sonores nommés (routage : `docs/production/handoff/RF2_20261001/ROUTAGE_SON_ARMES.md`),
banc d'abord, campagne ensuite sur décision. Une arme est un système complet (bible §10) : apparence, mains, sons,
animation, cadence, réserve, rechargement, impacts, retours sur les cibles, ramassage, nom HUD, comportement en
sauvegarde. Les conventions réversibles prototypées au banc sont nommées dans `docs/RF2_ARSENAL_BANC.md`.

## Contrats propres

**W05 FAMAS F1.** Automatique compact au rythme distinct du FAL ; sélecteur coup par coup / rafale (tir secondaire au
banc) ; chargeur 25 ; événements `shot`, `dry`, `mag_out`, `mag_in`, `seat`, `bolt`, `mode`, `cloth`, `raise`. Reste :
images finales d'Astra/Codex sur le master commun ; sons.

**W09 Scie Scorpion.** Mêlée motorisée : `start` à l'appui, `loop` tenu, `contact` à chaque prise, `stop` au relâchement
(la boucle s'arrête toujours : relâche, rangement, mort). Cadence de contact réparée le 30/09 : figée. Décision
attendue : la convention d'alimentation (câble et rallonge visibles ? batterie fictive nommée comme adaptation ?) ; le
pack interdit d'inventer une version commerciale à batterie sans la déclarer.

**W06 M2HB (à décider).** Deux présentations possibles, toutes deux réversibles au banc : (a) poste fixe : Viktor
utilise une arme montée sur trépied à un endroit de carte, vue proche du mécanisme, pas d'inventaire ; (b) arme portée,
lente, réserve rare. Proposition d'Opus : (a), qui garde « masse et son immédiatement reconnaissables » sans faire
porter 38 kg à un administrateur de bases de données. Rien n'est produit avant le choix.

**W07 RPG, W08 lance-flammes, taser.** Aucune production tant que le propriétaire n'a pas confirmé l'arme (RPG,
lance-flammes) ou fixé son repère et son modèle (taser). Les références préparatoires restent des références.

## Ordre proposé

Sons des armes en place (W01, W02, W10, puis W03, W04) → W05 et W09 complets au banc → décision M2HB → seconde vague
selon les confirmations. Aucun changement du Rapid 4+1, du barillet de six chambres ni de la cadence réparée de la scie.
