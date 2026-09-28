# RF01-TEXTURES-1940 — les matières de Sainte-Anne en 1940, RF01 seul

**Statut : RUNTIME_VERIFIED_OWNER_REVIEW_REQUIRED.** Mandat du propriétaire du 28/09
(`RF2_RF01_TEXTURES_1940_OPUS.md`) ; ressources produites par Astra (livraison du 28/09, `OWNER_REVIEW_REQUIRED`),
intégrées par Opus. Rien ici ne vaut accord du propriétaire ni « qualité artistique approuvée ». Le build RF01
accepté et son lanceur `JOUER_RF2_ART_REVIEW.cmd` sont inchangés (`04bdd0ae…`).

## Jouer

| Commande | Contenu |
|---|---|
| `JOUER_RF2_RF01_TEXTURES_1940.cmd` | écran titre ; « Nouvelle partie » : RF01 avec les matières 1940 |

Build `dist\candidates\RF2_RF01_TEXTURES_1940_20260928_1745\RF2_RF01_TEXTURES_1940.pk3`, sha256
`1c77187c3856c842bd39d1c57194365b4ef00600e14587096f0d923cd9d5125f`, commit `82d85a7` (intégration `800f0d4`, branche
`candidate/rf01-textures-1940`, base : tag `rf01-owner-accepted-20260927` + socle). Profil et sauvegardes séparés
(`user\uzdoom_rf01_textures_1940.ini`, copie de `user\uzdoom.ini` qui n'est pas modifié ; `user\savegames_rf01_textures_1940`).
Lot isolé : les plaques corrigées de RF01-PAN n'y sont pas (autre lot, autre candidate).

## Décision à prendre : les soubassements

Les murs à soubassement de RF01 ont trois familles, qui servent aussi à s'orienter : **bleu** (admissions,
couloirs), **vert** (salles, chambres), **sang-de-bœuf** (registres, loge). Le mandat demandait des soubassements
« gris-vert ou gris chaud » ; Astra l'a appliqué aux trois. Résultat mesuré sur la bande peinte (écart de couleur
CIE76 ; au-dessus de 10, deux couleurs se distinguent nettement) :

| | bleu–vert | bleu–sang-de-bœuf | vert–sang-de-bœuf |
|---|---|---|---|
| Build accepté | 35,8 | 41,9 | 40,1 |
| Candidate | **0,2** | 6,7 | 6,7 |

Le bleu et le vert ont maintenant la même couleur ; le sang-de-bœuf n'est plus qu'un gris un peu plus chaud. Les
couloirs et les chambres ne se distinguent plus par leurs murs. Image : `evidence\planches\soubassements_avant_apres.jpg`.

- **A** — garder la candidate telle quelle : palette du mandat, repère de couleur perdu.
- **B** (conseillé par Opus) — demander à Astra trois soubassements anciens et désaturés **mais distincts** (par
  exemple gris-bleu, gris-vert, brun-rouge passé), de même clarté, livrés en variante sans réécrire la livraison du
  28/09 ; Opus les intègre dans une nouvelle candidate datée.

## Ce qui change

Inventaire de RF01 (60 entrées, `docs/production/handoff/RF01-TEXTURES-1940/`) : **44 remplacées**, **12
conservées**, **4 restantes** ; détail fichier par fichier, empreintes comprises, dans
`evidence\inventaire\inventaire_resultat.md`.

| Famille | Remplacées | Conservées | Restantes |
|---|---|---|---|
| Murs, soubassements, faïence, façades, portes, métaux, fenêtre, côtés de meubles (textures murales) | 24 | `RFG_VITR` (vitrail et sa brightmap), `RFSIGN0…9` (plaques : lot RF01-PAN) | — |
| Sols, plafonds, dessus de meubles (plats) | 14 | `F_SKY1` (ciel) | — |
| Accessoires (chaise, armoire, radiateur, chariot, banc, lampe) | 6, par un atlas 1940 | — | — |
| Décalques d'usure (`RFDamp`, `RFGrime`, `RFStreak`, `RFScuff`) | — | — | 4 : non livrés, les originaux restent |

S'y ajoute l'état allumé de l'interrupteur (`RFM_SW1`), livré avec l'état éteint.

## Intégration

- **RF01 seul.** Les 39 textures portent des noms nouveaux (`RFPDADBA`, `RFFWOODA`…, table d'Astra
  `scripts/mapkit/rf01_textures_1940.csv`), définis dans `TEXTURES.rf01_1940`, images dans `patches/rf01_1940/`. Les
  noms et images d'origine ne changent pas : RF02 et les autres cartes les gardent. `maps/RF02.wad` est identique à
  l'octet ; aucun matériau partagé n'est écrasé.
- **Carte.** `scripts/mapkit/rf01.py` renomme les textures de la carte construite : 1570 valeurs, 38 noms ; lignes,
  sommets, secteurs et objets identiques au build accepté (contrôle statique inchangé : 7523 cellules, clés 1 et 2,
  sortie atteinte).
- **Accessoires.** Même maillages et UV ; en RF01 seulement, `RFPropBase` et `RFPropLamp` prennent l'atlas 1940 à
  leur apparition (`A_ChangeModel`) ; `MODELDEF` inchangé.
- **Interrupteur.** Paire `RFMSW0A`/`RFMSW1A` ajoutée à `ANIMDEFS`.
- **Taille dans le monde.** Mêmes dimensions en pixels et mêmes échelles qu'avant (4 px par unité) : un carreau, une
  planche, une porte gardent leur taille.
- **Impacts.** Les nouveaux noms gardent les trois premières lettres (RFW/RFD bois, RFM métal) : le matériau d'impact
  des balles ne change pas.

## Vérification dans le moteur

| Contrôle | Résultat |
|---|---|
| Contenu du pk3 comparé au build accepté | 41 fichiers ajoutés (le lot), 3 modifiés (`ANIMDEFS`, `RF01.wad`, `world.zs`), aucun supprimé |
| Mêmes cadrages avant/après, 1920×1080, personnages masqués | 59 cadrages (39 surfaces, 6 accessoires de loin et de près, lampe, 7 zones du mandat) : aucune texture manquante, aucun changement d'échelle, de calage ou de géométrie |
| Traversées RF01 (`scripts/e2e_rf01.py`) | A PASS (56 points, 17 ennemis tués, sortie) ; B PASS (sauvegarde, mort, reprise, chargement) |
| `scripts/check_runtime.py` | PASS sur les cartes de la branche |
| Lanceur, depuis `C:\` | charge ce build, RF01 démarre sans erreur |
| Visite | film de 63 s avec le son du moteur, pilote automatique à vitesse réelle : chambre, pavillon ouest, admissions, cour, pavillon est, lingerie, registres |

Ce que montrent les planches : sols plus matériels (gravier, dalles de pierre, parquet veiné, lino moucheté), façades
plus patinées, faïence et plafonds proches de l'existant, mobilier un peu plus usé. Le rendu reste lisible sous
l'éclairage actuel ; rien n'a été assombri.

## Limites

1. **Soubassements** : voir la décision ci-dessus.
2. **Finesse** : Astra a gardé 4 px par unité ; le contrat conseillait 8 pour les surfaces vues de près. De près,
   murs et soubassements restent aussi pixelisés que dans le build accepté (planches 06, 07, 09) : pas de régression,
   pas de gain.
3. **Décalques d'usure** non livrés (4 entrées).
4. **Contrat non reçu par Astra.** Le contrat d'Opus (inventaire, règles par famille, premier ensemble à valider
   d'abord) a été copié le 28/09 à 08:20 dans le worktree d'Astra du 27/09 (`RF2_UZDOOM_ASTRA_20260927`) ; Astra
   travaillait déjà depuis 08:07 dans un nouveau worktree (`RF2_UZDOOM_ASTRA_RF01_TEXTURES_1940_20260928`) et a
   reconstruit son propre inventaire. Erreur d'acheminement d'Opus. D'où l'absence de premier ensemble intermédiaire,
   la densité de 4 px/u et les décalques manquants.
5. **Palette** : proposition artistique plausible, sans couleur attestée à Sainte-Anne en 1940 (notes d'Astra
   ci-dessous).
6. **Correction** : le message du commit `800f0d4` annonce 55 erreurs de `check_runtime` « toutes RF02 de cette
   branche ». C'est faux : elles venaient d'un fichier de travail laissé par la branche de production
   (`build/RF02_TEXTMAP.txt`, RF02 haute définition). Sur les cartes de la branche, le contrôle passe.
7. Jugé sur captures fixes et un film, pas en partie longue ni à d'autres résolutions ; aucun avis du propriétaire.
8. **Ligne cumulative** : la passe n'est pas encore portée sur `prod/rf2-campaign` ; elle le sera après la décision
   sur les soubassements, pour que ce choix ne se propage pas en silence aux candidates suivantes.

## Sources et crédits

- Textures et atlas : Astra, générés avec l'outil de génération d'images intégré à son environnement ; masters,
  prompts et itérations dans `source/` de la livraison (`RF01_TEXTURES_1940_ASTRA_20260928.zip`, sha256
  `663af4b8…`). Les ressources RF01 existantes n'ont servi que de gabarits de disposition, d'échelle et de masque.
- Références consultées par Astra (texte et notices, aucune image patrimoniale incorporée) : L. Borne, *Études et
  documents sur la construction des hôpitaux*, 1898, Cnum/CNAM, p. 255, 319, 335 (reproductions « Droits réservés —
  CNAM », non redistribuées) ; GHU Paris, présentation de l'ouvrage des 150 ans de Sainte-Anne, 2017.
- Import : `art/rf01_textures_1940_astra/IMPORT_RECORD.json` (40 fichiers aux empreintes du manifeste, sha256 du
  manifeste `ec3098e9…`, chaque original remplacé à l'empreinte de la base).

## Preuves (dossier `evidence\` de la candidate)

- `planches\planche_01…09.jpg` : les 59 cadrages, build accepté à gauche, candidate à droite ;
  `planches\soubassements_avant_apres.jpg`.
- `captures\accepte_RF2_ART_REVIEW_1451\`, `captures\candidate_RF01_TEXTURES_1940_1745\` : captures brutes nommées
  par cadrage ; `vues\` : listes de vues et pk3 de contrôle.
- `inventaire\inventaire_resultat.md` et `.json` : remplacé, conservé, restant.
- `visite\tex1940_visite.mp4` (et une planche de 11 images).
- `controles.txt` : empreintes, contenu du pk3, blocs de la carte, contrôle statique, `check_runtime`, mesures des
  soubassements, traversées, lanceur ; `mesures\`, `outils\` (scripts des mesures) ; rapport de traversée
  `RF01_E2E_20260928_174308.json`.
