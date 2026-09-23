# ASTRA — RF01 P0 FAL

Batch : `RF01_P0_FAL`.

But : set first-person FAL cohérent, immédiatement intégrable dans RF01.

## Références

Inspecte d'abord `legacy/import` pour retrouver l'arme précédente jugée réussie, ses sources, mains, cadrage, offsets ou animation. Ne remplace pas une bonne base pour le plaisir de régénérer.

## Contraintes

- mains pâles ;
- manches noires ;
- silhouette FAL lisible ;
- perspective FPS stable ;
- même master/caméra pour toutes les frames ;
- transparence alpha propre ;
- zéro halo noir autour des manches ;
- pas de marquages fantaisistes ;
- variant exact du FAL non établi -> ne pas inventer des détails spécifiques ;
- flash de bouche séparé si cela facilite l'intégration.

## Set minimum

Produire selon la source disponible :

- ready/idle ;
- fire : montée/recul/retour ;
- reload : séquence cohérente ;
- éventuellement select/deselect ;
- muzzle flash séparé ;
- pickup/world representation seulement si rapide et cohérente.

Le nombre de frames doit suivre l'animation, pas un quota arbitraire.

## Sorties

PNG RGBA à canvas constant dans `runtime/weapons/fal/`.

Conserver source BLEND/PSD/KRA/ORA/etc dans `source/` si utilisée.

Créer dans `evidence/` une planche montrant toutes les frames sur fond clair ET sombre pour détecter les halos.

Manifest avec `target_relpath` proposés sous `sprites/weapons/fal/`.
