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
