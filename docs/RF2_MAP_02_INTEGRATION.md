# RF2-MAP-02 — RF02 « Paris - Rue de service » (production Opus)

**Statut : RUNTIME_VERIFIED_OWNER_REVIEW_REQUIRED.** Candidate du 27/09/2026, non approuvée. Les figures humaines du
texte manquent (demandées à Astra) : la carte n'est pas annoncée « complète et fidèle ».

## Jouer

- `JOUER_RF2_MAP-02_RF02.cmd` : ouvre directement RF02 (difficulté Service, équipement de sortie de Sainte-Anne :
  Browning, FAL et leurs munitions).
- `JOUER_RF2_MAP-02.cmd` : ouvre l'écran titre ; « Nouvelle partie » enchaîne RF01 puis RF02.
- Ce build est **cumulatif** : branche `prod/rf2-campaign` = RF01 accepté + ennemis retouchés (ART-02) + menus (UI-01)
  + RF02. Pour juger RF02 seul avec les ennemis d'origine, le lot ART-02 reste jouable à part.
- À la fin de RF02, le jeu revient au titre : RF03 n'est encore qu'un blockout V1 (Freedoom) et n'est pas enchaîné.
- Profil et sauvegardes séparés (`user\uzdoom_map02.ini`, `user\savegames_map02`).

## Ce que la carte fait du texte

Passage du roman l. 87–457, lu en entier ; tableau ligne par ligne dans `docs/production/CANON_FIDELITE.md` §6 et
fiche dans `docs/production/maps/RF02_FICHE.md`. Sept espaces dans l'ordre du texte, reliés par des rues :

1. **Boulevard Arago** — mur et grande porte close de la Santé, affiche INTERDICTION DE STATIONNER arrachée ;
   formulaires qui brûlent mal dans un seau (« Domicile. Père inconnu. Autorisation. Conforme. ») ; voiture d'enfant
   pleine de registres.
2. **Carrefour du tramway / Denfert** — le tram immobilisé, portes ouvertes, praticable : valises sur les banquettes,
   sacoche du receveur, ticket poinçonné au cercle incomplet barré ; pochoirs CAVE / POSTE DE SECOURS / EAU, sacs de
   sable, matelas, autobus incliné.
3. **Port-Royal / Cochin** — rideau de fer de la pharmacie, ERREUR Ø frais au pinceau, la goutte sous le R ; dans la
   vitrine latérale (un vrai miroir derrière les bocaux), le matelas avance seul dans le reflet et disparaît quand
   Viktor se retourne ; cour de Cochin, ambulances moteurs éteints.
4. **Montparnasse / rue de Rennes** — gare fermée, tableau des heures sans départ ; la TSF : de la rue, la vitrine
   montre un Amiga (écran bleu, disquettes dans une boîte à chaussures, un plan d'hôtel), qui disparaît quand on
   s'approche (CAN-002) ; trois voix des postes ; le poste au fusible noirci, réparé, puis la voix allemande ;
   épicerie pillée, vin dans la rigole ; barricade de livres, l'atlas et la fiche de lecteur « JERMA - ERREUR Ø ».
5. **Quai et pont** — rambardes de fonte, la Seine, papiers militaires, les moteurs venant du nord.
6. **Barrage près de l'Assemblée** — sacs de sable, mitrailleuse sous bâche, le téléphone militaire qui sonne :
   « Ardent ? Incident critique… » jusqu'à « Nous aussi. », Ø gravé sous le boîtier.
7. **Rues secondaires jusqu'à la porte Maillot** — rue étroite et borne-fontaine (le goût de rouille) ; Champs-Élysées,
   la colonne Morris ronde (LA VILLE ENCHANTÉE DE LA PORTE MAILLOT ; grattée, JERMA PALACE le temps d'un battement,
   puis la poudre dentifrice et la colle couleur grenat) ; Grande-Armée, pneus, la cloche à l'ouest ; porte Maillot,
   taxis abandonnés, LUNA PARK au U pendant, FERMETURE DÉFINITIVE barré au charbon, grille cadenassée, sortie par la
   porte de service entrouverte.

Rencontres : sept vagues du personnel de Sainte-Anne (l'adaptation acceptée de RF01), qui apparaissent hors de vue
(ruelles, derrière le bus et les ambulances, angles du quai, ruelles du boulevard après l'appel, rue au sud de la
porte Maillot). Aucune troupe allemande n'est combattue ; les moteurs et la radio seulement.

## Preuves

Build `dist\candidates\RF2_MAP-02_20260927_1543\RF2_MAP-02.pk3`, sha256 `11167ce2…78b7c1`, commit `b3d14b0`.
Dans `evidence/` :

- `RF02_E2E.json` — RF02 joué avec ce build par le pilote automatique (commandes de joueur ordinaires, départ direct) :
  passe A, 54 points de passage, 17 ennemis abattus, objectifs 1 à 8 dans l'ordre, sortie réelle du niveau ;
  passe B, sauvegarde avant Cochin, arrêt du moteur, relance, chargement, mort, reprise au dernier point de
  sauvegarde, sortie. PASS.
- `RF01_E2E.json` — RF01 rejoué avec ce même build : A et B PASS, objectifs identiques à ceux du build accepté.
- `film/RF02_traversee_avec_son.mp4` — la traversée complète en temps réel, 2 min 10 s, 1280×720, son du moteur
  (mixage du jeu enregistré par OpenAL, gain inchangé, aucun échantillon saturé).
- `scenes/` — treize vues des scènes (Santé, tram dehors et dedans, vitrine-miroir, ERREUR Ø, reflet de l'Amiga,
  tableau des départs, atlas, pont, téléphone, colonne Morris, entrée du Luna Park, porte de service) ; `tour/` —
  27 vues de la visite, en 1920×1080.
- Les quinze scènes se déclenchent chacune une fois dans la traversée (marqueurs `RF_DEV_SCENE` du journal).
- Lanceurs essayés depuis un autre dossier : départ direct (RF02 chargé en 3,6 s) et écran titre (pk3 chargé, titre
  stable).

## Limites honnêtes

- **Figures humaines absentes** : les trois femmes de la Santé, l'homme au seau, la femme à la voiture d'enfant, le
  vieil homme du tram, l'homme au matelas, la femme de Cochin et son enveloppe, le garçon de la TSF, les pillards, la
  jeune femme de Sainte-Anne et sa valise de chaussures, les soldats. Demandées à Astra (F02-01…08). Sans elles, Paris
  est plus vide que dans le roman, et deux scènes ne sont pas jouées (l'enveloppe « vos résultats », la valise).
- Images d'objets et de l'Amiga : versions procédurales d'Opus, lisibles mais nettement moins abouties que RF01 ;
  remplacement fichier pour fichier prévu (`DEMANDE_ASSETS.md` §4).
- Sons de lieu synthétisés par Opus (souffle des postes, sonnerie, moteurs, cloche, feu, rue), **non écoutés par un
  humain** ; aucune voix : les voix et la marche du texte sont écrites à l'écran.
- La colonne Morris est un modèle simple ; la Seine est une surface animée sans reflets ; pas d'arbres sur les
  Champs-Élysées ; le Lion de Belfort n'est pas représenté.
- Le fond sonore reprend RFAMB01 (celui de RF01) ; aucune musique nouvelle.

## Défauts trouvés dans le code partagé

- Le directeur n'appliquait les lignes d'objectif et de fin de niveau qu'à RF01 : corrigé pour tous les chapitres,
  RF01 inchangé.
- **Les panneaux muraux de RF01 accepté ne s'affichent pas.** L'ancien calcul du kit enfonce la texture sous le sol
  (le moteur relève une texture médiane avec un décalage positif, en pixels de texture). Preuve dans le dossier de la
  candidate, `evidence/rf01_panneaux/` : même vue du hall, build accepté (porte de la cour sans panneau) et même carte
  avec le seul décalage corrigé (PAVILLON EST au-dessus de la porte). RF02 utilise le calcul corrigé ; **RF01 n'a pas
  été modifié**. Correction possible en lot séparé (treize panneaux : ADMISSIONS, SORTIE, PAVILLON EST, LINGERIE…),
  sur décision du propriétaire.
- Le rayon « utiliser » du moteur s'arrête au bord d'une table ou d'un comptoir surélevé et rate les petits objets :
  après RF01, l'invite affichée devient la règle (la touche utilise l'objet nommé par l'invite). RF01 garde son
  comportement accepté. Sa note du registre d'admission, posée sur une table, **se lit bien** à la touche d'usage
  (vérification réelle du 27/09 soir sur le build accepté : `docs/production/RF01_REGISTRE_VERIFICATION.md`).
