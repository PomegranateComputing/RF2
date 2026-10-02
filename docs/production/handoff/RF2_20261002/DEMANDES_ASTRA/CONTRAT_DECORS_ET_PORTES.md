# Décors, portes et façades — ce que le moteur attend

Tables par lot : `CONTRATS/A02_RF05_FICHIERS.csv`, `A03_LUNA_FICHIERS.csv`, `A04_RF06_FICHIERS.csv`, `R01_RF02_FICHIERS.csv`,
`R02_RF01_FICHIERS.csv`, `J01_J02_JERMA_FICHIERS.csv`. La colonne `origine` dit qui a fait le fichier en place : un lot
nommé (à préserver, reprendre sur défaut précis) ou « Opus » (provisoire, à remplacer).

## Échelle monde

- 32 u = 1 m (Viktor : 56 u). Une porte simple : 64 u de large ; une pièce : 112 à 144 u sous plafond.
- **La taille monde d'une surface est fixée par sa définition** (`TEXTURES.*`, colonnes `monde_u` et `px_par_u`) : livrer
  le même nom aux mêmes dimensions en pixels garde tout en place. Pour plus de définition, me le demander : je change
  la définition (4 → 8 px/u), pas la taille monde. Ne jamais livrer une image deux fois plus grande sous le même nom
  sans cet accord.
- Murs courants : 4 px/u ; panneaux et inscriptions lus de près : 8 px/u ; façades de Paris : 3,7 px/u (256 × 448 u).
- Une texture de mur se répète en largeur : bords gauche et droit raccordés. Une texture « masquée » (grille, tréteau,
  cadrans) est en RGBA, ses vides vraiment transparents.
- Un sol ou plafond (`Flat`) fait 64 × 64 u (RF04–RF07) ou 128 × 128 u (RF01) et se répète dans les deux sens.

## Portes : règles depuis la passe du 02/10

Chaque porte est construite avec un dormant et un linteau fixes ; son vantail reçoit **une image recomposée à la taille
exacte de l'ouverture** par `scripts/mapkit/doors.py` (échelle uniforme, puis colonnes ou rangées retirées dans les
zones unies, jamais à travers une poignée ou une moulure ; la face arrière d'une porte simple est le miroir de la
face avant). Tes images sources ne sont pas modifiées.

| Image de porte | Taille naturelle | Ouvertures qu'elle habille en jeu |
|---|---|---|
| `RFD_SGL` (Sainte-Anne, simple) et sa version 1940 `RFDSGLA` | 64 × 128 u | 64 × 112, 48 × 104, 48 × 88 (chambres de RF06), 64 × 128 |
| `RFD_DBL`, `RFDDBLA` (double) | 128 × 128 | 128 × 128, 96 × 128, 96 × 112 |
| `RFD_OAK` (double de chêne) ; un vantail seul = `RFD_OAKS` | 128 × 128 ; 64 × 128 | salle de danse : 64 × 128, 48 × 96 |
| `RFM_DOOR`, `RFMDOORA` (métal) | 64 × 128 | 64 × 104 |
| `RFM_GRIL`, `RFMGRILA` (grille à barreaux) | 128 × 128 | 64 à 160 de large, 128 à 168 de haut (barreaux répétés et allongés) |
| `RF2_RIDO` (rideau métallique) | 128 × 128 | 48 × 104, 128 × 128 |
| `RF4_PSST` (sous-station) | 64 × 96 | 64 × 96 seulement |

Pour qu'une image de porte se prête à la recomposition : **des plages unies franches** (le plat d'un panneau, la
course d'un barreau) sur toute la hauteur et toute la largeur ; la quincaillerie groupée ; aucun texte dans l'image ;
pas de dégradé d'un bord à l'autre. `RF4_PSST` n'en a pas (rouille partout) : elle n'est posée qu'à sa taille.

Un montant de porte montre le matériau du mur ou du métal uni, jamais une image de porte.

## Façades

- **Paris** (`RF2_FAC1`–`3`, 256 × 448 u, rez-de-chaussée à deux rideaux et deux portes) : en bout de mur, l'ouverture
  qui serait coupée est remplacée par le mur nu de `RF2_FACU`. **Demande** : une vraie fin de façade (chaîne d'angle ou
  pilastre, 16 à 32 u de large sur 448 u), répétable en hauteur d'étage, pour remplacer cette pièce.
- **Foraines** (`RF4_FAC1`–`3`, une travée de 128 × 256 u) : posées par travées entières ; sur un mur plus bas (160,
  192 u), toute la composition est réduite à la hauteur du mur ; le reste du mur est un trumeau fait du poteau d'angle
  répété. Depuis le 02/10, huit trumeaux dessinés par la session de revue remplacent ce poteau répété aux huit
  tailles en jeu (16 × 128, 16 × 192 ×2, 16 × 256, 32 × 128, 32 × 144, 32 × 160, 48 × 256 u ; fichiers
  `patches/doors/RD….png`, 2 px/u, listés dans `scripts/mapkit/door_delivered.json` : le générateur ne les redessine
  plus). **Demande** : des façades basses dessinées pour 192 u et 160 u de haut si tu préfères cela à la réduction ;
  un trumeau livré pour une autre taille porte le nom que je te donne pour cette taille.

## Flaques

`sprites/rf04/R4PDA0`, `R4PDB0`, `R4PDC0` (384 × 384 px, 96 × 96 u, RGBA, vues de dessus, posées à plat sur le sol et
étirées par le jeu à la taille voulue) : provisoires, de mon fait, depuis le 02/10 (l'ancienne flaque était faite de
carrés de sol de 16 u, son bord était un escalier). La flaque du bassin porte la chaussure d'enfant ; les autres sont
l'huile et les suintements sous les machines de RF05.

## RF05 : états que le code affiche (lot A02)

| Élément | Fichiers | Changement d'état |
|---|---|---|
| Cadrans | `RF5_CAD0` (avant), `RF5_CAD1` (après MARCHE), 96 × 48 u, masqués, posés sur `RF5_MARB` | à la remise en marche ; depuis le 02/10 : version V03 de la session de revue, plaques ivoire et libellés lisibles (à préserver, reprendre sur défaut précis) |
| Coffret NODE 0 | `RF5_NOD0` fermé, `NOD1` ouvert diodes vertes, `NOD2` diodes rouges, 48 × 64 u | scène |
| Levier | `RF5_LEVM` (MARCHE), `RF5_LEVA` (ARRÊT), 32 × 48 u, provisoires | usage |
| Fusibles | `RF5_FUS0` (JERMA vide), `RF5_FUS1` (porcelaine en place), 48 × 32 u, provisoires | scène |
| Roue | `RF5_ROU0` / `ROU1` (deux phases, 3 tics chacune quand le moteur tourne), `RF5_ROUS` à l'arrêt, 64 × 64 u, masquées | le moteur |
| Enseigne | `RF5_LUN0` éteinte, `LUN1` allumée, 128 × 32 u, provisoires | parc rallumé |
| Moteur, voûte, marbre | `RF5_MOTR` 64 × 48, `RF5_VOUT` 128 × 128, `RF5_MARB` 128 × 128 | fixes (Codex : à préserver) |

Un état de plus (courroie fendue / renforcée, palier, fusible daté) = un fichier de plus au même format ; je branche le
changement sur la scène existante sans en modifier le déroulement.

## RF06 (lot A04)

Murs `RF6_BETN`, `BETS`, `PEAU`, `PEA2` (128 × 96 u, Codex : à préserver), sol et plafond `RF6_SOL`, `RF6_PLAF`
(Codex). Provisoires : numéros pochés et barrés `RF6_N117`, `N404`, `N017` (48 × 24 u, masqués, posés sur les portes),
cinq `RF6_ER1`…`ER5` (64 × 24 u : noir, rouge, gravé, ERREUR 0, barre débordante), le jour `RF6_JOUR`. Les graffitis
composés et relus du pack seraient des panneaux masqués de 64 à 128 u de large à poser sur `PEAU` / `PEA2`.

## Objets et figures fixes

Un objet plat vu de face est un sprite à une vue (`…A0`) avec `grAb` au pied ; un objet contournable et volumineux
gagne à être un modèle (OBJ + peau, comme le tram, le landau et les corps). Dire dans la remise si l'objet doit être
contourné : je choisis la représentation avec toi avant l'export.
