# ASTRA — RF01 P0 ENNEMIES

Batch principal : `RF01_P0_ENEMIES`, ou trois batches séparés si plus propre.

But : trois familles ennemies maximum pour RF01, immédiatement différenciables en combat.

## Canon

Inspecte d'abord le legacy et les documents du projet. N'invente pas des noms/lore si le canon ne les donne pas. Utilise des IDs fonctionnels `ENEMY_A/B/C` jusqu'à confirmation.

## Rôles fonctionnels

Prévoir trois rythmes distincts, par exemple :

- menace armée / distance ;
- poursuivant / pression rapprochée ;
- lourd / espace et timing.

Fable décidera le comportement final. Ton travail est la cohérence visuelle et les séquences nécessaires.

## Cohérence obligatoire

Chaque famille vient d'un master unique.

Garder : proportions, vêtements, visage/casque, accessoires, palette, hauteur, éclairage et caméra.

Ne génère pas chaque rotation séparément sans source commune.

## Sorties suggérées

Pour sprites : rotations 8 directions lorsque nécessaires ; idle/walk/attack/pain/death suffisants pour prototype de qualité.

Exporter PNG RGBA avec baseline/feet constante.

Ajouter une planche d'échelle : ennemi à distances courte/moyenne/longue avec repère de taille.

Si modèle 3D : conserver source + renders runtime ou GLB/FBX selon décision, mais ne suppose pas que Fable choisira automatiquement le modèle plutôt que sprites.

Manifest : target sous `sprites/enemies/<id>/` ou `models/enemies/<id>/` selon sortie.
