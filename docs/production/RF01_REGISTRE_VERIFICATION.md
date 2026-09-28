# RF01 — registre d'admission : vérification réelle (27/09/2026)

Demande du mandat (`02_OPUS_FABLE.md` §E) : essayer réellement l'interaction et la lecture avant de déclarer un
défaut. Le constat antérieur d'illisibilité reposait sur une déduction (le pilote automatique ne l'atteignait pas) ;
il a été retiré.

## Méthode

Build testé : **le build accepté lui-même**, `dist\review\RF2_ART_REVIEW_20260926_1451\RF2_ART_REVIEW.pk3`
(sha256 `04bdd0ae…883544f`), non modifié. Un pk3 de test séparé (`scripts/production/rf01_register_check_pk3.py`)
place le joueur, oriente sa vue et appuie une fois sur « utiliser » depuis la réflexion du joueur, comme une touche
réelle. Contrôles : ouverture de la porte de la chambre de départ, lecture de la note de la chapelle.

Deux premiers essais sont écartés : l'appui injecté depuis `WorldTick` arrivait après le traitement des commandes
du joueur (la porte de contrôle ne s'ouvrait pas non plus). Le troisième passe par la réflexion du joueur.

## Résultat (journal complet : `RF01_REGISTRE_VERIFICATION_journal.txt`)

| Essai | Position (x, y, z, angle) | Résultat |
|---|---|---|
| Contrôle : porte de la chambre | -544, -500, 0, 90 | porte ouverte (ouverture 100 puis 108) |
| Contrôle : note de la chapelle, depuis la nef | -548, 416, 0, 180 | lue |
| Contrôle : note de la chapelle, depuis l'estrade | -566, 390, 16, 110 | lue |
| Registre, face à la table, 23 u | -80, 745, 32, 90 | **lu**, objectif « Atteindre la loge du portier par les consultations. » |
| Registre, contre la table | -80, 752, 32, 90 | **lu** |
| Registre, de biais à droite | -60, 742, 32, 105 | **lu** |
| Registre, de biais à gauche | -104, 744, 32, 72 | **lu** |
| Registre, en retrait | -80, 730, 32, 90 | **lu** |
| Registre de garde sur le comptoir des admissions | 320, -290, 0, 270 | **lu** |

**Conclusion : le registre d'admission du RF01 accepté se lit à la touche d'usage depuis toutes les positions
essayées. Aucun défaut ; rien à corriger.** Les tests de bout en bout ne le montraient pas parce que le pilote
automatique saute cet appui (il croit voir une porte ouverte devant lui) ; c'est une limite du pilote, pas du jeu.
