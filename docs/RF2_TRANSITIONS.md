# RF2 — transitions en planches entre les chapitres

Commande du propriétaire du 01/10/2026 : entre les niveaux, une planche de BD noire des années 1980 avec une légende.
Codex dessine les planches ; le jeu les affiche dans la fin de chapitre existante (`RFDirector`), sans second système
de campagne.

## Ce que voit le joueur

À la ligne de sortie d'un chapitre, l'écran passe au noir, puis la planche apparaît en entier, la première case
éclairée et les suivantes dans l'ombre. **Utiliser** (ou **Tirer**) éclaire la case suivante et ses légendes ; sur la
dernière case, le même appui ferme la planche et ouvre le chapitre suivant. **Maintenir Utiliser** une seconde, ou
**Sauter**, passe la planche entière. La ligne des touches est rappelée sous la planche. Les légendes sont composées
par le jeu (police du jeu, cartouche crème) dans les zones prévues ; l'image ne porte aucun texte.

Sans planche pour une transition (image absente du build), la fin de chapitre reste le texte de sortie d'avant.
RF06 n'a pas encore de suite : sa fin dit « Fin provisoire : le chapitre du Jerma est en préparation. »

## Règles de flux

| Situation | Règle |
|---|---|
| Fin de planche ou passage | le chapitre se termine une fois (`Level.ExitLevel`), l'inventaire voyage une fois |
| Arrivée dans le chapitre suivant | le joueur reste retenu tant qu'une touche (tir, utiliser, sauter, tir secondaire) est enfoncée, puis 2 tics ; 4 s au plus. L'appui qui a fermé la planche ne devient ni un tir ni une utilisation |
| Immobilisation de la fin de chapitre | posée par la fin (gel, invulnérabilité), notée dans un jeton, retirée à l'arrivée (régression 1801/1708 corrigée au commit `413457e`) |
| Sauvegarde faite pendant la planche | le chargement reprend la planche à la case atteinte, puis le chapitre suivant |
| Sauvegarde de départ du chapitre suivant | jouable ; elle peut avoir été prise pendant la retenue d'arrivée : au chargement la retenue finit dès que les touches sont relevées. Elle ne rejoue pas la planche |
| Mort | impossible pendant une planche (la fin de chapitre rend invulnérable) |
| Formats d'écran | l'image entière reste en 16:9 : bandes latérales en 21:9, bandes haute et basse en 4:3 ; textes à taille minimale lisible |

## Données

`src/COMICDEF`, une scène par transition :

```
scene RF01_RF02 RF01 RF02 graphics/comics/RF01_RF02.png
panel 24 24 1180 640                     # x y w h en pixels de la page 1920 x 1080, ordre de lecture
caption 1 $RF_COMIC_RF01_RF02_1 48 48 560 0   # après la case 1 ; clef du fichier LANGUAGE ; zone x y largeur
```

Images : `src/graphics/comics/<ID>.png`, 1920 × 1080, sans texte (masters 3200 × 1800 chez Codex) ; légendes dans
`src/LANGUAGE` (`RF_COMIC_<ID>_<n>`). Les cases et zones de chaque page viennent du `planche.json` du lot de Codex.
Scènes déclarées : RF01_RF02, RF02_RF04, RF04_RF05, RF05_RF06 ; RF06_RF07 quand RF07 existera.

## Contrôles

| Contrôle | Outil | Résultat (build de développement, 01/10, planche d'essai faite de captures, jamais livrée) |
|---|---|---|
| Lecture normale | `scripts/production/comic_flow_probe.py` (mode `read`) | 4 cases une à une, fermeture, RF02, joueur libéré 2 tics après l'arrivée |
| Passage rapide | mode `pass` | Utiliser maintenu : planche passée en 1 s, RF02, libéré au relâchement |
| Tir maintenu à la fermeture | mode `fire`, FAL prêt en main | aucun tir pendant la planche ni à l'arrivée (munitions 20 + 60 inchangées) ; libéré au relâchement (120 tics) |
| Sauvegarde pendant la planche | modes `save` puis `load` | reprise à la case 2, fin de planche, RF02, libéré |
| Sauvegarde de départ de RF02 | mode `load` sur la sauvegarde automatique | prise pendant la retenue ; libéré au relâchement ; pas de planche rejouée |
| 16:9, 21:9, 4:3 | mode `shots` | image entière, sans étirement, bandes noires, légendes entières |
| Chaîne RF01 → RF06 avec chargement | `scripts/production/chain_test.py` | voir le rapport de la candidate |
