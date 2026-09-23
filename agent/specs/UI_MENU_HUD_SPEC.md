# UI / menus / HUD

## Principe

Utiliser les fonctions solides d'UZDoom, personnaliser la présentation et la hiérarchie. Ne pas réimplémenter une page de réglages système juste pour obtenir un bouton plus rouge.

## Menu principal

- Nouvelle partie
- Charger
- Options
- Crédits
- Quitter

`Continuer` uniquement si une logique robuste choisit une sauvegarde valide.

## Pause

- Reprendre
- Sauvegarder
- Charger
- Options
- Menu principal
- Quitter

## Options

Réutiliser autant que possible les sous-menus natifs :

- affichage ;
- résolution/mode fenêtre ;
- audio ;
- souris ;
- touches ;
- manette si le runtime la prend en charge ;
- accessibilité disponible nativement si pertinente.

Les réglages doivent survivre au redémarrage.

## HUD

Afficher uniquement des informations vraies :

- santé ;
- armure si utilisée ;
- munition du modèle réel de l'arme ;
- clés/objets réellement nécessaires ;
- crosshair ;
- objectif bref si le jeu en emploie un.

Pas de compteur de chargeur si le gameplay ne simule pas encore les chargeurs.

## DA

- noir / anthracite / acier / bordeaux profond selon validation visuelle ;
- matière physique légère, pas dashboard SaaS ;
- typographie lisible ;
- pas de texte généré dans une image ;
- boutons et focus visibles à la souris, clavier et manette si disponible ;
- résolution 1080p / 1440p / 4K sans cassure.

## Parcours d'acceptation UI

Menu -> options -> nouvelle partie -> pause -> sauvegarder -> menu -> charger -> mourir -> reprendre -> finir niveau -> menu -> quitter -> relancer -> vérifier les réglages.
