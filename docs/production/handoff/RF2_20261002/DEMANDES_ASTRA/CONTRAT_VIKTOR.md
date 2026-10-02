# Viktor dans le jeu — où il apparaît, avec quels fichiers

Relevé au commit `61d9b43`. Image de contrôle : `VIKTOR_EN_JEU.png` (les trois reflets et le portrait du HUD côte à
côte). Tables : `CONTRATS/V01_VIKTOR_FICHIERS.csv`, `CONTRATS/REF_VIKTOR_HUD_FICHIERS.csv`,
`CONTRATS/REF_VIKTOR_BRAS_ARMES_FICHIERS.csv` ; copies des fichiers dans `REFERENCES/`.

## Inventaire : il n'y a plus d'ancien Viktor dans les reflets

| Support | Fichiers | État |
|---|---|---|
| Portrait du HUD, six états de santé | `graphics/hud/viktor/VIKTOR_H100`, `H080`, `H060`, `H040`, `H020`, `DEAD` (512 × 512) | **référence du propriétaire** (crâne rasé, deux anneaux, sweat noir à capuche) : ne pas remplacer |
| Bras et manche noire, armes | `graphics/weapons/browning`, `fal`, `crowbar` (34 images) | **acceptés** : références de mains et de manche, ne pas remplacer |
| Reflet en pied, tenue noire | `sprites/rf02_figures/R2F8A1…A8` | `R2F8_V02` (Codex, 01/10), le Viktor du HUD ; a remplacé l'ancien reflet signalé par le propriétaire |
| Reflet, blouse grise d'ouvrier | `sprites/rf04/R4V2A1…A8` | `R4V2_R4V3_V01` (Codex, 01/10), même visage, même hauteur |
| Reflet, chemise claire et badge | `sprites/rf04/R4V3A1…A8` | idem |
| Planches de transition | `graphics/comics/*.png` | Viktor de dos ou par sa main (Codex) |
| Écran titre, menus | — | Viktor n'y figure pas |

Aucun autre fichier ne représente Viktor. Si une image de l'ancien Viktor reparaît quelque part, c'est un défaut à
me signaler avec la carte et le lieu.

## Contrat des reflets

- Acteur `RFViktorMirror` : visible **seulement dans les miroirs** ; il se tient à la place exacte du joueur et prend
  son angle à chaque tic ; les miroirs sont de vrais miroirs du moteur (`Line_Mirror`), pas des images de scène. Le
  reflet est donc vu sous tous les angles : **huit rotations vraies** (`A1`…`A8`, numérotation de
  `ROTATIONS_ETALON_ORDY_A.jpg`), une seule pose `A`, immobile.
- Toile 512 × 448 px, `grAb` (256, 424) : semelles sur la ligne y = 424, axe du corps à x = 256. `Scale 0.18`.
  **Hauteur du sommet du crâne aux semelles : 311 px = 56 u** (la taille du joueur). À tenir sur toute nouvelle version.
- RF02 : vitrine de la pharmacie (un miroir derrière la couche de bocaux `RF2_PHVI`, posée en haut de la vitrine).
- RF04 et RF05 : salle de danse, trois panneaux de miroir à l'ouest et deux à l'est. Pendant la scène du badge (RF04),
  la blouse grise et la chemise au badge apparaissent chacune dans le panneau voisin de celui où Viktor se regarde,
  puis disparaissent (« Le badge disparaît »). Le texte du badge est une ligne du jeu (`LANGUAGE`), pas dans l'image.
- Une pose de plus (geste, retard d'une seconde au Jerma) = une lettre de plus (`B`, `C`…), huit rotations chacune, même
  ancrage ; je règle le retard par le code.

## Ce qui n'existe pas encore (à convenir avant de dessiner)

| Élément du pack | État | Ce qu'il me faut |
|---|---|---|
| Matelas qui avance dans le reflet de la pharmacie (RF02) | pas de scène | le matelas comme figure de miroir : 8 rotations, toile et ancrage du tableau ci-dessus, objet porté sans porteur ; je fournis le déclenchement et la trajectoire |
| Reflet en retard au Jerma | pas de miroir dans RF07 | mêmes fichiers que R2F8 si la tenue est la même ; sinon une série nommée |
| Téléphone, application, vignettes | absent | écran typographique : images à plat, tailles à convenir |
| Feuille de continuité | absente | à produire par Astra depuis le HUD et R2F8 ; je la range dans `docs/production/` comme référence de série |
| Barbe de plusieurs jours (manuscrit) | le maître du HUD fait foi | ne pas modifier le visage sans demande du propriétaire |
