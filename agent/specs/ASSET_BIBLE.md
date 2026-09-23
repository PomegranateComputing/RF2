# RF2 — Asset Bible

## Direction générale

Le jeu doit paraître construit dans un même monde : sombre, matériel, institutionnel/industriel, usé, précis, étrange sans surcharge fantastique. Les lieux doivent être crédibles avant de devenir impossibles.

Éviter :

- « AI art » générique ;
- micro-détails incohérents ;
- textes illisibles générés dans les textures ;
- bruit/grunge uniforme sur tout ;
- noir utilisé pour masquer une géométrie pauvre ;
- photoréalisme d'une arme face à des ennemis jouets ;
- changements de style entre deux frames d'un même acteur.

## Cohérence de rendu

Pour une famille d'assets, figer :

- source/master ;
- caméra ;
- focale ;
- éclairage ;
- palette ;
- échelle ;
- point d'ancrage ;
- transparence ;
- convention de nommage.

Une animation ou huit rotations doivent provenir du même master, pas de huit générations indépendantes.

## Viktor / armes vues FPS

Référence prioritaire : fichiers approuvés retrouvés dans `legacy/import` s'ils existent.

Contraintes connues :

- mains pâles ;
- manches noires ;
- contour propre ;
- proportions constantes ;
- aucun halo sombre autour des manches ;
- le FAL est l'arme héroïque initiale.

Ne pas inventer un marquage/variant précis du FAL si le legacy ne l'établit pas. Marquer l'incertitude dans le manifeste.

## Ennemis

RF01 : trois familles max au départ.

Chaque famille doit se lire à distance par silhouette, posture et rythme. Les orientations, marches, attaques, douleurs et morts proviennent d'un master cohérent.

## Matériaux

Priorité aux familles réellement visibles dans RF01 : plâtre peint, carrelage, pierre, béton, métal peint, bois, verre, textile, surfaces médicales/institutionnelles, extérieur/cour.

Usure située : poignées, passages, impacts, humidité, rouille, bords. Pas de filtre « sale » universel.

## Audio

Sons propres, dynamiques, sans samples copyrightés non autorisés. Séparer si utile : attaque/mécanique/tail, impact par matériau, boucle d'ambiance, one-shots.

## UI art

Astra produit fonds, plaques, séparateurs, icônes, cadres et éléments non textuels. Le texte final est rendu dans le moteur autant que possible.
