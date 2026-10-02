# Éléments du roman — rapprochement avec le build courant (02/10/2026)

Matrice rapprochée : `ELEMENTS_ROMAN.csv` du pack `RF2_ASTRA_ART_MASSIF_20261002` (143 lignes). Build lu : branche `prod/rf2-campaign`, commit `f43d3fce` (même contenu de jeu que `61d9b431` : les deux commits suivants n'ajoutent que des documents et des scripts de production) : sources des cartes (`scripts/mapkit/*.py`), cartes construites (`src/maps/RF0x.wad`), textes (`src/LANGUAGE`), scènes (`src/zscript/rf/*.zs`). Détail ligne par ligne : `ELEMENTS_ROMAN_RAPPROCHEMENT.csv`, dans ce dossier.

**Lecture seule : rien n'a été lancé dans le moteur.** Les statuts viennent des sources et du contenu des cartes construites, pas d'une traversée. Une ressource dessinée par l'intégrateur en attendant celle d'Astra ou de Codex compte comme `INCOMPLET` (la scène fonctionne, l'art reste à livrer).

**Numéros de ligne : ceux du commit `f43d3fce`** (161 références contrôlées contre ce commit). L'arbre de travail bougeait pendant la lecture (flaques passées en images à plat, pochoir 404 déplacé : `luna_park.py`, `rf05.py`, `rf06.py`, `luna.zs`, `materials_rf04.py`, `MAPINFO`, non commités) ; ces modifications décalent quelques lignes de ces six fichiers et ne changent aucun statut.

## Comptes

| Périmètre | PRESENT | INCOMPLET | ABSENT | Total |
|---|---:|---:|---:|---:|
| **Les 143 lignes** | **19** | **31** | **93** | **143** |
| RF01 | 0 | 5 | 2 | 7 |
| RF02 | 8 | 5 | 0 | 13 |
| RF04 | 6 | 4 | 0 | 10 |
| RF05 | 3 | 10 | 0 | 13 |
| RF06 | 2 | 3 | 0 | 5 |
| Jerma (RF07-RF12) | 0 | 4 | 16 | 20 |
| Lieux ultérieurs | 0 | 0 | 75 | 75 |
| dont priorité P1 (91 lignes) | 16 | 24 | 51 | 91 |
| dont cartes produites, RF01 à RF07 (52 lignes) | 19 | 31 | 2 | 52 |

Rattachement des lignes à un lieu : une ligne à plusieurs lieux (`RF01/RF04`, `RF02/RF05`…) est comptée au premier ; « Jerma » regroupe EL049 à EL068, dont seules EL049 à EL052 tombent dans RF07 (roman P00612 à P00627), les seize autres dans RF08 à RF12, non produites ; « lieux ultérieurs » = EL069 à EL143, y compris les lignes documentaires sur le Jerma et `RF01/fin` (EL143, dernier état de Sainte-Anne, après RF23).

## P1 incomplets ou absents dans les cartes produites, avec la proposition

24 lignes. Les propositions respectent les décisions en vigueur : RF06 et le Jerma sans combat ; Elvis, le gardien, la jeune femme et les couples jamais des cibles ; aucune musique nouvelle ; rien d'expliqué que le roman laisse ouvert. Pour RF01 (carte acceptée), elles reprennent le lot borné de `CANON_FIDELITE.md` §7 et attendent un accord.

### RF01

- **EL002 — Montre arrêtée et changement 6h20/6h06** (INCOMPLET, lot V01). Manque : La montre comme objet : remise à Sainte-Anne (RF01), portée, montrée arrêtée à 6 h 20 puis à 6 h 06 au pointage ; aucun cadran, aucune icône de HUD avant RF07.
  Proposition : RF01 : la montre arrêtée posée avec les autres effets rendus sur la table de la chambre de départ (scripts/mapkit/rf01.py:259), à ramasser avant de sortir (lot borné déjà proposé en CANON_FIDELITE §7, à faire après accord puisque RF01 est acceptée). RF04 : au moment du pointage, afficher le cadran à l'écran comme la montre de RF07 (jerma.zs:241) : aiguilles à 6 h 20, puis à 6 h 06 quand le carton sort de l'horloge.
- **EL006 — Flacon brun 117** (INCOMPLET, lot J02). Manque : Le flacon brun à l'étiquette 117 comme objet : remis dans RF01, porté, bu (RF02), donné à la jeune femme puis rendu (RF05) ; aucune image, aucun objet d'inventaire.
  Proposition : RF01 : le flacon brun (étiquette blanche, 117 à l'encre violette) et le paquet de biscuits posés sur le poste des infirmières du pavillon est (scripts/mapkit/rf01.py:379), à ramasser, avec la ligne « Prenez ça. Pas tout d'un coup. » ; après accord (RF01 acceptée). RF05 : pendant RF_RF05_WOMAN_7, montrer le flacon à l'écran, moins plein quand elle le rend.
- **EL007 — Carton017 à lettres bleues** (INCOMPLET, lot J02). Manque : La remise à Sainte-Anne (RF01 : rien), le carton montré à l'infirmière, porté dans RF02 (il n'est donné qu'à l'entrée de RF04) ; les états du Jerma (humide, suie, tache de graisse en cercle barré, tombé du matelas) relèvent de RF08, non produite.
  Proposition : RF01 : le carton LUNA PARK - PERSONNEL TECHNIQUE, 017, parmi les effets rendus sur la table de la chambre de départ (scripts/mapkit/rf01.py:259), ramassé (donne RFTimeCard) ; icône du HUD gardée de RF01 à RF04 (lever la condition « RF04 » de hud.zs:336) ; après accord (RF01 acceptée). Rien à ajouter dans RF07 : la chute du carton est dans RF08.

### RF02

- **EL013 — Enveloppe de Cochin** (INCOMPLET, lot F01). Manque : RF02 : la scène (« Monsieur Ardent, vos résultats. » … « Gardez-les. » … « Quand vous saurez, revenez. »), l'adresse à moitié masquée par le pouce. RF05 : l'enveloppe définitive (fenêtre, typographie, adresse lisible) ; la main qui la tient manque puisque la jeune femme n'a pas de figure.
  Proposition : RF02 : une ligne de marche sur le boulevard de Port-Royal à hauteur du portail (x 1216) lance l'échange en sous-titres comme les autres scènes de RFParis ; la femme reste devant le portail, l'enveloppe ne se ramasse pas ; la vague E3 (rf02.py:384-385) ne se réveille qu'après la dernière réplique. RF05 : remplacer R5ENA0 par l'enveloppe d'Astra et la rendre lisible (LIRE) sur l'établi : nom derrière la fenêtre, Waukegan, Illinois, 117 ; elle reste non ouverte.
- **EL014 — Amiga au reflet puis Ducretet** (INCOMPLET, lot R01). Manque : Le maître d'Astra de l'Amiga 1200 pour le reflet ; le poste Ducretet couvert de poussière qui « lui renvoie son visage » à l'approche (la vitrine finale montre des postes génériques, sans Ducretet ni reflet).
  Proposition : Garder le déclenchement actuel. Remplacer RF2_AMIG par l'image composée depuis le maître d'Astra, et ajouter à l'état final de la vitrine un Ducretet poussiéreux à l'emplacement exact où le boîtier gris apparaissait, pour que le joueur voie l'un céder à l'autre en s'approchant.

### RF04

- **EL021 — Gardien avec registre puis guérite vide** (INCOMPLET, lot F01). Manque : La figure définitive du gardien (casquette, moustache blanche, registre sur les genoux, doigt noir de graisse) ; le registre resté sur la chaise, ouvert à une page blanche, n'existe que dans le texte.
  Proposition : Même place et même scène. Remplacer R4G1 par la figure d'Astra (assis, parle, tend la main, désigne le crochet). Après sa disparition, laisser dans la guérite, visible par la vitre depuis le chemin, la chaise et le registre ouvert sur une page blanche (objet fixe, sans interaction). Le gardien n'est jamais une cible.
- **EL028 — Tourniquet 617/618** (INCOMPLET, lot A03). Manque : RF05 : scripts/mapkit/rf05.py ne repose ni les tourniquets ni le compteur (aucun RF4_TOUR ni RF4_C618 dans src/maps/RF05.wad) ; le joueur qui sort de la salle de danse par le vestibule ne trouve plus rien à leur place. Les montants (RF4_TOUR) sont un substitut de l'intégrateur.
  Proposition : RF05 : reposer sous la marquise les trois tourniquets de RF04 (mêmes positions que rf04.py:273-278), la barre levée et le compteur resté à 618 (RF4_C618), sans interaction : le joueur qui repasse voit le chiffre qu'il a laissé.
- **EL030 — Jukebox muet THE SKY IS EMPTY** (INCOMPLET, lot A03). Manque : L'objet définitif dans ses états (sous la bâche, découvert : vitre fendue, touches jaunies, liste effacée, étiquette lisible).
  Proposition : Même place, même suite de gestes (retirer la bâche, lire, appuyer : rien, trois coups). Remplacer R4JB par le juke-box d'Astra en deux états, plus un troisième, allumé, pour RF05 (luna_machines.zs:30-34) ; aucune musique nouvelle, le sous-titre reste.

### RF05

- **EL031 — Escalier et ampoule grillagée** (INCOMPLET, lot A02). Manque : L'ampoule et sa grille n'existent pas comme objet : la lumière est un point lumineux sans source visible ; mains courantes et conduites de cuivre ne sont qu'une image plate provisoire.
  Proposition : Au palier (rf05.py:173-174), poser sur le mur une applique visible : ampoule nue derrière une grille de fil, allumée, à l'endroit du point lumineux actuel ; remplacer RF5_ESCA par les surfaces d'Astra. Le joueur descend, rien à actionner.
- **EL035 — Levier et ATTENTE gravé** (INCOMPLET, lot A02). Manque : Le levier n'est jamais vu sur ATTENTE : à l'arrivée il est dessiné sur MARCHE, alors que le roman le trouve à la troisième position (« Le levier se trouvait là ») ; pas de troisième image ; bakélite et gravure provisoires.
  Proposition : Même panneau. Trois images : à l'arrivée, moteur battant, la manette à mi-course sur ATTENTE ; ARRÊT après le premier usage ; MARCHE à la remise en route. Remplacer RF5_LEVM/RF5_LEVA par le levier d'Astra ; textes inchangés.
- **EL036 — Jeune femme pieds nus et enveloppe** (INCOMPLET, lot F01). Manque : La jeune femme elle-même : sa descente dans le cercle de l'ampoule, pieds nus et noirs de poussière, le talon blessé, assise sur la caisse, la main sur le mur ; la scène de soin n'est pas visible.
  Proposition : Sous-station, après ARRÊT : la figure d'Astra (la même personne que F02-07 de RF02, sans valise, pieds nus) apparaît en haut de l'escalier dans le cercle de l'ampoule, descend, s'assoit sur la caisse (rf05.py:202), examine son talon, remonte et pose la main sur le mur du palier. Figure sans collision, jamais une cible ; la vague des galeries reste retenue jusqu'à son départ (déjà le cas, luna_machines.zs:354-361).
- **EL038 — Graisse, clé17 et fibre synthétique** (INCOMPLET, lot A02). Manque : Aucun de ces objets n'est visible : ni chiffons, burette et clé de 17 dans le tiroir, ni graisse durcie, ni fragment de fibre rouge au fond du palier ; les pièces portées n'apparaissent pas dans le HUD.
  Proposition : Atelier : un tiroir ouvert montrant chiffons, burette et clé plate de 17 (objet fixe, vidé après usage). Moteur : au nettoyage, le capot du palier ouvert et, dans la graisse noire, le fragment rouge à regarder de près (LIRE) avant de l'ôter. L'action reste la même : trouver, revenir, nettoyer.
- **EL039 — Toile et agrafes cuivre sur courroie** (INCOMPLET, lot A02). Manque : La courroie renforcée n'a pas d'image propre : la roue et sa courroie sont les mêmes avant et après (RF5_ROU0/ROU1, RF5_ROUS à l'arrêt, avec la seule réparation ancienne) ; ni la fente, ni la bande de toile agrafée ne se voient ; la toile et les agrafes ne sont pas visibles dans la caisse.
  Proposition : Galerie nord : la caisse ouverte avec la bande de toile et les agrafes de cuivre visibles. Sous-station : après la réparation, la roue passe à une variante de RF5_ROU (arrêtée et en marche) où la courroie porte la bande de toile et ses agrafes de cuivre ; à l'arrêt avant réparation, une variante où la fente à mi-largeur se voit.
- **EL040 — Fusible JERMA daté 22.12.2022** (INCOMPLET, lot A02). Manque : Le fusible définitif : la date 22.12.2022 ne se lit que dans le texte, pas sur la porcelaine ; la boîte de rechange n'est pas visible ; tableau provisoire.
  Proposition : Salle des transformateurs : une boîte de rechange visible où un seul cylindre de porcelaine a la bonne taille ; à l'usage, montrer le fusible de près avec 22.12.2022 imprimé. Tableau : remplacer RF5_FUS0/FUS1 par celui d'Astra, le fusible daté visible une fois inséré dans la ligne JERMA.
- **EL041 — Lampes retardées et enseignes fragmentées** (INCOMPLET, lot A03). Manque : Les ampoules sont des points lumineux sans globe visible ; une seule enseigne, fixe une fois allumée : les fragments LUNA. PARK. NIAG. BROOK. qui clignotent par morceaux ne sont que dans le sous-titre.
  Proposition : Parc rallumé : aux quatorze points (rf05.py:299-303), des globes fendus visibles, éteints puis allumés avec leur retard. Quatre enseignes en ampoules qui s'allument par morceaux, chacune à sa place : LUNA et PARK sur les rochers de la ruelle, NIAG au-dessus de la rampe du bassin, BROOK sur la façade du pont ; jamais le nom entier.
- **EL042 — Train vide de trois voitures** (INCOMPLET, lot A03). Manque : Le train définitif (trois wagonnets, roues, inertie) : aujourd'hui une image plate tournée vers le joueur ; il ne parcourt que la rampe de levage.
  Proposition : Même trajet au-dessus de la ruelle. Remplacer le panneau R5TRA0 par le train d'Astra (trois voitures rondes à deux places, vides), vu de côté et de dessous ; garder le claquement du frein à chaque passage ; le joueur reste à distance, rien à actionner.
- **EL043 — Couples uniquement dans les miroirs** (INCOMPLET, lot F01). Manque : Les couples eux-mêmes dans les miroirs : costumes de plusieurs époques, le couple à l'écart près du juke-box, visages hors champ, la femme qui retire une chaussure.
  Proposition : Salle de danse de RF05 : des couples visibles seulement dans les miroirs (même procédé que le reflet de Viktor, figures.zs:65), placés sur le parquet derrière le joueur pendant la scène d'entrée ; un couple à l'écart près du juke-box, cadré bas, visages hors champ, elle retire une chaussure. Rien dans la salle si le joueur se retourne ; aucune collision, jamais des cibles, aucune musique nouvelle.

### RF06

- **EL045 — 117/404/017 barrés** (INCOMPLET, lot A04). Manque : Les pochoirs définitifs, avec des états distincts (peint, puis barré) et une peinture à l'échelle du mur.
  Proposition : Mêmes portes, même ordre. Remplacer les trois images par les pochoirs d'Astra, la barre visiblement posée après le chiffre et d'une autre main ; observation de passage, rien à actionner.
- **EL046 — Langues et ERREUR Ø en variantes** (INCOMPLET, lot A04). Manque : Les ERREUR Ø définitifs ; des graffitis où l'on reconnaisse plusieurs langues (anglais, français, maltais, italien, cyrillique) ; le texte src/LANGUAGE:288 RF_RF06_ERREUR n'est jamais affiché : aucune ligne de la carte ne porte la scène 5 (corridor.zs:101, absent de src/maps/RF06.wad).
  Proposition : Remplacer RF6_ER1 à RF6_ER5 par les cinq variantes d'Astra aux mêmes places. Dans la salle des peaux, poser sous la peinture soulevée des signatures, dates et initiales en cinq écritures, sans phrase inventée. Ajouter la ligne de marche de la scène 5 au premier ERREUR Ø (rf06.py:182) pour que le texte existant s'affiche ; rien n'est expliqué.
- **EL047 — Ampoules devant et derrière** (INCOMPLET, lot A04). Manque : L'ampoule nue elle-même (verre, culot, fil) : les lampes sont des points lumineux sans objet visible, on voit la lumière s'allumer et s'éteindre mais pas sa source.
  Proposition : À chaque point lumineux (rf06.py:193-194), pendre sous le plafond une ampoule nue visible à deux états, allumée et éteinte, commutée par RFCorridor.SetLamp avec sa lumière ; le joueur n'a rien à faire, il voit les ampoules s'éteindre derrière lui.

### RF07

- **EL049 — Terrasse et mer métallique** (INCOMPLET, lot J01). Manque : Les surfaces et objets définitifs : façade maritime, balcons sans vitres, baie cassée, gravats, palmiers, mer « dure, métallique ».
  Proposition : Garder le plan de la terrasse. Remplacer les huit textures RF7_* par celles d'Astra et les sept palmiers (rf07.py:107-109) par de vrais palmiers pliés par le vent ; la mer garde son horizon (rf07.py:104-105). Le joueur arrive, regarde, rejoint Elvis : sans combat.
- **EL050 — Elvis attend, guide et aide** (INCOMPLET, lot J02). Manque : La figure définitive d'Elvis (références du propriétaire) et ses gestes : attendre, se retourner, tendre la bouteille, porter. L'aide au-delà du sommier (matelas, photo, eau) est dans RF08-RF09, non produites.
  Proposition : Même parcours (rf07.py:169-171). Remplacer R7EV par la figure d'Astra : attente près de la baie, marche, tête tournée vers Viktor quand il attend, bras tendu pour la bouteille, prise du sommier. Jamais une cible, aucune collision.
- **EL051 — Chambre remplaçant le couloir** (INCOMPLET, lot J01). Manque : La chambre définitive : moquette humide, sommier renversé comme objet, un ERREUR Ø propre à ce mur, noir et récent.
  Proposition : Même pièce, même déclenchement au retournement. Habiller avec les surfaces d'Astra, remplacer le bloc par le sommier renversé, et peindre sur la cloison un ERREUR Ø noir, frais, à hauteur d'épaule, distinct des cinq du couloir. Rien ne dit où est passé le couloir.
- **EL052 — Sommier déplacé ensemble** (INCOMPLET, lot J02). Manque : Le sommier définitif (métal rouillé, poids) et l'effort à deux : Elvis ne fait aucun geste, l'objet glisse de 40 u d'un coup.
  Proposition : Même palier. Remplacer R7SB par le sommier d'Astra en deux états (en travers, relevé contre le mur) ; à l'usage, Elvis prend un côté (pose de portage) pendant que le joueur tient l'autre, le sommier pivote, puis « C'est là. ».

Hors de cette liste : les seize lignes du Jerma au-delà de RF07 (EL053 à EL068, dont 13 en P1) sont absentes parce que RF08 à RF12 ne sont pas produites ; leur implantation est déjà découpée dans `docs/production/maps/RF07_RF12_DECOUPAGE.md`.

## Doutes non levés

- **Reflets de Viktor (EL012, EL029), comptés PRESENT.** La matrice les donne « défaut signalé le 01/10 ». Le build contient les sprites de Codex importés ce jour-là (R2F8 V02, R4V2/R4V3 V01), au visage du maître du HUD. Le verdict du propriétaire sur ces images n'est écrit nulle part, et le lot V01 est redemandé à Astra : si ces images ne valent pas « maître actuel », les deux lignes passent à INCOMPLET.
- **Entrée du Luna Park (EL020), comptée PRESENT.** L'enseigne au U pendant et DÉFINITIVE barré sont dans RF02. RF04 ne montre que le revers des portes, d'un autre dessin (piliers à dômes de Codex contre palissade et grille dans RF02) : l'« entrée commune aux deux cartes » demandée par la matrice n'est pas faite.
- **Tourniquet (EL028), compté INCOMPLET** alors que la matrice le dit « présent rapporté » : l'action de RF04 est complète, mais RF05 ne repose pas les tourniquets. Si la ligne ne vise que RF04, elle est PRESENT.
- **Lumières sans source visible (EL031, EL041, EL047), comptées INCOMPLET.** Le comportement du roman est là (cercle de l'ampoule, allumage avec retard, ampoules devant et derrière, y compris après une sauvegarde), mais ce sont des points lumineux sans ampoule dessinée. À juger en jeu : si la lumière seule suffit, ces lignes remontent.
- **Couloir (EL044, EL048), comptés PRESENT** malgré des conduites faites d'un volume simple et des voix en sous-titres sans son ; l'ouverture sur le jour (RF6_JOUR) est provisoire.
- **Texte orphelin de RF06.** `RF_RF06_ERREUR` (src/LANGUAGE:288) n'est déclenché par aucune ligne de la carte (scène 5 absente de `scripts/mapkit/rf06.py` et de `src/maps/RF06.wad`) : oubli ou choix, non tranché.
- **Piscine et matelas vus depuis RF07 (EL062, EL053), comptés ABSENT.** RF07 montre une fosse de béton nu depuis la terrasse et une lueur dans la pièce de sortie ; ni mosaïque, ni slogans, ni matelas.
- **Origine de quelques images.** Les tables de contrat du 02/10 notent « Opus ou référence antérieure » pour la pointeuse et les compteurs 617/618 ; `scripts/mapkit/materials_rf04.py:39-41` les donne livrés par Astra (tranche 01 du 30/09) : je les ai tenus pour livrés. Les images procédurales de RF02 ne sont pas marquées provisoires (sauf RF2_AMIG) et le pack dit RF02 jugée bonne par le propriétaire le 01/10 (`00_LIRE_DABORD.md`) : leurs éléments sont comptés PRESENT.
- **Objets portés invisibles.** Ticket, fiche de lecteur, enveloppe, chiffons, toile, fusible et bouteille d'eau sont des objets d'inventaire sans image ni ligne de HUD (seuls les clefs et le carton s'affichent, `src/zscript/rf/hud.zs:316-340`). Je n'en ai pas fait un motif d'INCOMPLET pour les lignes de RF02 ; il pèse sur EL038 à EL040.
- **EL143 (`RF01/fin`)** est rangée dans les lieux ultérieurs et laissée sans proposition : c'est l'état final de Sainte-Anne, à implanter avec la fin du jeu, pas dans le premier chapitre.
