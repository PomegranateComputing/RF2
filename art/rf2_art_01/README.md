# RF2-ART-01 — sources de la candidate

Périmètre : Browning, FAL, RFOrderly, RFBrancardier, RFPorteRegistre, poses terminales, effets de sang et 66 cues audio RF01. Les cartes, collisions, vitesses, dégâts et durées d'animation ne sont pas modifiés par la passe artistique. La correction DamageFunction 9 provient d'Opus 844b50f.

Palette : tissus gris beige et bleu désaturé, acier bleui, cuir brun, peau pâle ; contraste local et usure limitée. Albedo des vêtements plafonné avant éclairage ; aucune modification du gamma ou de la lumière de RF01. Un master articulé par famille, huit angles réels sans miroir. Les matériaux sont attachés aux os durant l'animation.

## Reproduction depuis la racine du dépôt

Python 3 avec Pillow, numpy, scipy, soundfile, scikit-image. Les versions utilisées sont consignées dans requirements-lock.txt. Aucune clé API nécessaire pour réexporter.

```
python art/rf2_art_01/weapons/export_browning.py
python art/rf2_art_01/weapons/fal_legacy_source/build_batch.py
python art/rf2_art_01/enemies/production.py --workers 4
python art/rf2_art_01/enemies/corpses.py --family all
python art/rf2_art_01/audio/produce.py
python art/rf2_art_01/fx.py
```

Le FAL conserve ses 21 images promues du lot Astra. Leur réexport est vérifié identique octet pour octet dans `fal_legacy_source/reexport/`. Son traitement dans cette passe concerne le cadrage commun (échelles 6.8 / 8.16, offset -750 / -460) et le son. Copier les PNG de ce sous-dossier dans `src/graphics/weapons/fal/` si une reconstruction complète est nécessaire. Les propositions historiques de son ancien manifeste ne remplacent pas TEXTURES.weapons ni les timings actuels.

Le Browning possède sept poses issues du même master arrière, plus un flash séparé. Culasse animée par translations rigides et recul bref. Toile commune 1672×941, échelles 6 / 7.2, offset -700 / -300. Le Browning n'a pas de chargeur simulé ni de recharge.

Ennemis : 104 ORDY, 120 BRCD, 96 PREG. PNG avec grAb après recadrage, Scale 0.18. L'export utilise 5 pixels/unité source, une précompensation verticale 1.2 et les huit angles du rig. La hauteur visible debout reste proche de la base (le calcul doit inclure l'étirement du pixel du moteur). PRGS A/B conserve les deux liasses de la base.

Cadavres : sprites de chute puis OBJ uniquement pour ORDY M, BRCD M et PREG K ; même rig, échelle équivalente 0.9 en unités de carte. Le minimum Z du maillage est 0. Le pivot est recentré sur le corps ; le brancard reste indépendant sur ses roues, le porteur tombe à côté. Aucun changement de gravité ou de collision. Un corps rigide ne se conforme pas aux marches et peut traverser le mur ou une marche selon l'endroit de sa mort. Les preuves montrent ces limites. Les PNG terminaux restent disponibles en repli sprite.

Les six OBJ/skins sont conservés dans `enemies/model_exports/`. Après import des sources, `python art/rf2_art_01/install_models.py` les installe sous `src/models/rf2_art_01/`. Ce pas est explicite car l'importeur d'Opus n'autorise pas `src/models/`. MODELDEF est livré dans le patch partagé, à intégrer par Opus. Ne pas placer les OBJ sous sprites : le chargeur de textures les signale alors à tort comme images invalides.

Audio : sources sélectionnées uniquement, masters PCM24 mono 48 kHz, exports PCM16 mono 48 kHz. `audio/audio_manifest.json` donne prises, montages, gains, crêtes, RMS et empreintes. `audio/events.csv` donne les noms logiques et routages SNDINFO. Compression des tirs 5:1, seuil relatif -24.4 dB, attaque immédiate et relâchement 12 ms ; le corps enregistré reprend après le pic, sans écrêtage dur. Aucune longue réverbération cuite ; le moteur conserve ses environnements de pièce. Les tirs sont des enregistrements montés, sans prétendre à une prise exacte du Hi-Power ou du FAL. Aucune audition humaine par l'agent n'est revendiquée.

Les masters générés sont conservés avec leurs prompts exacts dans IMAGEGEN_PROMPTS.md (outil intégré image_gen). L'export est reproductible depuis ces images figées ; une nouvelle génération ne serait pas déterministe. Les images de génération n'ont pas été produites indépendamment pour chaque pose.

Les outils du dossier `review/` servent uniquement aux preuves et au conditionnement. Le patch dev est séparé du patch de production.
