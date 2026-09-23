# FABLE 5.1 — RF01 REBUILD

Transforme `src/maps/RF01.wad` de blockout généré en vrai premier niveau de campagne.

## Préservation

Ne modifie jamais `campaign/blockouts_v1/maps/RF01.wad`.

Avant la première modification, capture/consigne : nombre de secteurs/linedefs/things, durée de traversée du blockout si mesurable, captures de 4–6 points représentatifs.

## Lieux à conserver comme langage narratif

Chambre, Admissions, Cour des hommes, Pavillon est, Lingerie, Galerie nord, Registres, Chapelle vide, Consultations, Porche.

Leur position exacte peut changer.

## Reconstruction spatiale

Obligatoire :

- casser le motif « boîte-couloir-boîte » ;
- créer des sous-espaces crédibles ;
- introduire au moins deux changements de niveau/hauteur utiles ;
- ouvrir des vues sur la cour et entre ailes ;
- ajouter circulation de service ou secondaire ;
- créer deux raccourcis/boucles réellement utiles ;
- donner au joueur des repères visuels ;
- utiliser portes/encadrements avec dimensions cohérentes avec le PlayerPawn réel ;
- tester les portes depuis les deux côtés et après save/load.

Utilise slopes/3D floors/portals uniquement lorsqu'ils améliorent réellement le lieu et restent robustes.

## Progression

Ne conserve pas automatiquement la clé bleue du générateur.

Le verrou principal doit avoir une raison contextuelle : accès administratif, alimentation, porte de service, registre, mécanisme, événement ou autre solution cohérente.

La chapelle doit être une vraie branche/respiration/révélation ou raccourci, pas un distributeur de clé.

Le porche doit être une conclusion lisible, pas « pièce la plus au nord = exit ».

## Combats

5–7 rencontres authored max pour la première passe.

Pour chaque rencontre, définis :

- ce que le joueur voit en entrant ;
- menace principale ;
- espace de mouvement ;
- couverture/angles ;
- raison du placement ;
- sortie/transition ;
- ammo/health justifiés.

Pas de six ennemis distribués à des offsets fixes dans chaque salle.

## Art

Utilise les blockout textures seulement jusqu'à disponibilité des lots Astra. Remplace par familles cohérentes, pas texture par texture au hasard.

Les assets héros (FAL, ennemis, UI) doivent être intégrés et observés dans RF01 avant acceptation.

## Performance

Préserve la lisibilité et évite les grands espaces ouverts sans contrôle de visibilité. Mesure les problèmes réels avant d'optimiser.

## Acceptation

RF01 doit passer les critères de `RF01_PRODUCTION_SPEC.md` et `ACCEPTANCE_GATES.md`.
