# RF2_MAP_02 — première livraison de reprise

**OWNER_REVIEW_REQUIRED. Lot partiel ; RF02 n'est pas terminé.** Travail isolé sous `incoming/astra/` du worktree Astra. Référence Opus : `bc563206a52c4da129fffcaaf8248f25ed3c34a4` ; PK3 RF2-MAP-02 du 27/09 à 15:43, SHA-256 `11167ce28e37d07e84914435cc561d50d222e09824c142424c12c98c8778b7c1`.

## Ce qui est livré

* **11 remplacements de compatibilité** dans `runtime/` : quatre façades, vitrine TSF et apparition Amiga, seau, sacoche, téléphone, radio éteinte/allumée. Dimensions et grAb de la base conservés ; chaque cible et empreinte figure dans `manifest.json`. Les cinq sprites restent des billboards : ils ne constituent pas une présentation contournable achevée.
* **Présentation HD proposée**, séparée : six textures à leur définition native, cinq sprites à canevas ×4, grAb ×4 et échelle acteur ÷4. `presentation_proposal/manifest.json`, `dimensions.json`, `patch_bases.json` et `presentation.diff` forment un ensemble à importer conjointement. Les tailles du monde restent celles de la base. Aucun changement de dégâts ou de timings. Le patch a été contrôlé avec `git apply --check`, jamais appliqué au dépôt actif.
* **Masters 3D** : poussette, seau, sacoche, radio dans deux états, téléphone, valise ouverte, matelas, ensemble Amiga, tram et module de voie. Scripts Blender, BLEND avec atlas embarqué, GLB et OBJ de travail ; huit vues par master/état, plus intérieur du tram. Les OBJ utilisant des matériaux unis distincts de l'atlas ne sont pas tous prêts pour un skin UZDoom unique : conserver le GLB/BLEND comme source complète. La poussette, entièrement dans l'atlas, est effectivement testée en OBJ dans UZDoom.
* **19 propositions audio** dans `audio_proposal/` : trois Browning, trois FAL, neuf impacts de mêlée par matériau, trois mouvements de mêlée, un grincement de caisse de tram. WAV PCM24 mono 48 kHz, sources sélectionnées et crédits archivés. Pas de musique, voix ou imitation vocale ajoutée. Mesures effectuées ; **aucune audition par l'agent** et aucun changement des sons du jeu actif.
* **Elvis** : master d'après la photo fournie et préparation de scènes dans le lot frère `RF2_ELVIS_01`. Accord déclaré par le propriétaire consigné ; acteur animé non produit.

## Contrôle réel

`evidence/index.html` contient les comparaisons de dix caméras dans RF02 : référence, remplacements à la résolution historique et proposition HD. Ces vues montrent aussi l'apparition de l'Amiga à distance puis son retrait à l'approche. Les cinq vues de la poussette sont capturées dans UZDoom, à un emplacement d'essai ; le bloc de poussette de la carte n'a pas été remplacé.

Paquet de compatibilité : exactement 11 entrées changées, 1437 entrées identiques dont toutes les cartes, armes, scripts et sons. La revue HD change en plus uniquement les dimensions/échelles de présentation prévues dans les deux fichiers du patch. La revue poussette ajoute uniquement son acteur/modèle d'essai. Les builds de revue sont locaux sous `review/`, exclus de l'archive d'assets.

Ces contrôles ne valent pas parcours complet, contrôle de collision de la future poussette/tram, scène complète, audition ou approbation du propriétaire. La radio allumée garde le flag `Bright` existant : toute correction de cet éclairage relève de la présentation à raccorder par Opus.

## Limites et suite

Le tram comporte châssis, deux essieux, roues/boudins, plates-formes et marches, commandes, banquettes, douze valises, cage, perche abaissée et toit ; la voie droite possède rail, gorge et traverses. Il manque les deux poules et le vieil homme. Son gabarit et son plancher diffèrent du bloc actuel : `source/models/tram_contract_proposal.json` expose le raccord nécessaire. Aucune compatibilité de collision n'est revendiquée.

La valise reste **hors runtime** : formes des chaussures insuffisantes. Les huit figures RF02, le pied-de-biche visuel et ses séquences, l'entrée monumentale/abords Luna Park et les autres besoins du dossier absent restent à produire. Les ambiances/voix demandées ne sont pas couvertes par le seul grincement de tram. Aucun début du niveau suivant n'est annoncé.

Le dossier `RF2_CORRECTIONS_ET_SUITE_20260927`, documents 00–05, demande initiale et dix captures, n'a pas été trouvé aux emplacements inspectés. L'ancien pack `RF2_PRODUCTION_20260927` a été retrouvé mais ne le remplace pas. Demande de chemin envoyée au propriétaire dans la conversation. Les contrats techniques manquants sont détaillés dans `DEMANDE_CONTRATS_OPUS.md` ; ce fichier local n'a pas été envoyé automatiquement à une autre session.

## Reproduire

Python 3.12 ; Blender 5.2.2 LTS. Versions Python figées dans `source/requirements-lock.txt`.

```text
blender --background --python incoming/astra/RF2_MAP_02/source/build_props.py
blender --background --python incoming/astra/RF2_MAP_02/source/build_tram.py
python incoming/astra/RF2_MAP_02/source/export_images.py
python incoming/astra/RF2_MAP_02/source/build_audio.py
python incoming/astra/RF2_MAP_02/source/review_engine.py
python incoming/astra/RF2_MAP_02/source/review_presentation.py
python incoming/astra/RF2_MAP_02/source/finalize_delivery.py
python scripts/validate_astra_batch.py incoming/astra/RF2_MAP_02
```

La génération d'images n'est pas déterministe ; les masters retenus, références et prompts sont archivés. Les exports techniques se reproduisent depuis ces masters. La revue moteur utilise la candidate Opus figée et le runner existant, avec configuration/sauvegardes locales au lot. Elle n'écrit jamais dans le jeu actif.
