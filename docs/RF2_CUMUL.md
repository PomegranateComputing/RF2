# RF2 — candidate cumulée (tout en un)

**Statut : RUNTIME_VERIFIED_OWNER_REVIEW_REQUIRED.** Demandée par le propriétaire le 29/09 : un build avec toutes les
améliorations. Rien ici ne vaut accord du propriétaire. Le build RF01 accepté (`JOUER_RF2_ART_REVIEW.cmd`,
`04bdd0ae…`) et toutes les candidates précédentes restent inchangés, chacune avec son lanceur.

## Jouer

| Commande | Contenu |
|---|---|
| `JOUER_RF2_CUMUL.cmd` | écran titre ; « Nouvelle partie » : RF01 puis RF02 |
| `JOUER_RF2_CUMUL_RF02.cmd` | RF02 directement (difficulté Service, équipement de départ du chapitre) |

Build `dist\candidates\RF2_CUMUL_20260929_1801\RF2_CUMUL.pk3`, sha256
`5115307cd01b0c3ff98d81095a917fc930da316dcf20f75efa48432be278c684`, commit `70e3ccd`, branche `candidate/rf2-cumul`.
Configuration `user\uzdoom_cumul.ini` (copie de `user\uzdoom.ini`, qui n'est pas modifié), sauvegardes
`user\savegames_cumul`.

## Ce qu'il contient

| Amélioration | Lot | D'où |
|---|---|---|
| Ennemis de RF01 retouchés (visuel seulement) | RF2-ART-02 | ligne de production |
| Menus, mort et reprise, sons d'interface | RF2-UI-01 | ligne de production |
| Plaques de RF01 sur leur mur, lisibles | RF01-PAN | ligne de production |
| Portrait de Viktor en six états | HUD-02 | ligne de production |
| RF02 complet : carte, scènes, vagues, lot HD d'Astra, figures F02-01…08, poussette, tram sur rails, enseignes, V01–V10 | RF2-MAP-02, RF02-A/B/C | ligne de production |
| Pied-de-biche | COMBAT-02 | ligne de production |
| Matières « Sainte-Anne 1940 » de RF01, soubassements distincts, 8 px/u pour six matières | RF01-TEXTURES-1940 | candidate 1606 |

Ce qu'il ne contient pas :

- **Les armes du banc** (Rapid, MR73, FAMAS, Scorpion) : le mandat du 29/09 exclut toute activation en campagne à
  cette étape ; elles restent sur `JOUER_RF2_ARSENAL_ESSAI.cmd`.
- Les nouveaux décals d'usure d'Astra (retenus, trop discrets) : les décals d'origine restent.

## Construction

Branche prise sur `prod/rf2-campaign` (`3d04084`), fusion de `candidate/rf01-textures-1940` (`fadb3d8`). Le fichier
binaire `maps/RF01.wad` n'est pris d'aucun côté : il est régénéré par le générateur fusionné. Son TEXTMAP est
exactement celui de la ligne de production (plaques RF01-PAN comprises) avec les 1570 noms de la table 1940
remplacés ; seuls restent les 12 noms conservés exprès (ciel, vitrail, 10 plaques). Contenu du pk3 comparé à la ligne
de production : 41 fichiers ajoutés (le lot de textures), 3 modifiés (`ANIMDEFS`, `RF01.wad`, `world.zs`), aucun
retiré ; RF02 identique. Contrôle statique de RF01 inchangé (7523 cellules, clés 1 et 2, sortie atteinte) ;
`check_runtime` PASS.

## Vérification dans le moteur

| Contrôle | Résultat |
|---|---|
| Traversée RF01 A (nouvelle partie → sortie vers RF02) | PASS : 56 points, 16 morts d'ennemis relevées, objectifs 1, 3, 4, 5, 6, 9 |
| Traversée RF01 B (sauvegarde, mort, reprise, chargements) | PASS : 1 mort, 1 reprise, 2 chargements |
| Traversée RF02 A (départ direct → sortie) | PASS : 54 points, 17 morts d'ennemis relevées, objectifs 1 à 8 |
| Traversée RF02 B | PASS : 1 mort, 1 reprise, 2 chargements |
| Mêmes 13 cadrages matières et zones que la candidate 1606 (1920×1080) | matières 1940 identiques ; seuls écarts : le portrait de Viktor (HUD-02), la plaque LINGERIE (RF01-PAN), le corps au sol retouché (ART-02), un frottement d'origine |
| Les 13 plaques de RF01, de face | toutes sur leur mur, lisibles, sur les matières 1940 |
| Les 17 décals de RF01, face au mur marqué | décals d'origine présents, sur les soubassements 1940 |
| Lanceurs depuis `C:\` (`-norun`) | les trois chargent ce build, scripts compilés sans erreur |

Chaque capture porte le tic de jeu qu'elle montre (60/60 vérifiées). Preuves : `evidence\` de la candidate
(`planches\`, `captures\`, `e2e\`, `mesures_comparaison_1606.txt`, `PROVENANCE.txt`).

## Limites

- Aucun son écouté par Opus ; jugé sur contrôles et traversées automatiques, pas en partie longue.
- La ligne de production n'avait plus de build exporté depuis HUD-02 (27/09, 22 h 30) : ce build est le premier à
  contenir RF01-PAN porté, RF02-A/B/C et le pied-de-biche ensemble.
- La passe de textures RF01 reste une candidate : si le propriétaire la refuse, la ligne de production n'a pas bougé.
