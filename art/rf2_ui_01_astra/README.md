# RF2-UI-01 — ressources artistiques candidates

Fond issu de la cour RF01 et huit sons UI issus de prises CC0. Statut **OWNER_REVIEW_REQUIRED**. Contrat Opus conservé dans `source/contract/CONTRAT.md`.

## Import

Importer les **10 fichiers de runtime/** selon `manifest.json` : le même fond en `graphics/ui/RFMENUBG.png` et `graphics/TITLEPIC.png`, puis `sounds/ui/{cursor,choose,change,backup,clear,invalid,prompt,dismiss}.wav`. Les noms correspondent au contrat courant ; **aucun patch de code, de menu ou de SNDINFO n'est nécessaire**.

La base d'intégration est une photographie des sources Opus à HEAD `8d0ff8b`, avec modifications en cours listées et hashées dans `evidence/opus_snapshot.json`. Vérifier les `base_sha256` du manifeste avant import ; une divergence appelle une comparaison, jamais un écrasement automatique.

`patches/RF2_UI_01.patch`, `patches/files/` et `source/style_study/` sont une étude historique sur `5b53d9e`, **hors import** dans les menus actuels. Les polices et éléments géométriques restent disponibles comme sources facultatives. La direction finale et les fonctions des menus sont celles d'Opus.

## Sources et reproduction

À la racine du worktree : `python incoming/astra/RF2_UI_01/source/export.py`. Versions dans `source/requirements-lock.txt`. Master image figé et prompt exact conservés ; génération par l'outil intégré image_gen, puis export proportionnel déterministe. Fond RGB 1920×1080 sans texte peint. Le runtime Opus assure le texte, le recadrage et le dégradé de lisibilité.

Marches, grille et façades RF01 ; charbon, pierre froide et bleu de service. Accents bordeaux dans l'interface. Étude facultative : Inter OFL 1.1, titre 23 unités/menu 12 unités, exports ×4, marges et états dans les SVG et la proposition historique. Les polices courantes d'Opus sont conservées dans les preuves finales.

Audio : mono PCM16 48 kHz, masters PCM24, 65–220 ms, crêtes −27 à −20 dBFS. `evidence/audio_metrics.json` donne la correspondance événement/source. Kenney, RPG Audio, CC0 ; licence et huit prises originales jointes. Aucune audition de l'agent ; la galerie permet l'écoute des fichiers livrés. Pas de nouvelle musique.

## Preuves et limites

`evidence/index.html` : captures moteur du titre, difficulté, chargement, options, crédits, sortie, pause, sauvegarde et retour au titre à 1920×1080. Les anciennes vues de sauvegarde/chargement sont étiquetées comme étude historique. Cette étude a également été capturée à 2560×1440 ; elle ne prouve pas la mise en page des nouveaux menus dans cette résolution.

`evidence/validation.json` vérifie les dix cibles, formats, gains et bords des WAV, égalité des deux fonds, hash du paquet testé et absence de modification des autres ressources. Les menus sont ouverts par le scénario de contrôle ; aucun test de saisie/sauvegarde/reprise, navigation clavier/manette, 4K ou 21:9 n'est revendiqué. Opus reste responsable de l'intégration et de ces tests.

Le complément `06_CANON_OBJETS_ET_SCENES.md` est pris en compte dans le lot frère `RF2_CANON_01`. Ce lot UI ne représente ni ne valide CAN-001 à CAN-004. Le fond RF01 n'anticipe aucune révélation du couple ni des objets du Jerma.

`review/` contient les builds et fichiers locaux de test ; ce dossier est exclu de l'archive d'import.
