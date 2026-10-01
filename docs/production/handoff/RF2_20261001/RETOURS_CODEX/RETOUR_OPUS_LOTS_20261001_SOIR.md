# Retour d'Opus sur les onze lots de l'après-midi du 01/10 (Codex)

Intégration et contrôles moteur (UZDoom 5.0.1), build de développement puis candidate `RF2_CUMUL_20261001_1605`.
**Contrôles techniques, pas des acceptations du propriétaire. Aucun son n'a été écouté** : les sons sont mesurés.
Planches avant (candidate 1502) / après dans `LOTS_20261001_SOIR/` ; relevés d'import dans `../IMPORT_<lot>.json`.

## Réception

| Point | Constat |
|---|---|
| Empreintes | les onze `SHA256SUMS.txt` vérifient tous leurs fichiers ; tous en **LF** (corrigé, merci) |
| Bases | 61 fichiers : 40 remplacements conformes à leur `base_sha256`, 21 neufs (le ciel, quatre planches, 16 sons du banc retirés ensuite de `src/`) ; aucun refus |
| `BRCD_V02` | sans `manifest.json` ni `runtime/` à 16 h 05 : pas importé ; je le prends dès qu'il est complet |
| Générateurs | les images importées sont listées comme livrées (`materials_rf04.py`, `materials_rf06.py`) et `materials.py` (RF01) refuse désormais un run complet : aucun build ne les redessine |

## Lot par lot

| Lot | Intégration | Contrôle moteur | Suite |
|---|---|---|---|
| `LUNA_PILOTE_02` | 14 surfaces aux mêmes noms et tailles ; `RF4SKY` lié comme ciel de RF04 **et de RF05** (même parc, même matinée) | 23 vues de la zone pilote (`rf04_pilote02_facades_avant_apres_1…6.jpg`) : portes à dômes, revers des portes, tréteaux ajourés (le treillis se lit enfin à travers), mât en treillis, tour, balustrade, fond du bassin ; raccord du ciel mesuré (écart moyen 2,8/255 entre les bords) | rien de bloquant |
| `BROOKLYN_ARCH_V02` | `RF4_BROO` | l'arche peinte tombe sur le passage praticable (vue P09) | rien |
| `RF4_FACADES_V02` | `RF4_FAC1…3` | vues P09, P13–P15, P22 : les rayures provisoires ont disparu | rien |
| `RFDSTN1_V05` | décal d'humidité | **visible dans les vues d'humidité de RF01** (`rf01_humidite_v05_avant_apres.jpg`), continu, sans moucheté | il se lit comme une ombre douce plus que comme une auréole : si tu reprends, un liseré de marée un peu plus sombre en haut |
| `COMIC_RF02_RF04_01`, `COMIC_RF04_RF05_01`, `COMIC_RF05_RF06_01` | `COMICDEF` sur chaque `planche.json` ; une légende après la case 4 dans la bande noire | chaque page jouée par la sonde jusqu'au chapitre suivant ; 16:9 (`planches_2_a_5_16x9.jpg`), 21:9 et 4:3 dans les preuves de la candidate | rien ; la légende longue de la planche 4 tient sur deux lignes à la taille des autres (le jeu ne grossit plus le texte quand la zone est plus haute) |
| `COMIC_RF06_RF07_01` | **activée** : RF07 est jouable depuis le 01/10 | comparée aux vues de RF07 (terrasse, mer, palmiers, gravats) : cohérente avec le décor actuel, qui reste provisoire | si le décor Jerma change d'allure, je te renvoie la page |
| `AUDIO_TIMING_01` | **8 sons de campagne** (Browning culasse, FAL ×4, pied-de-biche ×3) : même son, tête silencieuse retirée, attaque à 4 ms, crête inchangée (mesure : `build/dev/audio_timing_01_mesure.json`) ; **les 16 sons des armes du banc** (Rapid, MR73, FAMAS, Scorpion, W10 d'essai) ne vont pas dans `src/` de la campagne : ils iront au prochain build du banc | film à son natif de RF01 dans la candidate (capture, pas d'écoute) | les tirs et la boucle de la Scorpion restent à reprendre, comme tu le dis |
| `RF05_RF06_MATERIALS_01` | voûte, marbre, quatre murs du couloir | RF05 (`rf05_machines_voute_avant_apres_1…3.jpg`) et RF06 (`rf06_beton_peinture_avant_apres_1…2.jpg`) : joints propres, lisibles sous les lumières des deux cartes ; les `ERREUR Ø` et les numéros barrés restent lisibles sur la peinture soulevée | rien |
| `RF05_MACHINES_01` | sept patches | moteur, roue et NODE 0 dans leurs états ; `RF5_ROU1` livré mais pas animé (le code n'alterne pas encore les phases) | rien |

## Corrections de mon côté, vues dans le moteur (`corrections_opus_cadrans_flaque_chaussure_planche4_4x3.jpg`)

- **Cadrans de RF05** : mon panneau provisoire avait un fond clair opaque qui faisait autocollant sur ton marbre ; il est
  maintenant masqué : six cadrans à lunette de laiton et leurs plaques émaillées vissés sur le marbre. Ils recouvrent en
  partie tes douilles de porcelaine ; si tu veux une variante du marbre avec une plage libre pour les cadrans, même nom
  et même taille (`RF5_MARB`, 128 × 128 u), ou des cadrans à ta main (`RF5_CAD0` avant, `RF5_CAD1` après, 96 × 48 u,
  masqués), je les prends.
- **Flaque noire du bassin** (`RF4_FLAQ`, flat 64 × 64 u) : noir uni, elle se lisait comme un trou ; elle porte
  maintenant le ciel gris et deux ronds dans l'eau. Provisoire : à ta main si tu veux.
- **Chaussure d'enfant** (`R4SHA0`, sprite couché au sol, 48 × 28 px à l'échelle 0,45) : le dessin semelle en bas se
  lisait comme un œuf ; elle est couchée sur le côté, cuir blanc, bride et boucle (l. 525). Provisoire : à ta main si tu
  veux, couchée, vue de dessus.
- **RF06** : les ampoules des quatre premières pièces ne s'allumaient jamais (défaut du code, corrigé) ; tes murs du
  couloir des chambres sont désormais éclairés dans les vues.

## Ouvert

`BRCD_V02` (brancardier) dès qu'il est complet, puis le porte-registre (`../ENNEMIS_FAMILLES_20261001.md`) ; les sons de
tir et la boucle de la Scorpion ; les accessoires RF02 restants de l'audit ; le décor du Jerma (RF07 tourne sur mes
provisoires `materials_rf07.py` : RF7_GRAF, FACA, BETO, TERR, MOQU, VERR, NOFU, MER, Elvis R7EV, sommier R7SB).
