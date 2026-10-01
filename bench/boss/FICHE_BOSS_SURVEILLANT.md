# Boss 1 — le surveillant-chef (fiche de rôle, 01/10/2026)

**Adaptation déclarée.** Le roman ne contient pas de boss. Ce rôle prolonge l'adaptation acceptée de RF01–RF05 : le
personnel de Sainte-Anne continue sa procédure derrière Viktor (« Toujours les mêmes », l. 493). Le surveillant-chef
est en haut de cette hiérarchie : les infirmiers, les brancardiers et les porte-registre lui répondent. Ce n'est ni un
patient, ni une maladie, ni une force occulte, ni une figure non hostile du texte reclassée (le gardien, la jeune
femme, le couple, Elvis, l'homme qui brûle les formulaires restent hors de cause). **Aucun boss dans le chapitre du
Jerma.**

## Ce que le corpus lui donne (matière, pas personnage)

| Motif | Lignes | Ce qu'il en tire |
|---|---|---|
| Le registre ouvert dans le vestibule de Sainte-Anne, les pages tournées par le courant d'air ; « un registre bien tenu valait davantage qu'une promesse » | 15–25 | il porte le registre ; il l'ouvre pour lancer l'attaque des registres |
| « Les procédures exigeaient du calme de ceux qu'elles suspendaient au-dessus du vide. Veuillez patienter. » | 577 | sa menace est la procédure : il annonce, il marque, il appelle |
| Les porte-registre, les brancardiers, les infirmiers de l'adaptation | RF01–RF05 | il les appelle au sifflet |
| Tampons, cachets, colonnes, observations | 467–487, 2887 | le tampon de laiton, encré avant de frapper |

## Où il peut apparaître (propositions, à décider par le propriétaire)

1. **Fin de RF01, la sortie de Sainte-Anne** : la loge des portiers et son vestibule (là où la procédure garde la
   porte). Le banc reproduit cette salle.
2. **Fin de RF05, le parc rallumé** : devant la porte de service, quand le personnel « tient le parc ».
Aucune de ces places n'est arrêtée ; le banc ne l'installe dans aucune carte.

## Apparence (à dessiner par Codex : visuel final candidat)

Un homme grand et lourd, la cinquantaine, manteau gris de surveillant jusqu'aux genoux, bande de col blanche,
casquette à visière ; un trousseau de clefs à la ceinture ; le registre relié de toile rouge sombre sous le bras ; un
tampon de laiton à manche de bois ; un sifflet à chaîne. L'usure du service : manches lustrées, encre violette aux
doigts, poches déformées par les clefs. La menace se lit par la carrure, le geste et l'équipement, pas par un costume
agrandi ni un monstre.

## Ce que le jeu attend (prototype du banc, `bench/boss/`)

| État | Lettres et durées (tics) | Lecture |
|---|---|---|
| Repos | `A` 10 | debout, registre sous le bras |
| Marche | `B C D E` 5 chacune | lourde, pas sonores |
| Entrée | marche `B–E` jusqu'au milieu de la salle, puis `H` 20 (ouvre le registre), `F` 14 (encre le tampon), `G` 10 (frappe le registre), `A` 10 | intouchable pendant l'entrée |
| Tampon (près) | `F` 24 (tampon levé, annonce), `G` 6 (frappe au sol : onde de 128 u), `G` 12 | phase 2 : parfois deux frappes |
| Registres (loin) | `H` 18 (ouvre le registre, annonce), `I` 6 (trois registres lancés en éventail), `I` 10 | |
| Sifflet | `J` 30 (siffle, annonce), `J` 6 (deux infirmiers entrent par les portes latérales) | trois fois au plus |
| Phase 2 (moitié de vie) | `K` 20, `A` 10 | la casquette tombe ; plus rapide ; siffle aussitôt |
| Douleur | `K` 6 | |
| Mort | `L` 8, `M` 8, `N` 10, `O` corps au sol (registre à côté) | chute au sol, sans changer de taille |

Figure : 8 vraies rotations par image, `grAb` aux semelles, hauteur debout ~66 u (plus grand que Viktor, 56 ; un
infirmier, 53), même éclairage que RF01. Projectile : le registre ficelé en vol (`BSLG A–C`), l'onde du tampon
(`BSWV A`, additive). Sons : `rf/boss/{stamp, ink, ledger_open, throw, ledger_hit, whistle, whistle_short, pain,
death, step}` (formats de `ROUTAGE_SON_ARMES.md`).

## Banc

`python bench/boss/build_boss_bench.py` construit `dist/boss/RF2_BOSS_ESSAI_<date>/` (module, lanceur `JOUER.cmd`,
`BUILD_INFO.json`) par-dessus une copie figée d'un build du jeu. Carte `BOSS01` : la salle de la loge ; franchir la ligne
d'entrée ouvre ses portes ; barre de vie et annonce de l'attaque à l'écran (aide de banc) ; mort du joueur : écran de
mort du jeu, reprise à la sauvegarde d'entrée ; victoire : reprise automatique (ou Utiliser). Images et sons du banc :
**provisoires** (silhouettes, sons synthétisés).
