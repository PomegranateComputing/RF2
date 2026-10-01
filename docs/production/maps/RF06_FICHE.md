# RF06 — La sortie du personnel (fiche, engagée le 30/09)

Cinquième niveau narratif. Titre V1 conservé : la « sortie du personnel » est la porte de service au fond de la salle de
danse (fin de RF05, l. 703) et le couloir qui ne devrait pas tenir dans le bâtiment. Carte suivante : RF07 « Jerma -
Façade maritime » (l. 733 et suivantes).

## Situation

| | |
|---|---|
| Lieu, date | un couloir impossible entre le Luna Park de juin 1940 et le Jerma Palace (Malte, décembre 2022) : le texte ne tranche pas |
| Entrée | la porte de service de la salle de danse ; la musique s'est tue, un bruit de vagues (l. 705–707) |
| Sortie | une ouverture rectangulaire qui découpe le jour : la terrasse du Jerma (l. 729–733) |
| Segment source | l. 709–731 |

## Séquence du texte (canon) → jeu

| Texte (lignes) | Dans la carte |
|---|---|
| Béton brut, plafond bas, conduites peintes en blanc ; le sol descend en pente presque imperceptible ; humidité salée (709) | couloir long, pente réelle (paliers de 8), sel sur les murs |
| Numéros de chambres au pochoir, puis barrés : 117, 404, 017, dans un ordre ni croissant ni aléatoire (709) | pochoirs barrés, ordre donné par le texte |
| Derrière lui, le train passe encore ; le grondement devient celui d'une ventilation hôtelière (713) | son qui se transforme en avançant |
| Les ampoules nues s'allument devant lui et s'éteignent après son passage (713) | lumières pilotées par la position du joueur |
| Peinture qui se soulève comme des peaux brûlées ; graffitis de plusieurs langues : anglais, français, maltais, italien, cyrillique (713) | couches de peinture, graffitis |
| ERREUR Ø tous les vingt ou trente mètres, noir, rouge, gravé ; un zéro à la place du Ø ; une barre qui coupe le mot (715–717) | occurrences variées tous les 20–30 m ; jamais expliquées |
| La pente s'accentue, l'air se réchauffe ; des voix : « Tu l'as vu où ? » « Dans l'autre aile. » « Il n'y a pas d'autre aile. » ; un rire ; un faisceau de lampe balaie le mur (719–727) | voix et faisceau **non hostiles** (les explorateurs du Jerma, RF07) |
| Le couloir tourne deux fois ; la seconde courbe n'est pas assez large pour la longueur parcourue ; une ouverture découpe le jour (729) | géométrie qui ne referme pas : impossible à parcourir en sens inverse |

## Décision et recomposition (01/10)

Choix retenu le 01/10 sur délégation du propriétaire : **sans combat** (voie a). Mandat : au moins cinq moments
spatiaux et deux explorations latérales. La carte (`scripts/mapkit/rf06.py`) suit le texte : la porte de service
refermée et les vagues ; le couloir des chambres aux numéros pochés puis barrés (117, 404, 017) ; une salle où la
peinture se soulève sur les graffitis ; la descente, plus raide et plus chaude ; le carrefour des voix et le faisceau
de lampe ; les deux virages et le jour. ERREUR Ø cinq fois, à 640–960 u d'intervalle, jamais le même. Explorations
latérales (adaptation, aucun texte ajouté) : la chambre 404 entrouverte, vide, un lit de fer sans matelas ; au
carrefour, un passage vers « l'autre aile » qui s'arrête à une rambarde au-dessus d'une cage d'escalier sans fond visible.

Lumière (01/10, après les vues de la candidate 1502) : les ampoules des quatre premières pièces restaient éteintes
(allumées au tic 0, avant que le moteur attache leur lumière au premier tic de la lampe) ; le premier allumage attend
le tic 2 et règle toutes les lampes, au chargement aussi (`corridor.zs`). Chambre 404 : ampoule au-dessus du lit,
plus forte, salle à 44.
