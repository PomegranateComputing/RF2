# RF02-B — tram, rails, poussette, objets fixés (en cours)

**Statut : IN_PRODUCTION.** Mandat du 27/09 soir, lot RF02-B (« tram complet sur rails, poussette, objets fixés »).
Rien ici ne vaut accord du propriétaire.

## 1. La voiture d'enfant (V02)

Le bloc de 48×32 qui tenait lieu de poussette est retiré ; à sa place, le modèle original d'Astra (lot
`RF2_MAP_02`, `source/models/pram.obj`, testé par Astra dans UZDoom), avec son atlas de matières
(`models/rf02/pram.obj`, `models/rf02/rf2_material_atlas.png` ; empreintes dans
`art/rf2_map_02_astra/IMPORT_RECORD_pram.json`) : caisse d'osier, registres ficelés, capote, roues et poignée.

- Classe `RFPram` (`paris.zs`, numéro 30652) : solide, 36×36 de collision au centre du modèle (47×30), 38 de haut.
  Posée au même endroit que l'ancien bloc, pointée vers l'ouest ; la femme (F02-02) est à la poignée.
- La note des registres (« Une voiture d'enfant pleine de registres ficelés ») reste lisible avec la touche
  d'usage ; sa feuille n'est plus dessinée (le modèle montre les registres) : nouvelle option de `RFNote`
  (troisième argument, bits 1 hauteur donnée, 2 sans feuille), à 0 pour toutes les notes de RF01 (inchangées).
- Vues dans le moteur : cadrage V02 du propriétaire, quatre côtés, dessus, les deux approches ; roues au sol.

Limites : le modèle a 32 690 faces pour un budget de 6 000 fixé au contrat (accepté pour cet objet unique ; temps de
trame à mesurer dans la scène). Les mains de la femme sont à hauteur de poitrine, au-dessus du guidon (≈ 30 u) :
contact à reprendre avec Astra (hauteur des mains des images de marche). La marche sur 300 u attend ce raccord.

## 2. Le tram et ses rails (V03, V04)

Le volume anguleux du carrefour (caisse de secteurs et de planchers 3D texturés, deux portes au milieu du flanc sud)
est remplacé par le modèle d'Astra (lot `RF2_MAP_02`, `source/models/tram.obj`, 344×112×136, 53 032 faces pour un
budget de 60 000) : châssis riveté, essieux et roues à boudin, ressorts, deux plateformes ouvertes aux extrémités avec
leurs marchepieds, caisse centrale ouverte à ses deux bouts, banquettes et douzaine de valises, cage, perche abaissée.
Même atlas que la poussette. Les rails sont des modules de 256 u (`track_straight.obj`, rails à ±30 sous les roues),
deux entiers et un demi à l'est de la place, à la place du sol peint `RF2_RAIL`. Tram et rails sont posés 1 u
au-dessus des pavés pour que les champignons des rails se voient. Empreintes :
`art/rf2_map_02_astra/IMPORT_RECORD_tram.json`.

**Le volume jouable reste dans la carte, invisible** (planchers 3D pleins d'alpha 0, nouvelle option `alpha` de
`slab()`, sans effet sur les cartes qui ne l'emploient pas : RF01 et RF02 régénérés identiques avant usage) : le
plancher, plein depuis les pavés jusqu'à 1 u sous celui du modèle (la rue reste visible sous le châssis puisque rien
n'est dessiné), deux marches de 15 de chaque côté de chaque plateforme, les parois de la caisse avec l'allée ouverte
aux deux bouts (48 u), les banquettes, les tableaux de bord des extrémités.

Mis au point avec des sondes dans le moteur (joueur posé puis poussé, positions relevées) : le moteur ne laisse pas
passer d'un plancher 3D à un autre qui commence exactement à son sommet (d'où un plancher plein depuis les pavés) ; et
entre le tableau de bord et la paroi de la caisse, 32 u ne laissaient pas passer un joueur de 32 u de large : les
parois invisibles de la caisse sont 8 u en retrait de celles du modèle, le passage des plateformes fait 48 u. Montée
par les marches sud, traversée de la plateforme, descente par les marches nord : vérifiées.

**Accès au récit** : l'accès se fait désormais par les plateformes (celles du modèle), plus par deux portes latérales.
La sacoche du receveur pend contre la caisse, sur la plateforme ouest (arrière), à hauteur de poitrine ; le vieil
homme dort sur la première banquette, à côté. L'itinéraire du pilote automatique monte par les marches de la
plateforme ouest et se tourne vers la sacoche.

La scène du ticket était manquée par le pilote automatique une fois sur deux, avant comme après le nouveau tram : il
s'arrête quelques unités plus loin que son point (élan) et, orienté à l'est, laisse la sacoche hors du cône d'usage du
directeur (±45°). Corrigé des deux côtés : le point du pilote vise la sacoche à 45° depuis ses arrêts observés ; et,
pour un joueur, le cône s'élargit à ±72° quand l'objet est tout contre lui (moins de 40 u) — objets de scène des
chapitres après RF01 seulement (`director.zs`).

**Piège réglé** : un acteur aussi large que le modèle touchait les planchers invisibles et le moteur le poussait
sous le plancher (on ne voyait que le toit, au ras des pavés) ; les acteurs du tram et des rails ont un petit corps
et un grand rayon de rendu (`RenderRadius`), qui les garde dessinés dès qu'une partie est en vue.

Limites : l'atlas commun (1254 px) est étalé sur un objet de 344 u : banquettes et parois paraissent pixelisées de
près (densité à relever par Astra) ; les deux poules de la cage ne sont pas produites ; pas de fil aérien (perche
abaissée, comme au contrat) ; les valises n'ont pas de collision propre (elles sont sur les banquettes).
