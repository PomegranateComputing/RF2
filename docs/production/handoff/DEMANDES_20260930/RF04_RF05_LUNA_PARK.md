# Demande LUNA-V01 — ressources du Luna Park (RF04 « Personnel technique », RF05 « Les machines continuent »)

| | |
|---|---|
| ID, version | LUNA-V01 |
| Priorité | P2 (les cartes sont construites en parallèle avec des ressources provisoires d'Opus, marquées comme telles ; tes fichiers les remplacent sous les mêmes noms) |
| Base | ligne de production `prod/rf2-campaign` (`23808c6` et suivants) ; fiches `docs/production/maps/RF04_FICHE.md` et `RF05_FICHE.md` (lignes du roman citées) |
| Identifiants | Luna Park = RF04 (décision du propriétaire du 27/09) ; RF03 « Batignolles » reste pour plus tard ; RF05 suit ; le couloir ERREUR Ø vers le Jerma sera RF06 « La sortie du personnel » |
| Texte | l. 451–707 du roman ; ce qui appartient au second passage (parc réquisitionné, porte 117, infirmerie) et au fil de juin 1940 (brassard T.D., effets personnels) n'apparaît pas ici |

## Conventions (les mêmes que RF02)

- **Figures** : PNG 512×448, 8 rotations (`A1…A8`), `Scale 0.18` comme les ennemis, `grAb` aux semelles ; jamais
  hostiles, jamais utilisables ; manifeste avec `target_relpath`.
- **Textures** : 4 px par unité pour les façades et ce qui se voit de loin, 8 px par unité pour ce qui se voit de
  près ; dimensions monde données ci-dessous ; bloc `TEXTURES` proposé pour chaque image (comme `TEXTURES.six_replacements.txt`).
- **Modèles** : OBJ + atlas comme le landau et le tram de RF02 ; taille monde et origine (au sol, au centre) indiquées.
- **Sons** : WAV 16 bits, 48 kHz, mono ; boucles sans clic de raccord ; **aucune musique** (le juke-box qui joue en
  RF05 reste un sous-titre).
- Inscriptions : texte exact du roman, composé avec une vraie police, jamais généré en image.

## RF04 — personnel technique

| ID | Objet (lignes) | Forme, dimensions monde | États | Nom provisoire d'Opus |
|---|---|---|---|---|
| F04-01 | Le gardien : silhouette large, casquette d'employé, moustache blanche, registre sur les genoux, assis (467) | figure assise, 8 rotations | A lit le registre ; B lève la tête et parle | `sprites/rf04/R4G1*` |
| F04-02 | Reflet de Viktor en blouse grise d'ouvrier (533) | figure debout, vue seulement dans les miroirs (comme F02-08) | A | `R4V2*` |
| F04-03 | Reflet de Viktor en chemise claire tachée sous le bras, badge plastique à la ceinture (533–537) | idem | A | `R4V3*` |
| M04-01 | Guérite : planches, vitre sale ; ERREUR Ø tracé au doigt gras sur la vitre (467, 515–517) | textures : paroi 64×128 u ; vitre 48×40 u | vitre propre / vitre au ERREUR Ø | `RF4_GUER`, `RF4_VIT0`, `RF4_VIT1` |
| M04-02 | Pointeuse fixée au mur (481) ; carton de pointage n° 017 `LUNA PARK - PERSONNEL TECHNIQUE`, heure imprimée en violet 06:06 | texture 32×48 u ; icône d'objet porté | carton non pointé / pointé 06:06 | `RF4_POIN`, `graphics/items/RF4CART0`, `RF4CART1` |
| M04-03 | Crochet de clefs, étiquettes de cuivre ATELIER, PISTE, SOUS-STATION, CHAMBRE FROIDE ; la dernière, plus claire, gravée JERMA (495) | texture 48×32 u | cinq clefs / sans SOUS-STATION | `RF4_CLE5`, `RF4_CLE4` |
| M04-04 | Décor de pont suspendu BROOKLYN BRIDGE, lettres rouges sur fond gris, planches (523) | façade 256×192 u | — | `RF4_BROO` |
| M04-05 | Couloir technique encombré de câbles derrière le décor (523) | paroi 128×96 u | — | `RF4_CABL` |
| M04-06 | Bassin vide, ligne d'algues sèches à hauteur d'épaule ; pancarte LES CHUTES DU NIAGARA ; rochers de décor de la cascade (523) | paroi de bassin 128×96 u (ligne d'algues à 48 u du fond) ; pancarte 128×32 u ; rocher 128×128 u | — | `RF4_BASS`, `RF4_NIAG`, `RF4_ROCH` |
| M04-07 | Chaussure d'enfant : cuir blanc, boucle latérale, semelle presque neuve, dans une flaque noire (523–525) | sprite ou petit modèle, 10 u de long ; flaque (plat) | — | `R4SH`, `RF4_FLAQ` |
| M04-08 | Marquise éventrée ; tourniquets, l'un avec un compteur mécanique 617 (531) | toile (plat et côté) ; tourniquet : modèle ou textures 32×40 u | compteur 617 / 618 | `RF4_MARQ`, `RF4_C617`, `RF4_C618` |
| M04-09 | Salle de danse : parquet gondolé, miroirs piqués, lumière par fragments (533) | plat parquet 64×64 u ; miroir (cadre et tain piqué, compatible avec une ligne miroir) 64×96 u ; colonne | — | `RF4_PARQ`, `RF4_MIRO`, `RF4_COLN` |
| M04-10 | Juke-box muet sous une bâche ; vitre fendue, touches jaunies, liste effacée, une étiquette lisible THE SKY IS EMPTY (541–545) | modèle ou sprite 8 rotations, env. 40×24×64 u | sous bâche / découvert (RF05 : éclairé, en marche) | `R4JB` |
| M04-11 | Charpente des montagnes russes (poteaux, contreventements), voie, quai d'embarquement (551, 693) | textures bois 64×128 u, voie (plat) | — | `RF4_BOIS`, `RF4_VOIE` |
| M04-12 | Affiches déchirées : femmes plongeant dans des bassins, automobiles sur une piste inclinée, acrobates, un champion de boxe (455) | 48×64 u chacune | — | `RF4_AFF1…4` |
| M04-13 | Porte de la sous-station (fer), passage herbeux entre les dalles (551) | porte 64×96 u ; plat herbe/dalles | — | `RF4_PSST`, `RF4_DALH` |
| M04-14 | Chemin de service envahi d'herbes, rails étroits sur traverses (463) | plats 64×64 u | — | `RF4_HERB`, `RF4_DECA` |

Sons RF04 : `S04-01` ambiance du parc (bois mouillé qui travaille, toile, grondement lointain déformé en manège, l. 461) ;
`S04-02` le moteur sous le parc : deux pulsations, une pause, une troisième plus longue, courroie qui claque (529,
559) ; `S04-03` pointeuse (481) ; `S04-04` clef décrochée, étiquettes de cuivre ; `S04-05` barre de tourniquet et
compteur ; `S04-06` touche de juke-box sans effet ; `S04-07` les trois coups du moteur (549) ; `S04-08` serrure dure
qui cède d'un coup (551) ; `S04-09` le rail tiède qui vibre sous la main (463). Noms provisoires : `sounds/luna/*.wav`.

## RF05 — les machines continuent

| ID | Objet (lignes) | Forme | États |
|---|---|---|---|
| F05-01 | La jeune femme de Sainte-Anne, sans valise, pieds nus noirs de poussière, petite blessure sous le talon ; robe claire (587–655) | figure 8 rotations (même personne que F02-07) | A debout ; B assise sur une caisse, examine son talon ; C main posée sur le mur |
| F05-02 | Dans un miroir de la salle de danse : couples de plusieurs époques (costumes, robes, jeans, uniformes, silhouettes floues) ; un couple près du juke-box, visages hors cadre, la femme retire une chaussure, lumière jaune de vidéo domestique (697–701) | figures vues seulement dans les miroirs ; 4 images de danse par couple | jamais des cibles ; le couple n'est **pas** identifié (CAN-004 : « M. & L. » seulement plus tard) |
| M05-01 | Escalier, mains courantes gonflées, conduites de cuivre verdies ; ampoule derrière une grille, cercle de lumière (555) | textures | — |
| M05-02 | Sous-station voûtée : tableaux de marbre, couteaux de coupure, cadrans, fusibles de porcelaine, gaines goudronnées (559) | textures + modèles | — |
| M05-03 | Moteur électrique, roue lourde, courroie de cuir avec réparation ancienne ; puis renforcée de toile et d'agrafes de cuivre (559, 667) | modèle animé (deux tours, hésitation, reprise) | en marche / arrêté / renforcé |
| M05-04 | Cadrans GRAND HUIT, CHAMBRE DES GLACES, SALLE DE DANSE, POMPES, ÉCLAIRAGE EXTÉRIEUR, JERMA (561, 683) | textures avec aiguilles | trop haut / zéro / hors échelle |
| M05-05 | Coffret noir sans plaque, languette NODE 0 au feutre blanc ; cartes minces, diodes, ventilateurs de 40 mm (561–565) | modèle | fermé / ouvert ; diodes vertes / rouges |
| M05-06 | Levier en bakélite, positions MARCHE, ATTENTE (gravé à la pointe), ARRÊT (571–573) | modèle | trois positions |
| M05-07 | Établi, chiffons, burette, clé plate de 17, spatule, tournevis, bidon de graisse, caisse (629, 661) | modèles ou sprites | — |
| M05-08 | Boîte de fusibles de rechange ; le fusible de porcelaine blanche imprimé 22.12.2022 (669) | sprite ou modèle | — |
| M05-09 | Train de trois voitures des montagnes russes, vide ; frein automatique (693) | modèle | roule / freine |
| M05-10 | Enseignes qui clignotent par morceaux : LUNA. PARK. NIAG. BROOK. ; ampoules sous des globes fendus (691) | textures | éteint / allumé par morceaux |

Sons RF05 : arrêt du moteur (la courroie claque trois fois), silence habité (gouttes, petits mouvements dans les murs,
circulation lointaine) ; redémarrage (sursaut, quart de tour, reprise) ; diodes et ventilateurs ; ampoules qui
s'allument avec retard ; moteurs secondaires et pompes ; train et frein automatique.

## Ce qu'Opus fait pendant ce temps

Les cartes RF04 et RF05 sont construites maintenant (géométrie, parcours, scènes, rencontres, transitions) avec des
ressources provisoires procédurales portant les noms ci-dessus ; elles restent « finition artistique ouverte ».
Chaque livraison est importée par contrôle d'empreintes, regardée dans le moteur, et renvoyée avec le tic et la
capture exacts si quelque chose ne va pas.
