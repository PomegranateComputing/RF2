# RF01-TEXTURES-1940 — retour d'Opus n° 1 sur la livraison d'Astra du 28/09

Livraison `RF01_TEXTURES_1940_ASTRA_20260928.zip` (sha256 `663af4b8…`), statut `OWNER_REVIEW_REQUIRED`.
Rien ici ne vaut accord du propriétaire.

## Reçu et intégré

- 40 fichiers importés aux empreintes du manifeste ; chaque original remplacé était à l'empreinte de la base
  (`art/rf01_textures_1940_astra/IMPORT_RECORD.json`).
- Tes noms (`OLD_TO_NEW`) et ton `TEXTURES.rf01_1940` sont repris tels quels ; la carte RF01 est renommée par le
  générateur (1570 valeurs) ; l'atlas est posé sur les six accessoires en RF01 seulement ; la paire d'interrupteur
  est dans `ANIMDEFS`. RF02 et les ressources partagées ne changent pas.
- Candidate : `dist/candidates/RF2_RF01_TEXTURES_1940_20260928_1745/` (sha256 `1c77187c…`), lanceur
  `JOUER_RF2_RF01_TEXTURES_1940.cmd`. Rapport : `docs/RF2_RF01_TEXTURES_1940.md`.
- Dans le moteur, 59 cadrages avant/après : échelle, calage, raccords, alpha de la fenêtre, UV de l'atlas et
  préfixes d'impact sont bons. Traversées RF01 A et B : PASS.

## Le contrat que tu n'as pas eu

Le contrat d'Opus a été déposé le 28/09 à 08:20 dans ton worktree du 27/09 (`RF2_UZDOOM_ASTRA_20260927`), pas dans
celui où tu travaillais depuis 08:07. C'est une erreur d'Opus. Référence :
`docs/production/handoff/RF01-TEXTURES-1940/CONTRAT.md` sur `prod/rf2-campaign` (commit `a5c7aa4`), avec
`INVENTAIRE.md` et `inventaire.json` ; copie jointe à ce retour.

## Points ouverts

1. **Soubassements — en attente de la décision du propriétaire.** Les trois familles servent à s'orienter dans RF01
   (`RFP_DADB` bleu : admissions et couloirs ; `RFP_DADG` vert : salles et chambres ; `RFP_DADR` sang-de-bœuf :
   registres et loge). Écarts de couleur de la bande peinte (CIE76) : build accepté 35,8 / 41,9 / 40,1 ; ta livraison
   0,2 / 6,7 / 6,7 : `DADB` et `DADG` ont la même couleur. Si le propriétaire choisit de garder le repère : trois
   variantes anciennes et désaturées mais distinctes (par exemple gris-bleu, gris-vert, brun-rouge passé), de clarté
   voisine, écart d'au moins 15 entre chaque paire ; même hauteur de soubassement (44 u du bas) et même moulure que ta
   livraison ; nouvel envoi `02_soubassements/` avec manifeste, sans réécrire celui du 28/09.
2. **Finesse (facultatif).** Tu as gardé 4 px/u ; le contrat conseille 8 px/u pour ce qui se voit de près (murs,
   soubassements, sols, plafonds, portes, côtés de meubles ; 2048 px au plus par côté), 4 px/u pour les façades. De
   près, murs et soubassements restent pixelisés comme avant. À faire seulement si le propriétaire demande une
   deuxième passe.
3. **Décalques d'usure** `graphics/decals/RFDSTN1…4` (humidité, crasse, coulure, frottement) : non livrés ; propres à
   RF01, remplacement direct possible (masques à alpha progressif).

Ordre : l'arsenal en cours passe d'abord, sauf instruction contraire du propriétaire. Opus prépare l'intégration
d'une variante des soubassements dès qu'elle arrive (même méthode, nouvelle candidate datée).
