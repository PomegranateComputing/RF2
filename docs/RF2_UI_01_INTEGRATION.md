# RF2-UI-01 — menus, mort et reprise (intégration Opus)

**Statut : RUNTIME_VERIFIED_OWNER_REVIEW_REQUIRED.** Candidate du 27/09/2026. Elle n'est pas approuvée tant que le
propriétaire ne l'a pas dit. RF01 reste la référence acceptée ; ce lot ne touche ni la carte, ni les armes, ni les
ennemis, ni les sons de jeu.

## Jouer

- `JOUER_RF2_UI-01.cmd` : build `dist\candidates\RF2_UI-01_20260927_1407\RF2_UI-01.pk3`
  (sha256 `6412032a…15739`), branche `candidate/ui-01`, commit `062639b` = tag `rf01-owner-accepted-20260927` + les
  commits de l'interface. Profil et sauvegardes séparés (`user\uzdoom_ui01.ini`, `user\savegames_ui01`) ; la
  configuration personnelle n'est pas touchée.
- Référence à côté : `JOUER_RF2_ART_REVIEW.cmd` (inchangé).
- Builds précédents conservés : `RF2_UI-01_20260927_1342` (composition de titre d'Opus, avant l'art d'Astra) et
  `RF2_UI-01_20260927_1358` (art d'Astra ; affichait « Player died. » à la mort, corrigé en 1407).

## Contenu

| Écran | Ce qui change |
|---|---|
| Titre | fond d'Astra (cour de RF01, sans texte peint), titre et sous-titre composés par le jeu, « dernière sauvegarde : date » |
| Menu principal | Continuer (charge la sauvegarde la plus récente ; grisé s'il n'y en a pas), Nouvelle partie, Charger, Options, Crédits, Quitter ; souris, clavier, raccourcis |
| Difficulté | Convalescence / Service / Nuit du 14 juin, une ligne d'explication chacune |
| Pause | Reprendre, Sauvegarder, Charger, Options, Menu principal, Quitter ; chapitre, titre du niveau et objectif en cours |
| Charger / Sauvegarder | liste à gauche, vignette et fiche à droite (date, niveau, durée) |
| Options | pages natives dans l'ordre de la spécification, réglages du jeu, menu natif complet en dernier |
| Crédits | Nameless / Pomegranate Interactive, polices et sons crédités |
| Boîtes de confirmation | carte sombre Oui / Non, sans texte anglais du moteur |
| Mort | « Viktor est tombé. », [E] REPRENDRE (dernier point de sauvegarde), [Échap] MENU ; obituaires du moteur traduits |
| Sons d'interface | huit sons courts d'Astra (prises CC0), sous le niveau des sons de jeu |

## Preuves

Dans `dist\candidates\RF2_UI-01_20260927_1407\evidence\` :

- `ui\<résolution>\` : 13 captures moteur par résolution (titre, difficulté, chargement, options, crédits, sortie,
  pause, sauvegarde, retour au titre, mort), en 1920×1080, 2560×1440, 2560×1080 (21:9) et 1440×1080 (4:3).
- `ui\navigation.txt` : une sauvegarde créée par ce build, puis Continuer → RF01 chargé depuis la sauvegarde ;
  Nouvelle partie → Service → RF01 depuis le début. PASS.
- `RF01_E2E.json` : RF01 joué de bout en bout avec ce build par le pilote automatique (commandes de joueur ordinaires) :
  passe A 57 points de passage, 17 ennemis abattus, objectifs 1, 3, 4, 5, 6, 9 ; passe B sauvegarde, sortie,
  chargement, mort, reprise au point de sauvegarde, sortie de niveau. PASS.

## Limites honnêtes

- Aucune capture 4K ; la mise en page est calculée sur un cadre 1920×1080 mis à l'échelle (vérifiée de 1440×1080 à
  2560×1440 et en 21:9).
- Navigation à la manette non testée.
- Les sons d'interface n'ont pas été écoutés en situation par un humain ; niveaux mesurés seulement.
- Le fond de titre représente la cour de Sainte-Anne ; il n'anticipe aucun élément du canon (CAN-001 à CAN-004).
- La direction visuelle (typographie, bordeaux, placement) est une proposition : seul le propriétaire peut l'approuver.

## Retour arrière

Lancer `JOUER_RF2_ART_REVIEW.cmd`, ou revenir sur la branche de production avant les commits UI-01. Les ressources
d'Astra et leur manifeste sont dans `art/rf2_ui_01_astra/`.
