# Opus — reprise RF02 du 28 septembre

Le dossier propriétaire de corrections est maintenant retrouvé et archivé dans `source/contract/corrections`. Ce lot complète `RF2_MAP_02` (façades/props/audio) et `RF2_ELVIS_01` (master et scènes sourcées). **Aucun import dans le dépôt actif.**

Ouvrir [la galerie](evidence/index.html), puis prendre les fichiers explicitement listés par `manifest.json` et ses `model_files`. Ce sont de **nouveaux noms**, pas des remplacements automatiques des figures existantes. Vérifier les consommateurs sur le HEAD courant, désormais RF01-PAN, et intégrer dans la prochaine candidate RF02.

## Propositions de présentation

- `figure_actors.zs.txt` : 11 classes visuelles, états nommés Burn/Walk/Idle/Sleep/Awake quand disponibles. Aucun civil hostile ou interactif créé. Viktor a `ONLYVISIBLEINMIRRORS`. Hauteurs, échelles et ancres dans `figures.json`.
- `TEXTURES.crowbar.txt` : cinq images d’arme et repli de l’objet au sol ; importer avec leurs échelles/offsets.
- `crowbar_actor.zs.txt` : template de présentation sans dépendance au banc de revue ; les états ne produisent **aucun dégât**. Raccorder à l’arme de mêlée, sa sélection, ses interruptions, le coup réel et les sons d’impact.
- `MODELDEF.crowbar.txt` + `crowbar_world.zs.txt` + OBJ/atlas : objet contournable de présentation. Remplacer sa classe purement visuelle par le pickup voulu lors de l’intégration.
- `SNDINFO.crowbar.txt` : alias proposé ; copier `RF2_MAP_02/audio_proposal/RF2_MELEE_SWING_01.wav` vers `sounds/astra/crowbar/swing.wav`. Les crédits et variations/impacts sont dans le premier lot. Le présent manifeste ne prétend pas livrer un nouveau son.

Ne pas importer `source/review_only.zs`, le handler RFArtReview ou `crowbar_presentation_review.zs.txt` : ils servent aux captures locales. La classe ViktorDebug visible hors miroir appartient exclusivement à ce banc.

## Réserves à conserver

Marche proposée, pas de trajectoire poussette correspondante ; contacts mains/poignée à finaliser. Assise du vieil homme dépend de la banquette définitive. Groupe Santé composé de quatre acteurs séparés ; mère/enfant à raccorder. La valise Sainte-Anne et le geste complet de lâcher des papiers restent à compléter. Le garçon n’a qu’un état : deux essais supplémentaires ont échoué dans l’outil image.

La revue moteur a contrôlé 88 vues fixes, 24 vues d’états, cinq poses d’arme, trois séquences de mouvement et huit angles du modèle au sol. Les empreintes des paquets sont jointes à chaque série. Cela ne valide ni campagne, ni combat, ni scène complète. L’enregistrement audio est prêt à écouter mais non écouté par Astra.

[Archive vérifiée](delivery/RF2_FIGURES_CROWBAR_20260928.zip) · [contrôles](evidence/validation.json) · [contrats encore nécessaires](CONTRATS_OPUS.md).

Cette passation est un fichier local ; aucun message automatique n’a été envoyé à une autre session.
