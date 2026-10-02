# Reprise du 02 octobre — périmètres 1 et 2

Après l'[audit de préservation](PRESERVATION.md), le propriétaire a demandé les deux périmètres.
Un pilote isolé réemploie les cadrans et matières existants, corrige les plaques de libellés,
dessine huit variantes de trumeaux et propose des volumes RF04/RF05/RF06.

Livraison et instructions : [RF2_UZDOOM_CODEX_ART_20261002_PRESERVATION](C:/PROJECTS/RF2_UZDOOM_CODEX_ART_20261002_PRESERVATION/POUR_OPUS.md).
Candidate : [RF2_PRESERVATION_PILOTE_20261002_V04.pk3](C:/PROJECTS/RF2_UZDOOM_CODEX_ART_20261002_PRESERVATION/candidate/RF2_PRESERVATION_PILOTE_20261002_V04.pk3).
Comparaison manuelle : [pilote RF04](C:/PROJECTS/RF2_UZDOOM_CODEX_ART_20261002_PRESERVATION/JOUER_PILOTE_RF04.cmd),
[RF05](C:/PROJECTS/RF2_UZDOOM_CODEX_ART_20261002_PRESERVATION/JOUER_PILOTE_RF05.cmd), [RF06](C:/PROJECTS/RF2_UZDOOM_CODEX_ART_20261002_PRESERVATION/JOUER_PILOTE_RF06.cmd).

16 vues finales conservées : RF04 (3), RF05 (3), RF06 (4), cadrans (2 états x 3 distances). Trois détails RF04 sont également comparés à caméra identique (trumeaux et charpente).

Parcours A et B réussis sur RF04, RF05 et RF06 (sauvegarde, fermeture, recharge, sortie ; mort/reprise sur RF04 et RF05).

| Carte | Parcours A | Parcours B | Code de retour |
|---|---|---|---|
| RF04 | PASS | PASS | 0 |
| RF05 | PASS | PASS | 0 |
| RF06 | PASS | PASS | 0 |


Conservation et limites : [empreintes et dry-runs](C:/PROJECTS/RF2_UZDOOM_CODEX_ART_20261002_PRESERVATION/evidence/INVARIANTS.json).
Fonctionnement : [rapports des parcours](C:/PROJECTS/RF2_UZDOOM_CODEX_ART_20261002_PRESERVATION/evidence/parcours/RESULTATS.json).
RF01/RF02, armes, sons, HUD et acteurs/code restent identiques à la base PORTES 1018 dans ce pilote.
L'ensemble de la refonte et les retouches sonores restent ouverts. Aucune acceptation artistique n'est présumée.

Opus modifie actuellement les générateurs de production ; les propositions de ce lot sont fondées sur la
base sauvegardée et doivent être rapprochées de ses changements, sans remplacement global.
Cette session n'a importé aucun fichier dans `src/`, modifié aucun générateur de production ni repointé les lanceurs.
