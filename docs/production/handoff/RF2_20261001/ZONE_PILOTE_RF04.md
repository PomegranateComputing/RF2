# RF04 — zone pilote : ce que la carte lit (Opus → Codex, 01/10)

Plan reconstruit : `docs/production/maps/RF04_RELEVE_PLAN.md`. La zone pilote est la **première vue sur le parc** :
de l'angle nord-est de l'esplanade, le bassin vide dans sa longueur, la rampe du Water Chute et sa tour au nord, la
charpente des montagnes russes sur le ciel à l'ouest, la façade Brooklyn à l'est, le revers des portes au sud. Opus
construit la géométrie avec les noms ci-dessous ; un nom arrive avec tes fichiers sans changer la carte.

Échelle : 1 u ≈ 3,1 cm ; joueur 56 u, yeux à 41 u ; 4 px/u pour ce qui se voit de loin, 8 px/u de près.

| Nom | Où, dimension monde | Ce qu'il doit montrer | État |
|---|---|---|---|
| `RF4_BROO` | façade d'attraction, est de l'esplanade, 256 × 192 u | pont suspendu de décor, BROOKLYN BRIDGE en lettres rouges sur fond gris | reçu (`LUNA_PILOTE_01`), intégré à 256 × 192 u ; arche à caler sur le passage (retour du 01/10) |
| `RF4_BRBK` | revers de la même façade, 256 × 192 u, vu du couloir technique | ossature de bois, contrefiches, toile clouée, câbles | provisoire d'Opus |
| `RF4_CABL` | murs du couloir technique, 128 × 96 u | câbles en faisceaux, isolateurs, boîtes de jonction | provisoire d'Opus |
| `RF4_BASS` | parois du bassin, 128 × 96 u (bassin profond de 96 u) | béton/enduit de bassin, ligne d'algues sèches à 48 u du fond | reçu, intégré |
| `RF4_BASF` | fond du bassin (sol), 64 × 64 u | dépôt sec, craquelures, flaques noires | provisoire |
| `RF4_BALU` | balustrade du bord du bassin, masquée, 64 × 32 u | fonte ou ciment moulé, peinture écaillée ; on voit le bassin à travers | provisoire d'Opus |
| `RF4_ROCH` / `RF4_ROCF` | rochers de la cascade et des montagnes : faces 128 × 128 u / dessus 64 × 64 u | rocher de décor en ciment sur grillage, fissuré, armatures visibles par endroits | `ROCH` reçu, intégré ; `ROCF` provisoire d'Opus |
| `RF4_CHUT` / `RF4_CHUS` | rampe du Water Chute : dessus 64 × 64 u / flancs 128 × 64 u | planches et rigole, rouille des ferrures ; pente de 30° environ | provisoires d'Opus |
| `RF4_TOWR` | tour de départ de la rampe, faces 128 × 256 u | charpente et plate-forme, escalier de service | provisoire d'Opus |
| `RF4_BOIS` | charpente des montagnes russes : faces de treillis masquées 64 × 128 u (croix de Saint-André) | bois peint en blanc écaillé (photo Schall 1935), boulons, contrefiches | reçu **opaque** : gardé pour les flancs de la voie ; le treillis vu à travers devient `RF4_TREI` |
| `RF4_POTE` | poteaux de la charpente, 16 × 16 u de section, 128 u de haut | même bois | provisoire d'Opus |
| `RF4_VOIE` | dessus de la voie (sol), 64 × 64 u | planches, rails plats vissés | provisoire |
| `RF4_DALH` / `RF4_HERB` | sol de l'esplanade / herbes, 64 × 64 u | dalles disjointes, herbe entre elles ; sable | `DALH` reçu, intégré ; `HERB` provisoire |
| `RF4_PORT` | revers des portes LUNA PARK et du pavillon à arcades, 256 × 256 u | maçonnerie de décor, piliers à dômes vus de dos, grilles fermées | provisoire d'Opus (à refaire : il ne ressemble pas aux portes) |
| `RF4_MAST` | mât de la tour aérienne, faces 16 × 512 u, et ses bras | treillis métallique rouillé, câbles pendants | provisoire d'Opus |
| `RF4_TREI` | treillis entre les poteaux du grand huit, masqué, 64 × 224 u | croix de Saint-André en bois blanc écaillé, vides transparents | nouveau, provisoire d'Opus |
| `RF4_FAC1` / `FAC2` / `FAC3` | façades des attractions (est de l'esplanade, salle de danse), 128 × 256 u, accrochées en haut | façades peintes de fête fermée, l'essentiel dans les 192 u du haut | provisoires du 30/09 |
| `RF4SKY` | ciel du parc | ciel gris du 14 juin 1940, fumées au loin ; les silhouettes restent celles de la carte | nouveau |

Ordre utile (01/10, après les premières vues moteur) : `RF4_TREI`/`RF4_POTE`, `RF4_PORT`, `RF4_FAC1…3`,
`RF4_BALU`/`RF4_BASF`, `RF4_ROCF`, `RF4_CHUT`/`RF4_CHUS`, `RF4_TOWR`, puis le reste. Après tes fichiers, Opus capture la zone aux caméras de `vues/rf04_pilote.json` et dépose
les vues et ses remarques dans `RETOURS_CODEX/`.
