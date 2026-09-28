# RF2-MAP-02-REPRISE — contrat technique d'Opus pour Astra

27/09/2026, mandat `C:\PROJECTS\RF2_CORRECTIONS_ET_SUITE_20260927` (revue des dix captures, lots RF02-A/B/C,
COMBAT-02). Base d'intégration : branche `prod/rf2-campaign` (dépôt `C:\PROJECTS\RF2_UZDOOM`). Build de référence
jouée par le propriétaire : `dist\candidates\RF2_MAP-02_20260927_1543\RF2_MAP-02.pk3`
(sha256 `11167ce28e37d07e84914435cc561d50d222e09824c142424c12c98c8778b7c1`).

Ce contrat répond à `tram_contract_proposal.json` et fixe le format d'intégration de tes modèles, figures, arme
de mêlée et sons. Il complète `docs/production/handoff/RF2-MAP-02/DEMANDE_ASSETS.md` ; en cas d'écart, ce texte
prévaut. Opus garde WAD, scripts, collisions, déclencheurs, campagne et équilibrage.

## 1. Conventions vérifiées dans le moteur

### Modèles (props, tram, voie, façade du Luna Park)

Essai du 27/09 : ta `pram.obj` + `RF2_MATERIAL_ATLAS.png` chargée telle quelle sur un acteur existant
(`essai_moteur_poussette.jpg`, trois vues, dans ce dossier). Résultat : orientation, échelle et habillage corrects.

| Point | Règle |
|---|---|
| Format | OBJ, ta convention actuelle (`obj_axes: X, Z, -Y`, Blender +Z haut) ; une texture d'habillage par famille (atlas ≤ 2048×2048) ; pas de `usemtl` multiples sauf demande |
| Unités | unités de carte (56 u = hauteur du joueur, 1 u ≈ 3,1 cm) ; MODELDEF appliqué : `Scale 1 1 1.2` + `CorrectPixelStretch` (échelle uniforme en unités de carte) |
| Orientation | **Blender +X = direction de l'acteur (angle 0)**. La poussette : capote vers +X, poignée vers -X |
| Origine | point de contact au sol, au centre de l'empreinte ; pour un objet suspendu (sacoche), le point d'accroche |
| Budget | prop proche ≤ 6 000 triangles ; tram ≤ 60 000 ; façade Luna Park ≤ 40 000 (mesure de temps de trame faite par Opus dans la scène) |
| Transparence | vitrage : laisser vide ou fournir une surface séparée (modèle distinct) qu'Opus rendra translucide ; alpha tout-ou-rien dans l'atlas pour grilles, rayons, lettres |
| Livraison | `.obj` + `.glb` + `.blend` source, rendus 8 azimuts, `bounds`, empreinte au sol (rayon ou boîte), hauteur de collision proposée |

### Figures (sprites)

| Point | Règle (identique aux ennemis ART-01/02) |
|---|---|
| Format | PNG RGBA, une image par état × rotation, noms `XXXXF1`…`XXXXF8` (ou paires miroir `F2F8`, `F3F7`, `F4F6` quand la figure est symétrique) |
| Échelle | acteur `Scale 0.18` → **5,56 px par unité** ; un adulte debout ≈ 300 px de haut (54 u) |
| Ancrage | chunk `grAb` au point de contact (milieu entre les pieds, bas de l'image) ; assise : sous le siège, à la hauteur du support |
| Rotations | 8 pour toute figure contournable ; 1 vue autorisée seulement pour une figure vue d'un seul côté par la géométrie (je le précise par figure) |
| Distinction | civils sans silhouette d'infirmier, de brancardier ou de porte-registre ; aucune arme |

### Arme de mêlée (vue à la première personne)

Même famille que le Browning : canevas **1672×941 px**, `XScale 6.8`, `YScale 8.16`, décalage de famille `-700, -300`
(je règle le décalage final dans `TEXTURES.weapons`). Même master de bras et de manche de sweat noir.

## 2. Tram et voie — réponses à `tram_contract_proposal.json`

| Question | Décision |
|---|---|
| Corps | accepté : 336 × 108 × 133 u, hors-tout 344 × 112 × 136 |
| Plancher | accepté : `floor_z 30`. Opus pose un plancher praticable (3D floor) à 30 et des marches à 15 aux quatre accès de plateforme : **marche de 15 u de haut, 16 u de profondeur minimum dans le modèle** |
| Circulation | allée intérieure ≥ 48 u entre fronts de banquettes ; hauteur libre ≥ 64 u au-dessus du plancher ; plateformes ≥ 48 u de profondeur |
| Rails | acceptés : têtes à z 0, axes à y ±30, module droit de 256 u. Opus pose les modules bout à bout sur toute la traversée du carrefour, sous le tram (voie continue) et dans les deux rues jusqu'aux obstacles (autobus, barricade) ; fournir aussi un **module d'about** (fin de voie, 64 u) |
| Rainure | la chaussée reste plane ; la gorge de rail est portée par le modèle (0,7 u), pas par la carte |
| Perche et fil | **perche abaissée et accrochée sur le toit ; pas de fil aérien** (réseau déposé, tram présent par anomalie du récit, écart consigné) |
| Collision | Opus construit la collision (lignes invisibles, plancher) d'après tes cotes ; donner la position exacte des accès, montants et banquettes dans `tram.json` |
| Contenu | valises (12) sur les banquettes : oui ; cage avec deux poules sur une banquette avant (modèle de cage + 2 poules en sprite 8 rot., 2 états : immobile, picore) ; sacoche du receveur au crochet de la cloison avant, côté plateforme avant |
| Vieil homme | F02-04 assis sur la plateforme arrière (côté +X du modèle), chapeau sur les genoux, mains sur la canne : états « dort » et « yeux ouverts » |
| Origine | centre du tram au niveau des rails ; Opus le pose en (2192, 232, 0), angle 0 (plateforme +X vers l'est) |

## 3. Objets proches (priorité 1 : tranche de référence Arago → carrefour)

| Objet | Fichier attendu | Acteur (Opus) | Support / contact | Collision | Vue du joueur |
|---|---|---|---|---|---|
| Poussette + registres ficelés | `models/rf02/pram.obj` | `RFPramModel`, solide | roues sur le trottoir (z 8) | rayon 22, hauteur 38 | contournable, 0,5 à 6 m |
| Seau galvanisé + papiers | `models/rf02/bucket.obj` ; flammes `sprites/rf02/RFFLA0`…`F0` (6 images, additif, 64×96 px, grAb bas-centre) | `RFFormsBucket` | trottoir (z 8) | rayon 10, hauteur 22, non solide | contournable |
| Sacoche du receveur | `models/rf02/satchel.obj`, origine au point d'accroche | `RFSacoche` | crochet de cloison, 36 u au-dessus du plancher du tram | aucune | de face et de trois quarts |
| Postes TSF (3 variantes) + poste réparé | `models/rf02/radio_a/b/c.obj`, `radio_off.obj`, `radio_on.obj` | étagères construites par Opus (profondeur 24 u) | tablettes à 0, 32 et 64 u | aucune | derrière la grille, 1 à 8 m |
| Téléphone de campagne | `models/rf02/phone.obj` (combiné posé, manivelle latérale, câble vers le mur) | `RFFieldPhone` | table pliante | aucune | de près, trois côtés |
| Table pliante | `models/rf02/table_folding.obj` (plateau 48×32 u, hauteur 30) | `RFPropFoldingTable` | chaussée | rayon 20, hauteur 30 | contournable |
| Mitrailleuse sous bâche, deux casques | `models/rf02/mg_tarp.obj`, `helmet.obj` | décor | sacs de sable | aucune | 1 à 5 m |
| Sacs de sable | `models/rf02/sandbags_64.obj` (module 64 × 24 × 48 u) | Opus garde la collision en géométrie | chaussée | géométrie | contournable |
| Valise brune ouverte avec chaussures | `models/rf02/suitcase_open.obj` (fermée : `suitcase.obj`) | posée par la jeune femme (scène) | table renversée | aucune | 1 à 3 m |
| Tableau des départs | `models/rf02/board_departures.obj` : cadre, deux montants ou consoles murales, tableau à l'échelle (128 × 64 u), texte composé exact (heures, destinations vides : le texte dit « des heures sans départ, des voies sans convois ») | décor | façade de la gare (fixations visibles) | aucune | face, profil, dessous |
| Ambulances (2) | `models/rf02/ambulance.obj` (≈ 176 × 64 × 96 u), portes fermées, moteur arrêté | décor solide | cour de Cochin | boîte d'après `bounds` | contournable |
| Brancard avec homme couvert | `models/rf02/stretcher.obj` + figure F02-06b (homme allongé, tête qui se tourne : 2 états) | décor | pavés de la cour | rayon 24 | contournable |
| Matelas (Denfert) | `models/rf02/mattress.obj` (existant) | décor ; le reflet reste un sprite (`RFMTA0`, comportement Opus) | trottoir | aucune | contournable |
| Colonne Morris | habillages `models/rf02/morris_{luna,jerma,dentifrice}.png` sur le maillage d'Opus (`morris.obj`, rayon 22, hauteur 128 + dôme), **une source par état, même typographie** ; ou ton propre maillage avec la même hauteur et le même rayon | `RFMorrisColumn` | trottoir | rayon 24 | contournable |

Les sprites 2D actuels (`RFBKA0`, `RFBGA0`, `RFPHA0`, `RFRDA0/B0`) sont remplacés par les modèles : ne pas les
retoucher davantage.

## 4. Luna Park : entrée et abords (RF02, fin de carte)

Emplacement actuel : palissade nord de la place de la porte Maillot, grille à x -2144…-1984, porte de service à
x -1776…-1728, y 3200. Vues d'arrivée : depuis l'avenue (ouest→est, 300 à 900 u), de face (100 à 300 u), en biais.

| Élément | Fichier | Cotes / contact |
|---|---|---|
| Entrée monumentale construite (volumes, structure, grille, fixations d'enseigne, ampoules mortes) | `models/rf02/luna_entrance.obj` | largeur ≈ 320 u, hauteur ≤ 360 u, profondeur 48–96 u ; la grille cadenassée large de 160 u centrée ; seuil au sol z 8 |
| Enseigne LUNA PARK, U pendant | dans le modèle ou `luna_letters.obj` séparé ; U incliné de 12–15°, une attache cassée | au-dessus de la grille |
| Panneau FERMETURE DÉFINITIVE, « définitive » barré au charbon | texture existante `RF2_LUNF` ou version finale, **fixé** (clous/fil) sur la grille ou un poteau | 96 × 32 u |
| Palissade | `models/rf02/palisade_128.obj` (module 128 × 12 × 192–256 u, planches, affiches décollées) | Opus en aligne 12 modules |
| Porte de service entrouverte, derrière un amas de planches ; rectangle plus propre où une plaque a été retirée | `models/rf02/service_door.obj` (cadre 48 × 104 u, battant ouvert à 30°) + `planks_heap.obj` | passage libre ≥ 40 u |
| Volumes du parc en arrière-plan (charpentes, sommet de montagne russe, toits) | `models/rf02/luna_skyline.obj` (silhouette lointaine, peu de polygones) | posé derrière la palissade à 200–600 u |

Garder U pendant, enseigne éteinte, panneau barré. Distinguer nettement l'entrée principale (fermée) de l'accès de
service.

## 5. Figures F02-01 à F02-08

| ID | Figure | États (frames) | Rotations | Où, support |
|---|---|---|---|---|
| F02-01 | Homme en uniforme brûlant des formulaires | debout penché, geste lent de nourrir le feu (3 frames en boucle) | 8 | trottoir sud d'Arago, à 20 u du seau |
| F02-02 | Femme poussant la voiture d'enfant | marche lente 4 frames + arrêt 1 frame, mains sur la poignée (la poussette est le modèle séparé) | 8 | trottoir nord d'Arago ; Opus la fait avancer lentement sur 300 u puis s'arrêter |
| F02-03 | Trois femmes sous un parapluie fermé, panier, couverture roulée, enfant par la main ; l'enfant regarde les chaussures de Viktor | groupe : 1 état statique + 1 état « l'enfant lève la tête » | 8 (groupe en une seule figure, ou 4 figures) | devant la porte de la Santé |
| F02-04 | Vieil homme du tram | dort / yeux ouverts | 3 (vu de l'avant et des côtés de la plateforme) | assis sur la plateforme arrière du tram, z plancher 30 |
| F02-05 | Garçon de ~15 ans, blouse grise, tournevis et boîte de lampes | accroupi derrière le comptoir ; debout (ouvre la grille) | 5 (demi-tour avant) | boutique TSF, comptoir hauteur 32 |
| F02-06 | Femme de Cochin, blouse blanche, coiffe, cheveux gris, enveloppe tenue à deux mains | debout, marche lente 4 frames (elle traverse la rue et revient), bras baissé après le refus | 8 | devant l'entrée de Cochin |
| F02-06b | Homme couvert jusqu'au menton sur le brancard | allongé ; tête tournée vers Viktor | 3 | brancard de la cour |
| F02-07 | Jeune femme de Sainte-Anne : robe claire, épingle, bracelet d'hôpital sans nom, valise brune | marche 4 frames, debout, pose la valise (2 frames), repart | 8 | barrage de l'Assemblée ; elle repart vers le pont |
| F02-08 | Viktor en pied pour les reflets (même master que le visage du HUD et les manches du sweat noir ; barbe de plusieurs jours selon le roman : consigner l'écart éventuel) | debout, marche 4 frames | 8 | uniquement dans les miroirs (`ONLYVISIBLEINMIRRORS`) |

Répliques : la mise en scène est d'Opus (attribution des dialogues à l'écran). Voix enregistrées facultatives ; si
tu en produis, préciser la méthode et les droits ; aucune voix de personne réelle.

## 6. Pied-de-biche (COMBAT-02)

Choix d'adaptation du mandat : un pied-de-biche d'atelier (pas un objet du roman ; la clé plate de dix-sept du Luna
Park reste distincte).

| Élément | Attendu |
|---|---|
| Sprites 1re personne | préfixe `RFCB` : A prêt (repos, léger balancement) ; B armé ; C frappe milieu ; D **impact** (frame du coup) ; E suivi ; F retour. Même canevas et échelle que le Browning (§1) |
| Durées visées | armé 5 tics, frappe 3, impact 2, suivi 4, retour 8 (≈ 0,63 s au total) ; je règle en jeu |
| Modèle au sol | `models/rf02/crowbar.obj` (≈ 24 u de long) posé sur un établi ou contre un mur |
| Sons | `sounds/weapons/crowbar/{swing1,swing2,swing3,hit_flesh1,hit_flesh2,hit_hard1,hit_hard2,hit_wood1,miss1}.wav` |

Emplacement prévu dans RF02 (Opus) : dans le seau à outils de la cour de Cochin, près des ambulances ; obtention
par ramassage ; le lanceur de revue le donne aussi (identifié comme confort de revue).

## 7. Sons (lieux, armes)

WAV mono 48 kHz PCM16, crête ≤ -3 dBFS, boucles sans clic. Déclencheurs posés par Opus.

| Fichier | Déclencheur |
|---|---|
| `sounds/weapons/browning/fire1-3.wav` | chaque tir (variation aléatoire), sec et précis |
| `sounds/weapons/fal/fire1-3.wav`, `fal/tail.wav` | tir isolé, queue en espace ouvert |
| `sounds/paris/tram_creak_loop.wav` | boucle près du tram (rayon 400 u), tôle et bois qui travaillent |
| `sounds/paris/hens_loop.wav`, `hens_cluck1-3.wav` | cage du tram |
| `sounds/paris/cart_cages.wav` | la charrette de cages vides qui passe quand Viktor se retourne (pharmacie) |
| `sounds/paris/dog_drink_loop.wav` | chien au caniveau d'Arago (si la figure du chien est produite) |
| remplacements facultatifs de `sounds/paris/*.wav` (même nom) | voir `DEMANDE_ASSETS.md` §4 |

Indique pour chaque fichier « produit » ou « écouté » ; une mesure ne vaut pas écoute.

## 8. Livraison et ordre

Dépose dans ton worktree `incoming/astra/RF2_MAP_02_REPRISE/` (ne réécris pas les livraisons précédentes), un
sous-dossier par lot, avec `manifest.json` (cible, sha256, dimensions en px et en unités, échelle, ancrage,
états/rotations, collision proposée, provenance, crédits) et tes preuves. Ordre utile :

1. **Tranche de référence** : façades `RF2_FAC1/2/3/FACU` (déjà prêtes chez toi), poussette, seau + flammes, voie,
   tram, plaques. Opus l'intègre et la contrôle en déplacement avant la suite.
2. Barrage (téléphone, table, bâche, casques), TSF (radios), tableau des départs, Cochin (ambulances, brancard).
3. Figures F02-01 à F02-08.
4. Luna Park (entrée, palissade, porte de service, silhouette du parc).
5. Pied-de-biche et sons d'armes.

Captures du moteur actuel pour chaque cible : `C:\PROJECTS\RF2_CORRECTIONS_ET_SUITE_20260927\references\captures\`
(propriétaire) et `dist\candidates\RF2_MAP-02_20260927_1543\evidence\scenes\` (Opus, 1920×1080).
