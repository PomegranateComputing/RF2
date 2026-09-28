# RF02-C — parcours, figures et scènes (en cours)

**Statut : IN_PRODUCTION.** Mandat du 27/09 soir, lot RF02-C (« parcours complet, figures F02-01…08, Luna Park »).
Rien ici ne vaut accord du propriétaire.

## 1. Figures d'Astra (lot `RF2_MAP_02_REPRISE`, 28/09)

**Import** : `scripts/production/import_astra_new_files.py` (empreintes, tailles, aucune cible existante écrasée) ;
144 fichiers nouveaux : 136 sprites de figures (`sprites/rf02_figures/`, huit rotations, échelle 0,18 comme les
ennemis, point d'ancrage aux semelles), et les ressources du pied-de-biche (cinq poses, objet au sol, modèle et
atlas), qui attendent le lot COMBAT-02. Registre `art/rf2_map_02_reprise_astra/IMPORT_RECORD.json` ; notes,
manifeste, contrats de raccord, propositions de code et validations archivés à côté. Les fichiers de revue
d'Astra (`review_only.zs`, banc RFArtReview, ViktorDebug) ne sont pas importés.

**Classes** (`src/zscript/rf/figures.zs`, écrites d'après la proposition d'Astra) : visuelles seulement, sans
collision, jamais hostiles ni utilisables ; numéros 30641 à 30651.

| ID | Figure | Placement (`scripts/mapkit/rf02.py`) | États |
|---|---|---|---|
| F02-01 | l'uniforme qui brûle les formulaires | trottoir sud d'Arago, à 20 u du seau, tourné vers lui | geste lent en boucle (A-B-C-B) |
| F02-02 | la femme de la voiture d'enfant | à la poignée, derrière la voiture (bloc actuel) | arrêt ; la marche (4 images) attend le modèle de poussette (RF02-B) |
| F02-03 | le groupe devant la porte de la Santé | quatre figures, l'enfant devant, tournées vers le boulevard | fixe |
| F02-04 | le vieil homme du tram | assis sur la banquette de la plateforme arrière, près de la sacoche du receveur | endormi ; yeux ouverts quand Viktor s'approche (112 u, en vue) |
| F02-05 | le garçon de la boutique TSF | accroupi derrière le comptoir | fixe (un seul état livré) |
| F02-06 | l'infirmière de Cochin | devant le porche de Cochin, côté boulevard | fixe |
| F02-07 | la jeune femme à la valise | dans la chicane du barrage, tournée vers l'entrée | fixe |
| F02-08 | Viktor | suit le joueur, visible seulement dans les miroirs | fixe |

**Vérification dans le moteur** (build de développement, 1600×900, personnages hostiles masqués) : chaque figure de
face et de biais ; pieds au sol, échelle cohérente avec les portes et les ennemis ; le reflet de Viktor apparaît dans
le miroir de la pharmacie (sweat noir, pantalon gris). `RF02.wad` : seuls s'ajoutent 11 objets ; contrôle statique
inchangé.

**Reste à raccorder** (contrats d'Astra, `CONTRATS_OPUS.md`) : marche de la femme avec la poussette (modèle de
RF02-B, trajectoire de 300 u) ; assise définitive du vieil homme sur la banquette du futur tram ; contact des mains
(poignée, valise, enveloppe, seau) ; séparation mère/enfant du groupe ; second état du garçon (non produit) ;
infirmière qui traverse et revient avec l'enveloppe, femme à la valise qui la pose et repart vers le pont ; reflet de
Viktor en marche. Les sacs de sable du barrage et les bocaux de la pharmacie restent des volumes grossiers (V08, V09).
