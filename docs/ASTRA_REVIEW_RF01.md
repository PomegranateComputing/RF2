# Revue des lots Astra — RF01

Revue d'intégration côté runtime. « Promu » signifie copié dans `src/` par
`scripts/promote_astra_batch.ps1` (empreintes vérifiées, journal `docs/ASTRA_PROMOTION_*.json`)
puis raccordé au moteur. L'approbation artistique reste celle du propriétaire.

## RF01_P0_FAL — promu le 2026-09-24

- Validation structurelle : PASS (21 fichiers).
- Comparaison avec les frames legacy déjà intégrées (`graphics/weapons/fal/NN_FAL_*.png`) :
  - la prise, la rotation, l'alignement et l'insertion du chargeur n'ont plus l'alternance
    manche / peau / manche de l'avant-bras gauche (manche continue) ;
  - la couture claire qui dessinait un liseré blanc sur la crosse en READY a disparu ;
  - FIRE ne contient plus de flash : le flash séparé `RFMZ A0` est affiché sur le calque flash.
- Cibles : les `target_relpath` proposés (`sprites/weapons/fal/RF2_FAL_*.png`) auraient donné
  à tous les fichiers le même nom court de lump (`RF2_FAL_`). Promotion avec
  `-Remap 'sprites/weapons/fal/=graphics/weapons/fal/'` ; les sprites `RFLV A0..T0` et `RFMZ A0`
  sont déclarés dans `src/TEXTURES.weapons` (échelle 6 / 7.2, offset -700,-300 inchangés).
- Anciennes frames legacy retirées de `src/` (conservées dans l'historique git).
- Reste à juger en jeu : cadrage 16:9 / 16:10, fermeture des doigts sur le chargeur, contact
  du levier d'armement, cadence de la recharge.

## RF01_P0_ENEMIES — promu le 2026-09-24

- Validation structurelle : PASS (322 fichiers).
- Contenu : mêmes rendus que les sprites legacy déjà intégrés (`ORDY`, `BRCD`, `PREG`, `PRGS`),
  avec ancrage au sol relevé de 1 à 4 px sur 250 vues et six vues de mort du Brancardier
  re-rendues (bouts de doigts coupés). Aucune régression constatée hors moteur.
- Cibles : les noms proposés (`RF2_EN*_...png` sous `sprites/enemies/enemy_*`) tombaient sur
  trois noms courts de lump. Promotion avec `-NameFrom cached_source` : chaque fichier reprend le
  nom de sprite qu'il remplace, le ZScript n'a pas changé.
- Limite connue (signalée par Astra, confirmée) : rendu « mannequin » stylisé, crânes, membres
  fins, motifs de tissu marqués ; pas au niveau matière du FAL. Ce lot corrige des défauts
  techniques, il ne clôt pas la direction artistique ennemie.

## Demandes pour les prochains lots

1. `target_relpath` : proposer des noms de sprites Doom valides (4 lettres + frame + rotation)
   sous `sprites/`, ou un chemin hors `sprites/` pour les images référencées par `TEXTURES`.
2. Ennemis : nouvelle passe matière/anatomie cohérente avec le FAL (même éclairage, tissus
   crédibles, visages non squelettiques), à partir d'un master par famille.
3. Lots P0 encore absents : matériaux (`RF01_P0_MATERIALS`), props, audio, UI art. RF01 tourne
   sur les matériaux et sons de remplacement générés par `scripts/mapkit/`.
