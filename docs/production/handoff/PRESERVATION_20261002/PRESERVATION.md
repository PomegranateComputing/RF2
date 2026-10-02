# RF2 Préservation et reprise des éléments existants

Consigne directe du propriétaire du 02 octobre 2026, destinée à Astra et Opus : **préserver ce qui est déjà valable**,
examiner l'existant avant toute reprise et distinguer ce qui doit être conservé, amélioré localement ou remplacé.
Les refontes doivent apporter un gain visible sans perdre les qualités acquises. Cette consigne maintient les reprises
profondes du Luna Park, de RF05 et de RF06.

## Base examinée et portée des sources

Audit du dépôt à `61d9b43100bf071022f705e4bf10d82a3d660392`, branche `prod/rf2-campaign`, initialement sans modification
locale. Les deux documents du pack artistique ont été lus comme contexte et prescriptions de production ; leurs
ordres de lancement ne constituent pas une nouvelle demande de lancer tous les lots dans cette session.

Le pack se fonde sur le cumul du 30/09 à 18 h 21. Le dépôt actuel contient des améliorations ultérieures :

| Référence | Usage | Vérification du 02 octobre |
|---|---|---|
| `RF2_ART_REVIEW_20260926_1451` | RF01 accepté, référence à préserver | SHA-256 conforme au rapport |
| `RF2_CUMUL_20260930_1821` | Version jouée par le propriétaire, base du pack | SHA-256 conforme au rapport |
| `RF2_CUMUL_20261001_1605` | Candidate chargée par les lanceurs CUMUL, comparaison antérieure | SHA-256 conforme au rapport |
| `RF2_PORTES_20261002_1018` | Candidate de revue des portes et des derniers lots | SHA-256 conforme ; les 1 865 fichiers de `src/` y sont identiques |

Les 21 images du FAL et les 8 images du Browning actuels sont identiques à leurs fichiers dans le build RF01 accepté.
Les 5 images du pied-de-biche sont identiques à celles du cumul 1821 ; cette arme est postérieure à la référence 1451.
Les empreintes actuelles correspondent aussi aux imports ORDY E V04 (8 fichiers), BRCD V02 (120), PREG V02 (97),
chaussure V02 (1), cadrans V02 (2) et sols RF06 (2). Détails : [contrôles](CONTROLES.json).

## Tri avant reprise

Les décisions ci-dessous sont des recommandations de conservation et de reprise. Elles ne valent pas acceptation
artistique de nouvelles candidates par le propriétaire.

| Élément | Décision | Base à réemployer et intervention justifiée |
|---|---|---|
| RF01 | Conserver ; retouches locales | Parcours, rencontres, architecture et direction appréciés. Garder les matières 1940 et finitions réussies. L'auréole d'humidité V05 reste un défaut local signalé ; ne pas assombrir ou reconstruire toute la carte pour la corriger. |
| Armes appréciées | Conserver ; retouches sonores ciblées | FAL, Browning, bras et manche noire actuels. Garder les mécaniques éprouvées. Réemployer les sons réussis ; corriger les tirs ou raccords problématiques après comparaison, en conservant les corrections de timing utiles. |
| Armes du banc | Conserver les meilleurs états ; améliorer les défauts relevés | Repartir des derniers lots et du banc 1607, pas des premières poses. Rapid 4+1, MR73 à six chambres et cadence corrigée de la Scorpion. La boucle sonore de la Scorpion reste ouverte ; les armes du banc restent sur leur banc. |
| Viktor et RF02 | Conserver ; améliorer localement | HUD actuel, reflet `R2F8_V02` à 56 u et variantes de tenue cohérentes. Garder rue, devantures, figures et compositions réussies. Reprendre les accessoires encore frustes de l'audit RF02 depuis leurs maîtres, ainsi que les défauts précis de placement. |
| ORDY | Conserver la base actuelle ; améliorer les défauts résiduels | ORDY V03 avec E V04 déjà importé. La consigne du pack sur E V03 doit être rapprochée de cette correction. Juger le raccord E→B en mouvement avant une nouvelle reprise ; garder états, cadence, ancrage et collision éprouvés. |
| BRCD et PREG | Conserver V02 comme points de départ ; améliorer si nécessaire | Familles déjà importées et contrôlées par Opus. Les captures montrent le drap et les sangles de BRCD, le visage et les bras mieux dégagés de PREG. Garder les silhouettes, gestes et corps convaincants ; approfondir seulement les défauts constatés aux différentes distances et en animation. |
| Luna Park RF04 et RF05 | Reprise profonde avec réemploi | Garder l'implantation commune, les circulations utiles et la séquence narrative. Réemployer le pilote Luna 02, les tréteaux ajourés, la balustrade, le bassin, les façades et l'arche Brooklyn V02 réussis. Reconstruire les éléments encore insuffisants : attractions, coulisses, accessoires provisoires, raccords et trumeaux forains dessinés. |
| Machines et cadrans RF05 | Conserver les machines ; améliorer localement les cadrans | Garder voûte, marbre, douilles, moteur et phases de roue désormais animées. Les cadrans V02 ont gagné en matière mais perdu la lisibilité de leurs libellés : reprendre les plaques ou lettres sans refaire le panneau entier. Contrôler les états avant et après MARCHE. |
| Chaussure et flaque du bassin | Conserver la chaussure ; reprendre la flaque | La chaussure V02 se lit mieux dans la capture de jeu. Garder ce maître et son placement. Le contour en escalier de la flaque reste à corriger sans perdre le reflet d'eau ni le rôle narratif de l'objet. |
| RF06 | Reprise profonde avec réemploi | Garder les six moments, les explorations latérales, l'éclairage réparé, les meilleurs murs, sols et plafonds. Enrichir complexité spatiale et continuité matérielle sans perdre orientation et lisibilité des inscriptions. RF06 reste sans combat. |
| Jerma et transitions | Réemployer les compositions ; remplacer les provisoires insuffisants | Conserver les gestes d'exploration, Elvis guide, les transitions et leur fonctionnement. Le décor provisoire du Jerma demande une production artistique ; recontrôler la planche RF06→RF07 après cette reprise. Tout le Jerma reste sans combat. |

## Preuves examinées et limites

Lecture des rapports d'import et de revue d'Opus, puis examen visuel des comparatifs capturés dans UZDoom :

- [BRCD face et profil à trois distances](../RF2_20261001/RETOURS_CODEX/LOTS_20261002/brcd_rf04_planche_1.jpg).
- [PREG face et profil à trois distances](../RF2_20261001/RETOURS_CODEX/LOTS_20261002/preg_rf04_planche_1.jpg).
- [Cadrans, chaussure, sols et roue](../RF2_20261001/RETOURS_CODEX/LOTS_20261002/cadrans_chaussure_sols_roue_avant_apres.jpg).
- [Bassin et balustrade du pilote Luna](../../../../build/dev/revue_lots_1001b/rf04_2.jpg).
- [Portes avant et après](../../portes/planches/P1_portes_repetees_en_hauteur.jpg).

Les rapports existants documentent animations, ancrages, collisions et parcours vérifiés par Opus. Cet audit n'a pas
relancé le moteur, visionné les films à vitesse normale ni écouté les sons. Les captures fixes ne suffisent pas à
valider une animation ou le ressenti sonore ; ces points restent à comparer lors de la reprise concernée.

La fidélité précise à une phrase du roman doit être contrôlée dans le DOCX définitif et sa transcription indexée du
pack. Les anciens numéros de ligne EPUB des fiches de production ne sont pas les identifiants `Pxxxxx` du pack.

## Comparaison exigée pour chaque remplacement

Avant une reprise, identifier le fichier maître, la version importée, le build de référence, le défaut précis et les
qualités à conserver. Faire une nouvelle version du lot, avec les empreintes de base ; garder les sources anciennes.

Opus compare l'ancienne et la nouvelle version dans une candidate nommée, aux mêmes caméras, distances et éclairages,
puis en déplacement à vitesse normale. Pour une créature : face, profil, dos à 128/256/512 u, marche, préparation,
attaque, retour, douleur, chute et corps final. Pour un décor : plusieurs angles et le parcours utilisable. Pour les
sons : mêmes actions enregistrées au son natif, écoute comparative, synchronisation et raccords de boucle.

La comparaison doit établir le gain de cohérence artistique, proportions, animation, ambiance et lisibilité ; elle
vérifie aussi collisions, interactions, mécaniques, sauvegardes et transitions selon les éléments modifiés. Une
régression doit être corrigée ou l'élément antérieur réemployé. Aucun remplacement global ne se justifie par la seule
date plus récente d'un lot. Le cas des libellés RF05 illustre ce contrôle à poursuivre.

## Originaux et retour en arrière

Une sauvegarde locale a été créée **avant les modifications documentaires de cette session** :
[ORIGINAUX.zip](../../../../build/preservation/RF2_PRESERVATION_20261002_61d9b431/ORIGINAUX.zip), en lecture seule,
2 248 fichiers. Elle comprend `src/`, scripts, tests, instructions d'agents présentes, documentation, lanceurs,
Markdown racine et copies des deux documents du pack. Chaque fichier archivé a été relu et son SHA-256 vérifié ; les
sources ont aussi été recontrôlées après l'archivage pour détecter un changement concurrent.

SHA-256 de l'archive : `6e5b2297e951607a552f40f8ec753476c8f591ed753417bd3d26bfa7d0e4073d`.
Inventaire complet : [BASE_MANIFEST.json](../../../../build/preservation/RF2_PRESERVATION_20261002_61d9b431/BASE_MANIFEST.json).
Cette sauvegarde est locale dans `build/`, dossier ignoré par Git ; elle n'est pas transportée par un clone du dépôt.

Les builds nommés, le tag RF01 accepté, les maîtres dans `art/` et les livraisons dans `incoming/astra/` et
`C:/PROJECTS/RF2_UZDOOM_CODEX_ART_20261001/` restent conservés à leurs emplacements existants. Ces derniers répertoires
artistiques ne sont pas dupliqués dans l'archive. Pour revenir à un élément, extraire d'abord la sauvegarde dans un
dossier séparé et comparer les empreintes ; Opus réimporte ensuite les fichiers concernés dans une nouvelle candidate.
