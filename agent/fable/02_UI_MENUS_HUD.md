# FABLE 5.1 — UI / MENUS / HUD

Livrer dans le même milestone que RF01.

Lis `agent/specs/UI_MENU_HUD_SPEC.md`.

## Stratégie

Conserve les fonctions natives solides d'UZDoom pour options, binds, sauvegarde/chargement. Personnalise via MENUDEF et les mécanismes UZDoom appropriés au lieu de reconstruire ces systèmes.

## À implémenter/tester

Menu principal : Nouvelle partie, Charger, Options, Crédits, Quitter.

Pause : Reprendre, Sauvegarder, Charger, Options, Menu principal, Quitter.

HUD : données réellement existantes seulement.

Mort/reprise : fonctionnelle.

Fin RF01 : transition valide vers RF02 ou écran intermédiaire temporaire explicitement documenté, sans erreur fatale.

## Art Astra

Le lot `RF01_P0_UI` ne doit contenir que le shell artistique. Le texte et les fonctions restent contrôlés par le moteur.

## Validation

Tester :

menu -> options -> nouvelle partie -> pause -> sauvegarde -> menu -> charger -> mourir -> reprendre -> finir RF01 -> menu/transition -> quitter -> relancer -> vérifier persistance options.

Tester au minimum en 1920x1080 et 2560x1440 ; 4K si la machine le permet sans rendre le cycle lent.
