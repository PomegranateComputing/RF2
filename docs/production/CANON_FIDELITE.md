# RF2 — matrice de fidélité au roman

Document actif (27/09/2026), tenu par Opus. Exigence du complément propriétaire `06_CANON_OBJETS_ET_SCENES.md` :
les scènes et objets essentiels du roman doivent être présents, reconnaissables et mis en scène dans leur contexte.
Une mention ici ne vaut pas présence dans le jeu : seule la colonne « État » dit ce qui est réellement intégré.

## 1. Source et méthode

- EPUB de référence : `C:\Users\zecol\OneDrive\Documents\ECRITURE\La_Couleur_de_la_Pomegrenade_KDP_MASTER_COUVERTURE.epub`,
  SHA-256 `b5f76b0e64e8963ef28ddf346671e04d53aca9f23123a1311fcbc221b50a4af9` (identique au pack du 27/09 ; c'est la seule
  édition trouvée sur le poste, avec des manuscrits `.docx` par blocs dans le même dossier, non utilisés).
- Numéros de ligne : lignes du texte extrait de `EPUB/text/body.xhtml` par `scripts/production/novel_extract.py`
  (le roman n'est pas copié dans le dépôt). Le corps compte 45 017 lignes ; avant-propos `ch002`, prologue, épilogue `ch004`.
- Lecture : **intégrale**. Opus a lu lui-même les lignes 1–599 (Sainte-Anne, traversée de Paris, entrée du Luna Park) ;
  le corps entier a été lu en huit tranches par huit lectures parallèles, plus une pour l'avant-propos, le prologue et
  l'épilogue, chacune rendant un inventaire factuel (séquence, lieux, objets, inscriptions exactes, menaces, sons).
  Les neuf inventaires sont reçus. Ils restent hors du dépôt (ils citent longuement le roman) ; seules les références
  utiles au jeu sont reprises ici.
- Statuts du récit à préserver : observation, vidéo, photo, image générée, souvenir, document, hypothèse, anomalie.
  Le roman fait constamment douter de ce qui est vu ; l'adaptation garde ces statuts (un reflet reste un reflet).

## 2. Limites posées par l'auteur (avant-propos, à respecter partout)

« Ce n'est pas un voyage dans le temps. » Ni « démon caché dans le data center », ni « intelligence artificielle
devenue Dieu », ni « société occulte ». « La maladie n'est pas un monstre narratif. » « Ce livre ne possède pas de
clé » : l'origine d'ERREUR Ø reste multiple (graffiti, code `ERR 0` d'un genlock, erreurs de lecture). « La couleur de
la pomegrenade n'est pas un code. » Livre « obsessionnellement matériel » : dates, formats, procédures, températures.

Conséquence pour les ennemis : le roman ne contient **aucun monstre ni combat armé**. Les familles hostiles du jeu
sont une adaptation (acceptée pour RF01 : personnel de l'institution qui continue sa procédure). Elles ne doivent
jamais représenter le couple, les patients, la maladie, ni une force occulte.

## 3. Fil du roman et cartes

Ordre courant du projet = ordre MAPINFO RF01–RF23 (titres V1 = repères historiques). Correspondance constatée :

| Séquence du roman | Lignes | Carte V1 correspondante | Remarque |
|---|---|---|---|
| Sainte-Anne, 14 juin 1940, 6 h 20 | 3–85 | RF01 (accepté) | |
| Traversée de Paris : Arago, Santé, tramway, Denfert, Port-Royal, Cochin, Montparnasse, TSF rue de Rennes, librairie, pont, barrage de l'Assemblée, Champs-Élysées, porte Maillot | 87–457 | RF02 « Rue de service » (titre justifié l. 415–417) | en production |
| Luna Park, premier passage : guérite, pointage 06:06, clés, décors, salle de danse, sous-station (NODE 0, levier MARCHE/ATTENTE/ARRÊT) | 451–689 | RF04 « Personnel technique », RF05 « Les machines continuent » | **avant** Batignolles dans le roman |
| Couloir ERREUR Ø vers le Jerma | 691–731 | transition | |
| Jerma Palace, décembre 2022 : terrasse, chambre au matelas, escalier de service, cuisines et chambres froides, quai, piscine (escarpin), bureau ENGINEERING (disquette) | 733–1097 | RF07–RF12 | |
| Malte, nuit des générations ; page StepRoom « M. & L. » | 1099–1451 | chapitre Jerma (local vidéo RF12 ?) | |
| Hiver 2022-2023, ville non nommée : magasin et dépôt de Milan Kovac (lecture de l'Amiga) | 1453–2741 | aucun titre V1 (RF20 « Amiga de Milan » vient d'un autre passage) | à décider |
| Faisceau des Batignolles 1940 : wagons de viande refusés, manifeste « FLOW CONSULTANT » | 2743–2991 | RF03 « Batignolles - Refus de réception » | **après** Luna Park et Jerma dans le roman |
| Clichy, Luna Park second passage (réquisitionné, palais du rire, porte 117, infirmerie) | 2993–3601 | RF05 / RF06 | |
| Bâtiment B (ponction), flashback Paceville, DAT de Milan (vidéo 2007) | 3603–4801 | — | |
| Waukegan : motel 217, WKG Cold Storage bâtiment 2, unité 117, local de pointage caché, carnaval | 4803–7751 | RF13, RF14, RF15, RF16 | |
| Paris 2026, Sainte-Anne archives, Gennevilliers, Saint-Ouen | 8629–11253 | RF18 (Gennevilliers) | |
| Lausanne, Luna Park 1940 (dépôt, Dépôt Ouest), Waukegan remorque, Racine | 11255–16881 | RF17, RF19 | |
| Malte, Żabbar, Lakeshore (chambre froide, cassette VHS-C « C-4 », `CONSERVATION HOLD`), Morrow ; en montage alterné, Luna Park juin 1940 (convoyeur, brassard T.D., effets personnels évacués) | 16883–33763 | RF17 « Conservation provisoire » (Lakeshore ou Morrow, à trancher), RF19 ; le fil 1940 nourrit RF04–RF06 | |
| Décommission SQL « VERIFY RESTORE TO ISOLATED HOST », Vella, retours StepRoom `M + L / DO NOT MAIL` | 31877–44067 | RF20 « Copie de secours », RF21 « Retours », RF22 « Destinataire présent » | |
| Hôpital 2026, salle d'attente, « trois hommes se levèrent » ; épilogue | 44763–45015 ; `ch004` | RF23 « Salle d'attente » | |

**Écart d'ordre à trancher par le propriétaire** : dans le roman, le premier Luna Park et le Jerma précèdent les
Batignolles (RF03). RF02 se termine à la porte de service du Luna Park (fidèle au texte). Options : (a) garder l'ordre
V1 et faire de RF03 un saut assumé ; (b) permuter pour suivre le roman (RF03 = Luna Park, Batignolles plus tard).
Opus ne renumérote pas la campagne sans décision.

## 4. Éléments obligatoires CAN-001 à CAN-004

| ID | Passage source | Statut dans le récit | Première apparition / récurrences | Carte(s) proposée(s) | Forme d'adaptation | Dépendances | État |
|---|---|---|---|---|---|---|---|
| **CAN-001** Disquette rouge 3,5″ `JERMA_A1200_04` / `ROOMS / FLOW / FINAL` | trouvée l. 1007–1015 (bureau ENGINEERING, sous un annuaire moisi) ; lecture l. 1869–2075 ; ligne violette `BACK FROM WORK - ROOM 117` l. 1931 ; revient dans le lecteur l. 4965 ; lue à Lausanne l. 12379–12773 ; photo de M. J. Vella « une disquette rouge entre deux doigts » l. 27227 | observation, puis anomalies contestées ; photo | Jerma → atelier de Milan → Lausanne → enveloppe « 4/17 » (Waukegan) | découverte : chapitre Jerma côté service (RF10) ; lecture : chapitre Milan (à placer) ; contenu ROOMS/FLOW/FINAL comme espace : RF11 | objet ramassable à l'endroit exact ; étiquette lisible (deux lignes, cercle barré au dos) ; second état avec la ligne violette | master Astra (coque rouge sombre presque brune, étiquette manuscrite) ; texte composé | présence exigée, **implémentation non commencée** |
| **CAN-002** Amiga 1200, moniteur, lecteur | reflet dans la vitrine de TSF l. 213 ; atelier de Milan l. 1807–2453 (Workbench, `Disk is unreadable.`, `1 024 objects, 0 bytes free.`, lecture après coupure) ; Amiga de l'unité 117 même numéro de série l. 5455–5467 ; Vella « devant un Amiga 1200 ouvert » (photo) l. 27227 ; bordereau 1997 `2 x AMIGA COMPUTER UNITS` l. 28057 | reflet (vision), puis observation contestée ; documents et photos | RF02 (reflet), Milan, WKG, Echandens, Malte (Vella) | **RF02** : reflet dans la vitrine de TSF (première occurrence) ; atelier de Milan ; RF15 (WKG) | RF02 : apparition brève dans le reflet, disparaît quand Viktor approche ; plus tard machine en espace, écran modulaire, son du lecteur | master Astra de la machine + écran bleu Workbench + boîte à chaussures de disquettes ; son du lecteur | RF02 : mise en scène prévue, **master manquant** |
| **CAN-003** Escarpin du matelas brûlé | l. 889–935 (dans le matelas jeté dans la piscine vide ; absent des photos d'Elvis l. 909–913 ; réapparaît sur le rebord l. 1095) | observation contre photographie | Jerma ; échos : valise de chaussures (RF02 l. 391), chaussure d'enfant au Niagara (l. 523) | RF09 « La piscine vide » | séquence locale : le matelas, la chaussure visible ; photo diégétique d'Elvis sans elle ; extinction ; réapparition sur le rebord | master Astra (semelle noire, talon bas, boucle latérale) ; matelas brûlé | présence exigée, non commencée |
| **CAN-004** Couple « M. & L. » → Mark D. et Lena M. (vidéos 2007, StepRoom) | page archivée « M. & L. » l. 1397–1439 ; fragments l. 1545–1587 ; vidéo complète sur la DAT l. 4221–4333 ; « Mark D. and Lena M. » l. 5437 ; noms complets « Mark Dale, Lena March » dans un rapport qui refuse toute identification l. 24281 ; bandes WKG (BACK FROM WORK, ARGUMENT / DELETE, LAKE DAY) l. 5969–6451 ; `M + L / DO NOT MAIL` détruit sans accès l. 41773–44047 ; avant-propos « Ce couple de 2007 » | page, vidéo, souvenir incertain, documents ; identité jamais certifiée | nuit de Malte → DAT → Waukegan → retours | présence substantielle : chapitres Waukegan (RF13–RF16) et RF21 « Retours » ; « M. & L. » d'abord seulement | supports (écrans, bandes) montrant leurs gestes, visages hors cadre ; respect de l'ordre des identités ; ne jamais en faire des ennemis | masters Astra des deux personnes (pas les rigs ennemis) ; lecteurs vidéo ; sons | présence exigée, non commencée |

## 5. Autres éléments essentiels

| ID | Élément | Passage | Cartes | Forme d'adaptation / état |
|---|---|---|---|---|
| CAN-005 | **Carton de pointage** `LUNA PARK - PERSONNEL TECHNIQUE`, n° 017, pointé `06:06` | rendu à Sainte-Anne l. 11, lu l. 75 ; guérite l. 481 ; tombe du matelas du Jerma l. 813 ; local de pointage WKG l. 6637 | RF01 (remise), RF02 (porté), RF04 (pointeuse) | objet porté (HUD « objets ») ; pointage réel au Luna Park. RF01 : ajout borné proposé (voir §7) ; RF02 : porté à partir du départ |
| CAN-006 | **ERREUR Ø** (et `ERR 0`, `ERREUR O`, `ERROR 0`) | registre de Sainte-Anne au crayon bleu l. 21 ; rideau de la pharmacie, frais l. 153 ; fiche de lecteur l. 315 ; guérite l. 517 ; couloir tous les 20–30 m l. 715 ; Jerma ; code genlock l. 43495 | toutes | occurrences placées selon le texte, jamais expliquées ; RF02 : rideau de la pharmacie (Port-Royal) |
| CAN-007 | Bracelet blanc, rendez-vous du **19 août 2026 à midi** ; flacon brun **117** ; montre arrêtée | l. 11, 57 | RF01, RF02 | objets portés ; mention dans les notes |
| CAN-008 | Sous-station du Luna Park : moteur à courroie, coffret **NODE 0**, levier `MARCHE / ATTENTE / ARRÊT` | l. 551–689 | RF04/RF05 | mécanisme central d'une carte |
| CAN-009 | Jerma : chambre au matelas qui brûle, graffitis, `ROOM 117 - SEALED` | l. 733–1097 | RF07–RF12 | architecture et scènes |
| CAN-010 | Train de viande (Tchernobyl), manifeste `VIKTOR ARDENT - FLOW CONSULTANT`, wagons refusés | l. 2253–2297, 2743–2991 ; RF19 | RF03, RF19 | réparation du groupe froid comme action de jeu |
| CAN-011 | WKG Cold Storage, unité 117, `NOTHING BELOW WATERLINE IS IN THE RIGHT BOX.` | l. 5099–5627 | RF14, RF15 | lieux |
| CAN-012 | T-shirt `L.I. GARBAGE BARGE - WORLD TOUR '87` (Mobro 4000), Khian Sea / Felicia / Pelicano | avant-propos ; prologue ; l. 9469, 41611 | RF15, RF18, RF21 | objet conservé ; pas de carte navale déduite |
| CAN-013 | FAMILY WATCH (1988), Amiga de Reggie, disquette `SATAN SYMBOLS` | l. 4247–4265, 6539–6601 | RF16 | écrans et bandes |
| CAN-014 | Vella : transparents Meridian, palette `POM6` (**POMEGRENADE 108 36 39**, CONCRETE 112 107 101, SERVICE BLUE 44 62 71), fichiers `OUT`, `FIREXIT`, `COLDROOM` | l. 30217–30251, 37031–37239, 43483 | RF10, RF20 | plans et palette — les trois couleurs servent déjà de repères de matière |
| CAN-015 | Cassette VHS-C « C-4 » (`COPY 2`, `RETURN WITH PAYMENT`, location Meridian 6427, Sea Glass Media, Jerma 2006-2007) gardée à Lakeshore ; Contact A refuse toute lecture (`CLOSE IT.`, `NON-ACCESS FIRST.`) ; Morrow Private Archive Services | l. 22515–28133 ; partie 6 | RF17 | chambre froide, étagère C-4, bac `CONSERVATION HOLD` : lieu de garde, jamais de lecture jouable. Le contenu de la bande n'est jamais montré |
| CAN-019 | Luna Park, juin 1940, second fil : convoyeur réparé, brassard gris `T.D.`, effets personnels évacués (`EFFETS PERSONNELS — NE PAS UTILISER`, cahier `DÉPÔTS PROVISOIRES`), caisses civiles marquées Sainte-Anne, guichet de billetterie, réserve de confiserie, autos tamponneuses, salle de tir, manteau gris à la croix de craie | l. 22771–27779 | RF04–RF06 | espaces et objets du Luna Park réquisitionné ; aucun combat dans le texte |
| CAN-020 | Viktor porte un « sweat noir » dans le Luna Park de 1940 | l. 22783 | tout l'arsenal | appui textuel du bras en sweat noir accepté en RF01 |
| CAN-016 | Salle d'attente 2026 : borne, étiquette `VIKTOR ARDENT`, grenade en plastique aux 47 trombones, `FOLLOW CLINICALLY`, trois hommes qui se lèvent | l. 44763–45015 ; épilogue | RF23 | chapitre calme, sans combat |
| CAN-017 | Elvis Zaicenoks (personne réelle nommée dans l'avant-propos et le roman) | avant-propos ; l. 735 et suivantes | chapitres Jerma | **demande d'accord à documenter avant toute représentation** |
| CAN-018 | Motifs 117, 14:58 +2, 03:17, 017/066/117/404 ; grenade (fruit), jamais arme dans le texte | partout | toutes | détails de lieu, pas de mécanique |

## 6. RF02 — couverture visée

Éléments du passage l. 87–457 retenus pour RF02 (fiche : `docs/production/maps/RF02_FICHE.md`) : registres dans la
voiture d'enfant, formulaires brûlés au seau, porte close de la Santé et son affiche, **tramway** (valises, cage,
sacoche du receveur, ticket poinçonné), pancartes des abris, **pharmacie de Port-Royal ERREUR Ø frais**, matelas qui
avance seul dans le reflet, ambulances de Cochin, **TSF et reflet de l'Amiga (CAN-002)**, librairie et fiche de
lecteur (`JERMA - ERREUR Ø`), pont, **téléphone du barrage**, **valise de chaussures de la jeune femme**, colonne
Morris (Luna Park / JERMA PALACE), entrée du Luna Park. Figures humaines : demandées à Astra
(`docs/production/handoff/RF2-MAP-02/DEMANDE_ASSETS.md`).

## 7. RF01 accepté — éléments du texte absents et ajout borné proposé

Absents du build accepté : ERREUR Ø au crayon bleu dans le registre du vestibule (l. 19–23) ; remise du carton de
pointage, du bracelet 2026, de la montre et du flacon 117 (l. 11, 57) ; patient au ventilateur, infirmières (l. 27–85).
Proposition bornée (lot séparé, sans toucher parcours, combats, armes ni sons) : les effets rendus posés sur la table
de la chambre de départ (ramassage → objets portés), et la ligne `ERREUR Ø` ajoutée au texte du registre des
admissions. À faire après décision, en commit isolé, avec comparaison du WAD.

## 8. Journal

- 27/09 : matrice créée après lecture intégrale ; CAN-001 à CAN-004 : présence exigée, rien d'intégré.
