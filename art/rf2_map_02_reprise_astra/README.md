# RF02 — Figures et pied-de-biche, reprise du 28 septembre 2026

**OWNER_REVIEW_REQUIRED. Présentation contrôlée en moteur ; scènes et combat non intégrés. RF02 reste en cours.**

Travail isolé dans le worktree Astra, sous `incoming/astra/RF2_MAP_02_REPRISE`. Le dossier de corrections indiqué par le propriétaire a été retrouvé à `C:/PROJECTS/RF2_CORRECTIONS_ET_SUITE_20260927` : ses 19 fichiers, documents et captures sont archivés et leurs empreintes contrôlées. La mention « dossier manquant » de la livraison précédente décrit sa situation au 27 septembre et est désormais levée.

## Contenu

| Famille | Exports | État de la proposition |
|---|---:|---|
| F02-01 — homme aux papiers | 3 poses × 8 rotations | Papiers tenus/abaissés ; lâcher et feuilles au feu à raccorder |
| F02-02 — femme à la poussette | 4 poses × 8 rotations | Boucle raster proposée ; alternance des appuis et raccord des mains à affiner |
| F02-03 — groupe de la Santé | 4 personnes × 8 rotations | Panier, couverture/parapluie fermé, mère et enfant séparés ; composition de scène à faire |
| F02-04 — vieil homme du tram | 2 poses × 8 rotations | Assoupi/éveillé ; contact banquette et canne à vérifier |
| F02-05 — garçon à la TSF | 1 pose × 8 rotations | Accroupi avec outil/composants ; second état non produit |
| F02-06 — femme de Cochin | 1 pose × 8 rotations | Blouse/coiffe blanches, enveloppe |
| F02-07 — jeune femme de Sainte-Anne | 1 pose × 8 rotations | Robe claire, bracelet ; valise séparée encore à finir |
| F02-08 — Viktor | 1 pose × 8 rotations | Master facial accepté en référence, sweat noir, légère barbe ; miroirs seulement |
| COMBAT-02 — pied-de-biche | 5 poses HD + modèle 3D et repli sprite | Bras/manche noire ; repos, préparation, frappe, prolongement, retour ; objet au sol contournable |

Total : **136 sprites de figures, cinq images d’arme et un sprite de repli**, plus OBJ/atlas du modèle au sol. Les 11 acteurs représentent les huit familles, le groupe de la Santé étant composé de quatre personnes.

Sprites de figures : RGBA 512 × 448, grAb `(256,424)`, échelle proposée `0.18`. L’étalonnage des hauteurs varie de 36 à 68 unités selon la posture. Le facteur horizontal 1,2 compense l’aspect pixel du moteur. Chaque rotation conserve la calibration de son état initial : une personne qui se penche n’est pas artificiellement remise à la hauteur debout.

Arme : cinq PNG RGBA 1536 × 1024 ; TEXTURES avec XScale 6,8 / YScale 8,16 et offset −750, −460. Séquence de revue B5/C2/D3/E5/A3 tics, à raccorder au contrat de combat d’Opus. Modèle au sol : environ 24,58 × 1,28 × 4,38 unités ; OBJ Y-up, MODELDEF Scale 1/1/1,2 + CorrectPixelStretch. L’aspect brillant des arêtes provient de l’atlas, sans éclairage forcé.

## Contrôles et consultation

[Galerie hors ligne](evidence/index.html) : 88 vues de figures, états interactifs, cinq poses de l’arme, clip muet de trois séquences et huit vues du modèle au sol. Les 24 captures de mouvements de figures sont aussi livrées. La télémétrie confirme les états A/B/C, A/B/C/D et A/B ; les 68 captures du clip parcourent les cinq poses de l’arme.

Base figée : candidate RF02 issue du commit `bc563206a52c4da129fffcaaf8248f25ed3c34a4`, revue HD antérieure SHA `696b020c596cdb498bc59e25284b3eba73fe7b660171e5da3a2ab93c427d870d`. Le dépôt actif est passé à `candidate/rf01-pan` pendant la pause ; aucun retour forcé ni import dans cette branche. Toutes les cartes du paquet de référence sont conservées à l’identique.

Les paquets locaux sous `review/` ajoutent uniquement les acteurs, ressources et dispositifs de revue. Les captures consignent le SHA de leur paquet. La correction ultérieure du déclencheur d’attaque ne change pas les sprites de figures ; la dernière reprise des UV du modèle au sol est contrôlée dans sa propre série. Les captures sont des essais scriptés avec déplacements de caméra, pas un parcours de campagne.

Le clip déclenche l’état Fire de la présentation directement : il ne valide pas une commande joueur, une collision ou des dégâts. Le son de mouvement vient du premier lot, avec sa provenance conservée. La sortie OpenAL complète est fournie dans `evidence/crowbar_engine_mix.wav`, avec en-tête finalisé pour lecture : **produit/enregistré, écoute non effectuée**. Elle n’est pas synchronisée au clip muet.

## Limites précises

Les silhouettes raster ne sont pas un rig 3D ; les changements de vêtement/pose entre états restent visibles, surtout dans la marche. Une revue isolée ne valide pas les appuis en mouvement, l’assise, les mains sur une poignée ou la main de l’enfant. Le second état du garçon et une remise en page ont échoué deux fois dans l’outil d’image ; les prompts sont conservés, sans image de remplacement ni faux état dupliqué.

La jeune femme n’a pas encore sa valise finalisée. L’homme aux papiers n’a pas encore de feuilles détachées dans une scène de combustion. Le tram, ses poules, les autres objets et matériaux restants, l’entrée Luna Park, les voix/ambiances et les scènes d’Elvis ne sont pas achevés par ce lot. Le master d’Elvis et l’accord propriétaire restent dans `../RF2_ELVIS_01`, sans nouvelle demande de consentement.

## Remise et reproduction

[Passation Opus](POUR_OPUS.md), [raccords techniques](CONTRATS_OPUS.md), [provenance](SOURCES.md), `manifest.json`, `presentation_proposal/` et `SHA256SUMS.txt` accompagnent les sources. L’archive `delivery/RF2_FIGURES_CROWBAR_20260928.zip` exclut PK3, profils privés, sauvegardes et caches.

```text
blender --background --python incoming/astra/RF2_MAP_02_REPRISE/source/build_crowbar.py
python incoming/astra/RF2_MAP_02_REPRISE/source/export_figures.py
python incoming/astra/RF2_MAP_02_REPRISE/source/review_figures.py build
python incoming/astra/RF2_MAP_02_REPRISE/source/review_figures.py 1 figures
python incoming/astra/RF2_MAP_02_REPRISE/source/review_figures.py 2 figure_motion
python incoming/astra/RF2_MAP_02_REPRISE/source/review_figures.py 3 crowbar_poses
python incoming/astra/RF2_MAP_02_REPRISE/source/review_figures.py 4 crowbar_motion
python incoming/astra/RF2_MAP_02_REPRISE/source/review_figures.py 6 crowbar_world
python incoming/astra/RF2_MAP_02_REPRISE/source/finalize_delivery.py
python scripts/validate_astra_batch.py incoming/astra/RF2_MAP_02_REPRISE
python incoming/astra/RF2_MAP_02_REPRISE/source/finalize_delivery.py archive
```

Python et bibliothèques dans `source/tool_versions.json`, Blender 5.2.2 LTS, UZDoom 5.0.1. Les masters retenus et prompts permettent de reproduire les exports techniques ; la génération d’images n’est pas déterministe.
