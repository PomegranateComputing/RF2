# Demande JERMA-V01 — Jerma Palace, arrivée (RF07 « Jerma - Façade maritime »)

| | |
|---|---|
| ID, version | JERMA-V01 (environnement seulement) |
| Priorité | P3 : la carte n'est **pas construite** tant que le propriétaire n'a pas tranché la présence hostile au Jerma (`docs/production/maps/RF07_FICHE.md`, « Question à trancher ») ; ce qui suit sert dans toutes les options |
| Base | ligne de production `prod/rf2-campaign` ; fiche RF07 ; conventions de LUNA-V01 (textures 4 px/u de loin, 8 px/u de près ; figures 512×448, 8 rotations, `Scale 0.18`, `grAb` aux semelles ; WAV 16 bits 48 kHz mono ; inscriptions composées avec une vraie police, jamais générées) |
| Texte | l. 733–861 (Jerma Palace, Marsaskala, 22 décembre 2022, 14:58). Rien après la l. 861 (quai, piscine, escarpin : RF09) |
| Pas dans cette demande | **Elvis** (personne réelle nommée ; figure seulement avec les références que fournira le propriétaire, CAN-017) ; toute présence hostile ; musique |

## Lieux et objets

| ID | Objet (lignes) | Forme, dimensions monde | États | Nom provisoire |
|---|---|---|---|---|
| M07-01 | Terrasse couverte de gravats ; la mer « dure, métallique, travaillée par le vent » sur tout l'horizon ; palmiers pliés (733) | sol 64×64 u ; ciel/horizon de mer (texture de ciel 1024×256 px) ; palmier en sprite 8 rotations, env. 24×160 u | — | `RF7_GRAV`, `RF7SKY`, `R7PA` |
| M07-02 | Ailes de béton ouvertes, façades crevées, balcons sans vitres (733) | façade 256×256 u, de loin (4 px/u) | — | `RF7_FAC1`, `RF7_FAC2` |
| M07-03 | Graffiti bleu NO FUTURE (733) | 128×48 u, masqué | — | `RF7_NOFU` |
| M07-04 | Chambre éventrée : moquette humide, sommier renversé ; ERREUR Ø sur la cloison à hauteur d'épaule, noir récent (739–743) | moquette (plat) ; sommier : modèle OBJ, env. 80×40×10 u ; inscription 96×32 u, masquée | — | `RF7_MOQU`, `R7SO`, `RF7_ERR1` |
| M07-05 | Couloirs : graffitis qui se recouvrent sans se supprimer, les anciens revenant là où la peinture neuve s'écaille ; sel, plâtre mouillé (757) | 3 textures de mur 128×128 u, raccordables ; une bande basse d'humidité | — | `RF7_GRF1…3` |
| M07-06 | Escalier de service : verre pilé et cendres sur les marches ; sommier rouillé qui obstrue la porte du palier, soulevé à deux, laisse une ligne noire sur les paumes (761) | plat 64×64 u ; sommier debout : modèle, env. 80×8×100 u | en place / écarté | `RF7_MARC`, `R7SR` |
| M07-07 | La chambre au matelas : fumée froide ; matelas qui brûle de l'intérieur sans flamme, petites poches orange dans les déchirures ; un ressort chauffé rougit (765–775) | matelas : modèle, env. 76×40×14 u, **deux états de braise** au moins ; ressort en image séparée | braises A / B ; éteint (porté) | `R7MA` |
| M07-08 | ERREUR Ø sur toute la largeur du mur derrière le lit, le mur fume autour du cercle barré (767–769, 795) | 192×64 u, masqué | — | `RF7_ERR2` |
| M07-09 | Carte de pointage 017 humide mais intacte, colonnes en violet, dernière ligne 06:06, tache de graisse en cercle barré dans l'angle ; la suie étalée quand Viktor l'essuie (813–819) | icône d'objet porté (même format que `RF4CART1`) ; objet au sol (sprite, 8 u) | tombée / essuyée (suie) | `graphics/items/RF7CART0`, `RF7CART1`, `R7CA` |
| M07-10 | NE PAS OUVRIR POUR VÉRIFIER, en français, très bas, presque au niveau du sol, sous des couches de graffitis (833) | 128×16 u, masqué, pour une ligne au ras du sol | — | `RF7_NPAS` |
| M07-11 | Le téléphone : application jamais installée, vignettes grises ; la première nommée `jerma_error_zero_0001.png` ; compteur en haut 17, 66, 117, 404 (837) | image plein écran de téléphone (HUD), 540×960 px, et quatre états du compteur | 17 / 66 / 117 / 404 | `graphics/hud/RF7TEL0…3` |
| M07-12 | Anciennes cuisines : carreaux blancs jusqu'à l'épaule, jaunis autour des hottes, verdis près du sol ; chambres froides ouvertes, portes d'acier pendues à des charnières rouges de rouille ; l'une avec des rayonnages, l'autre avec un fauteuil de plage, un masque de plongée et des centaines de bouchons en plastique triés par couleur (849) | murs 128×128 u (8 px/u) ; porte de chambre froide 64×112 u ; accessoires en sprites ou petits modèles | — | `RF7_CUIS`, `RF7_CFRO`, `R7FA`, `R7MQ`, `R7BO` |

## Sons (aucune musique)

| ID | Son (lignes) | Forme |
|---|---|---|
| S07-01 | La mer frappe la digue « avec un bruit de portes qu'on ferme » (827) | boucle 10–20 s, sans clic |
| S07-02 | Le vent entre par les fenêtres vides, traverse les chambres (827) | boucle |
| S07-03 | Une alarme, quelque part : un bip unique, rien ne suit (827) | un coup |
| S07-04 | Le matelas qui se consume par l'intérieur (765) | boucle courte, crépitement sourd |
| S07-05 | Quelque chose glisse à l'intérieur du matelas, bruit mat ; plus tard plus long, métallique ou osseux (785, 801) | deux sons |
| S07-06 | Un ressort grince contre la rampe (835) | un coup |
| S07-07 | Dans la chambre derrière eux, quelque chose tombe avec la lourdeur d'un sac mouillé (835) | un coup, lointain |
| S07-08 | Le téléphone vibre dans la poche (837) | un coup |
| S07-09 | Aux portes du couloir : une semelle frotte, un vêtement bouge (799) | trois variations, très bas |

Ordre utile : M07-07, M07-08, M07-09, M07-04, M07-06, puis le reste ; sons S07-01, S07-04, S07-05. Même remise que
LUNA-V01 (un dossier par lot, manifeste avec `target_relpath`, `SHA256SUMS.txt` en fins de ligne LF).
