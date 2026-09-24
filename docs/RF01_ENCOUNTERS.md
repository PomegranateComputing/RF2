# RF01 — fiche des rencontres

Difficulté « Service » (normale). « Difficile » ajoute un infirmier à E3, E4, E5 et E6, un à E7
et un infirmier en embuscade (réveil à vue) dans les Registres. Source : `scripts/mapkit/rf01.py`.
Les ennemis en attente ne sont pas visibles avant leur signal (contrôle `scripts/mapkit/encounters.py`).

| # | Lieu | Signal | Ennemis (PV) | Ce que voit le joueur en entrant | Espace, couverture | Sortie | Ressources avant |
|---|------|--------|--------------|----------------------------------|--------------------|--------|------------------|
| E1 | Couloir du pavillon ouest | milieu du couloir ; prise de la clé de la grille | infirmier du poste (60), puis infirmier de la chambre 2 (60) | un long couloir vide, portes des chambres, la grille au bout | couloir de 128 u, pilastres, radiateur ; recul vers les chambres | la grille (clé) | Browning, 9 mm ×4 boîtes, 2 pansements |
| E2 | Admissions | seuil du vestibule, en prenant le FAL | 2 infirmiers : Économat (porte est) et porte de la cour (120) | le FAL posé près d'un corps, dos au hall | vestibule étroit contre hall haut ; comptoir en L, colonnes | porte de la cour | FAL (20+20), 2 chargeurs, pansement |
| E3 | Cour des hommes | passage sous l'arcade sud | Porte-Registre sur le perron, 2 infirmiers de l'arcade est (230) | la cour entière, le bassin, le perron nord | grand espace ouvert, arcades, bassin et jardinières ; distance au lanceur | pavillon est (arcade est) | chargeur du hall |
| E4 | Pavillon est, salle commune | premières marches de la salle | Brancardier sur l'estrade, charge dans l'allée (170) ; infirmier du bureau (60) | l'allée entre deux rangées de lits, l'estrade au fond | allée de 224 u, lits bas ; esquive latérale contre la charge | porte de service (escalier) | chargeur du bureau, pansement de l'estrade |
| E5 | Lingerie (sous-sol) | porte de la lingerie ; milieu de la salle | 2 infirmiers entre les cuves (120) ; Porte-Registre en haut de l'escalier ouest (110) | un sous-sol carrelé bas, cuves, chariots | plafond bas, cuves comme couverture ; l'escalier ouest monte vers le tireur | escalier ouest vers la galerie | chargeur, pansement ; séchoir secret : 2 chargeurs, pansement |
| E6 | Consultations | ouverture de la salle d'attente ; couloir des consultations | Brancardier dans le couloir (170) ; 2 infirmiers du cabinet A et de l'infirmerie (120) | la salle d'attente, bancs, l'ouverture vers le couloir | couloir long et étroit : la charge est dangereuse ; portes des cabinets | porte à sens unique vers le hall | 2 chargeurs, 2 pansements |
| E7 | Admissions (finale) | sortie de la loge après le treuil | 3 infirmiers depuis la cour, Porte-Registre depuis les consultations (290) | le hall connu, désormais ouvert vers le porche | hall haut, comptoir, colonnes ; deux directions d'arrivée | le porche (grille levée) | pansement du hall, restes du parcours |

Respiration : la chapelle vide (branche du couloir ouest, sacristie secrète). Secrets : séchoir
de la lingerie (panneau carrelé) et sacristie.

Bilan des ressources posées (normal) : 320 cartouches de 7,62 mm (FAL compris), 84 de 9 mm,
300 points de soins ; 1 510 PV ennemis. Marge large : la pression vient du corps à corps et de
la charge du Brancardier, pas de la pénurie. À recalibrer après un parcours humain.

Porte-Registre : le lancer suit une trajectoire calculée vers le torse du joueur (distance et
dénivelé) ; coincé par le joueur dans un passage étroit (haut de l'escalier de la lingerie), il
lance quand même au bout d'une seconde sans pouvoir bouger. Sans cela, le joueur arrivé à son
contact en haut de l'escalier ne prenait plus aucun coup (vu en jeu, parcours B).
