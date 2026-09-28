# RF01 — inventaire des surfaces (passe « Sainte-Anne 1940 »)

Généré par `scripts/production/rf01_texture_inventory.py` depuis `src/maps/RF01.wad` (sha256 `ada65ca8783336f341e91cc63c28e0c449e393849987a7ae9035f458f03f65b7`) et `scripts/mapkit/rf01.py` (zones). Empreintes et détails : `inventaire.json`. En gras : premier ensemble représentatif (chambre de départ et couloir du pavillon ouest).

| Id | Représente | Fichier | px | Monde (u) | px/u | Usages RF01 | Zones | Autres cartes | Dépendances | Transparence | Action |
|---|---|---|---|---|---|---|---|---|---|---|---|
| F_SKY1 |  |  |  |  |  | secteurs 24 | COUR DES HOMMES, RUE CABANIS / SORTIE, PAVILLON EST - SALLE COMMUNE, COULOIR OUEST | RF02, RF03, RF04 ... | MAPINFO | - | hors lot (ciel) |
| RFD_DBL | porte a deux vantaux 128x128 | src/patches/rf01/RFD_DBL.png | 512x512 | 128x128 | 4.0 | cotes 6 | COULOIR OUEST, ECONOMAT, PAVILLON EST - SALLE COMMUNE | - | - | aucune | remplacer |
| **RFD_SGL** | porte simple 64x128 | src/patches/rf01/RFD_SGL.png | 256x512 | 64x128 | 4.0 | cotes 30 | POSTE, CONSULTATIONS, COULOIR DU PAVILLON OUEST, LOGE | RF02 | - | aucune | variante RF01 `RFD4SGL` |
| **RFF_CER** | sol carrele 32 u | src/patches/rf01/RFF_CER.png | 512x512 | 128x128 | 4.0 | secteurs 24 | ADMISSIONS, COULOIR OUEST, ECONOMAT, POSTE | RF02 | - | aucune | variante RF01 `RFF4CER` |
| RFF_CERD | sol carrele sombre | src/patches/rf01/RFF_CERD.png | 512x512 | 128x128 | 4.0 | secteurs 1 | COUR DES HOMMES | - | - | aucune | remplacer |
| RFF_CHK | sol en damier | src/patches/rf01/RFF_CHK.png | 512x512 | 128x128 | 4.0 | secteurs 23 | LINGERIE, POSTE, SALLE D'ATTENTE, CONSULTATIONS | - | - | aucune | remplacer |
| RFF_CONC | ciment | src/patches/rf01/RFF_CONC.png | 512x512 | 128x128 | 4.0 | secteurs 19 | LINGERIE, PORCHE, RUE CABANIS / SORTIE | - | - | aucune | remplacer |
| RFF_GRAV | gravier (cour) | src/patches/rf01/RFF_GRAV.png | 512x512 | 128x128 | 4.0 | secteurs 8 | COUR DES HOMMES, PAVILLON EST - SALLE COMMUNE, COULOIR OUEST, LINGERIE | RF02 | - | aucune | variante RF01 `RFF4GRAV` |
| RFF_LINO | linoleum | src/patches/rf01/RFF_LINO.png | 512x512 | 128x128 | 4.0 | secteurs 16 | PAVILLON EST - SALLE COMMUNE, LINGERIE | - | - | aucune | remplacer |
| RFF_PAVE | paves (rue) | src/patches/rf01/RFF_PAVE.png | 512x512 | 128x128 | 4.0 | secteurs 1 | RUE CABANIS / SORTIE | - | - | aucune | remplacer |
| RFF_SLAB | dallage de pierre 64 u | src/patches/rf01/RFF_SLAB.png | 512x512 | 128x128 | 4.0 | secteurs 26 | CHAPELLE VIDE, COULOIR OUEST, PAVILLON EST - SALLE COMMUNE, COUR DES HOMMES | RF02 | - | aucune | variante RF01 `RFF4SLAB` |
| **RFF_WOOD** | parquet | src/patches/rf01/RFF_WOOD.png | 512x512 | 128x128 | 4.0 | secteurs 40 | GALERIE NORD, REGISTRES, POSTE, LINGERIE | RF02 | - | aucune | variante RF01 `RFF4WOOD` |
| RFG_VITR | vitrail de la chapelle 64 (+ brightmap RFG_VITR_BM) | src/patches/rf01/RFG_VITR.png | 256x256 | 64x64 | 4.0 | cotes 12 | CHAPELLE VIDE, REGISTRES | - | GLDEFS | masque (0/255) | remplacer |
| RFG_WIN | fenetre 64 (vitrage a alpha progressif) | src/patches/rf01/RFG_WIN.png | 256x256 | 64x64 | 4.0 | cotes 110 | PAVILLON EST - SALLE COMMUNE, GALERIE NORD, COULOIR OUEST, LINGERIE | - | - | alpha progressif | remplacer |
| RFM_DOOR | porte metallique 64x128 (lingerie) | src/patches/rf01/RFM_DOOR.png | 256x512 | 64x128 | 4.0 | cotes 6 | LINGERIE | - | - | aucune | remplacer |
| RFM_GRIL | grille de fer 128x128 (grilles verrouillees) | src/patches/rf01/RFM_GRIL.png | 512x512 | 128x128 | 4.0 | cotes 6 | ADMISSIONS, GALERIE NORD, PORCHE, LOGE | RF02 | - | aucune | variante RF01 `RFM4GRIL` |
| RFM_PANL | metal peint 128 | src/patches/rf01/RFM_PANL.png | 512x512 | 128x128 | 4.0 | cotes 5 | LINGERIE, RUE CABANIS / SORTIE | RF02 | - | aucune | variante RF01 `RFM4PANL` |
| RFM_SW0 | interrupteur eteint 64 (paire ANIMDEFS avec RFM_SW1 allume) | src/patches/rf01/RFM_SW0.png | 256x256 | 64x64 | 4.0 | cotes 2 |  | - | ANIMDEFS | aucune | remplacer |
| RFM_TOP | dessus metallique (cuves, radiateurs) | src/patches/rf01/RFM_TOP.png | 256x256 | 64x64 | 4.0 | secteurs 16 | LINGERIE, PAVILLON EST - SALLE COMMUNE, CHAMBRE, ADMISSIONS | RF02 | - | aucune | variante RF01 `RFM4TOP` |
| RFM_VATS | cotes des cuves de la lingerie 64x48 | src/patches/rf01/RFM_VATS.png | 256x192 | 64x48 | 4.0 | cotes 16 | LINGERIE | - | - | aucune | remplacer |
| RFP_CEID | plafond platre sombre (service) | src/patches/rf01/RFP_CEID.png | 512x512 | 128x128 | 4.0 | secteurs 60 | LINGERIE, REGISTRES, CHAPELLE VIDE, COULOIR OUEST | RF02 | - | aucune | variante RF01 `RFP4CEID` |
| **RFP_CEIL** | plafond platre clair | src/patches/rf01/RFP_CEIL.png | 512x512 | 128x128 | 4.0 | secteurs 119 | PAVILLON EST - SALLE COMMUNE, POSTE, ADMISSIONS, GALERIE NORD | - | MAPINFO | aucune | variante RF01 `RFP4CEIL` |
| **RFP_DADB** | mur 256 : enduit au-dessus, soubassement peint bleu (44 u en bas, calé en bas), moulure — admissions, couloirs | src/patches/rf01/RFP_DADB.png | 1024x1024 | 256x256 | 4.0 | cotes 183 | GALERIE NORD, ADMISSIONS, COULOIR OUEST, ECONOMAT | - | - | aucune | remplacer |
| **RFP_DADG** | mur 256 : soubassement vert (44 u en bas) — salles, chambres | src/patches/rf01/RFP_DADG.png | 1024x1024 | 256x256 | 4.0 | cotes 130 | PAVILLON EST - SALLE COMMUNE, CHAMBRE, LINGERIE, POSTE | - | - | aucune | remplacer |
| RFP_DADR | mur 256 : soubassement sang-de-boeuf (44 u en bas) — registres, loge | src/patches/rf01/RFP_DADR.png | 1024x1024 | 256x256 | 4.0 | cotes 47 | REGISTRES, ECONOMAT, LOGE, POSTE | - | - | aucune | remplacer |
| RFP_DRK | enduit de service assombri 128 | src/patches/rf01/RFP_DRK.png | 512x512 | 128x128 | 4.0 | cotes 75 | LINGERIE, SALLE D'ATTENTE | RF02 | - | aucune | variante RF01 `RFP4DRK` |
| **RFP_PLN** | enduit uni 128 (retours, embrasures, contremarches) | src/patches/rf01/RFP_PLN.png | 512x512 | 128x128 | 4.0 | cotes 81 | COULOIR OUEST, POSTE, PAVILLON EST - SALLE COMMUNE, GALERIE NORD | - | - | aucune | remplacer |
| RFP_TILE | mur 256 : faience 16 u jusqu'a 48 u, enduit au-dessus — lingerie, consultations | src/patches/rf01/RFP_TILE.png | 1024x1024 | 256x256 | 4.0 | cotes 77 | LINGERIE, POSTE, SALLE D'ATTENTE, CONSULTATIONS | - | - | aucune | remplacer |
| RFSIGN0 |  | src/patches/rf01/RFSIGN0.png | 256x64 | 64x16 | 4.0 | cotes 2 |  | - | - | aucune | hors lot (plaques RF01-PAN) |
| RFSIGN1 |  | src/patches/rf01/RFSIGN1.png | 256x64 | 64x16 | 4.0 | cotes 4 |  | - | - | aucune | hors lot (plaques RF01-PAN) |
| RFSIGN2 |  | src/patches/rf01/RFSIGN2.png | 256x64 | 64x16 | 4.0 | cotes 6 |  | - | - | aucune | hors lot (plaques RF01-PAN) |
| RFSIGN3 |  | src/patches/rf01/RFSIGN3.png | 256x64 | 64x16 | 4.0 | cotes 2 |  | - | - | aucune | hors lot (plaques RF01-PAN) |
| RFSIGN4 |  | src/patches/rf01/RFSIGN4.png | 256x64 | 64x16 | 4.0 | cotes 2 |  | - | - | aucune | hors lot (plaques RF01-PAN) |
| RFSIGN5 |  | src/patches/rf01/RFSIGN5.png | 256x64 | 64x16 | 4.0 | cotes 2 |  | - | - | aucune | hors lot (plaques RF01-PAN) |
| RFSIGN6 |  | src/patches/rf01/RFSIGN6.png | 256x64 | 64x16 | 4.0 | cotes 2 |  | - | - | aucune | hors lot (plaques RF01-PAN) |
| RFSIGN7 |  | src/patches/rf01/RFSIGN7.png | 256x64 | 64x16 | 4.0 | cotes 2 |  | - | - | aucune | hors lot (plaques RF01-PAN) |
| RFSIGN8 |  | src/patches/rf01/RFSIGN8.png | 256x64 | 64x16 | 4.0 | cotes 2 |  | - | - | aucune | hors lot (plaques RF01-PAN) |
| RFSIGN9 |  | src/patches/rf01/RFSIGN9.png | 256x64 | 64x16 | 4.0 | cotes 2 |  | - | - | aucune | hors lot (plaques RF01-PAN) |
| RFS_BASE | soubassement de pierre 128x64 (bas de facades) | src/patches/rf01/RFS_BASE.png | 512x256 | 128x64 | 4.0 | cotes 50 | COUR DES HOMMES, RUE CABANIS / SORTIE, LINGERIE, GALERIE NORD | RF02 | - | aucune | variante RF01 `RFS4BASE` |
| RFS_FACD | facade parisienne 256x448 (rue Cabanis, vue de loin) | src/patches/rf01/RFS_FACD.png | 512x896 | 256x448 | 2.0 | cotes 7 | RUE CABANIS / SORTIE | - | - | aucune | remplacer |
| RFS_HOSP | facade de pavillon hospitalier 256x320 | src/patches/rf01/RFS_HOSP.png | 512x640 | 256x320 | 2.0 | cotes 6 | PORCHE, RUE CABANIS / SORTIE, LOGE | RF02 | - | aucune | variante RF01 `RFS4HOSP` |
| RFS_LIME | pierre calcaire appareillee 128 — chapelle, porche | src/patches/rf01/RFS_LIME.png | 512x512 | 128x128 | 4.0 | cotes 87 | CHAPELLE VIDE, COULOIR OUEST, PORCHE, LOGE | - | - | aucune | remplacer |
| RFS_REND | enduit de facade 128x256 (cour, exterieurs) | src/patches/rf01/RFS_REND.png | 512x1024 | 128x256 | 4.0 | cotes 136 | COUR DES HOMMES, PAVILLON EST - SALLE COMMUNE, ECONOMAT, COULOIR OUEST | - | - | aucune | remplacer |
| **RFT_BED** | dessus de lit (literie) | src/patches/rf01/RFT_BED.png | 256x256 | 64x64 | 4.0 | secteurs 10 | PAVILLON EST - SALLE COMMUNE, CHAMBRE, LINGERIE, POSTE | - | - | aucune | remplacer |
| **RFT_BEDS** | cote de lit 64x32 | src/patches/rf01/RFT_BEDS.png | 256x128 | 64x32 | 4.0 | cotes 19 | PAVILLON EST - SALLE COMMUNE, CHAMBRE, LINGERIE, POSTE | - | - | aucune | remplacer |
| **RFT_HEAD** | tete de lit 64x48 | src/patches/rf01/RFT_HEAD.png | 256x192 | 64x48 | 4.0 | cotes 33 | PAVILLON EST - SALLE COMMUNE, CHAMBRE, LINGERIE, POSTE | - | - | aucune | remplacer |
| RFW_PANL | lambris / boiserie 128 (meubles, rayonnages) | src/patches/rf01/RFW_PANL.png | 512x512 | 128x128 | 4.0 | cotes 24 | PAVILLON EST - SALLE COMMUNE, LINGERIE, ADMISSIONS, RUE CABANIS / SORTIE | RF02 | - | aucune | variante RF01 `RFW4PANL` |
| RFW_SHLF | face de rayonnage 64 | src/patches/rf01/RFW_SHLF.png | 256x256 | 64x64 | 4.0 | cotes 15 | REGISTRES, CONSULTATIONS, POSTE | - | - | aucune | remplacer |
| RFW_TBLS | cote de table 64x32 | src/patches/rf01/RFW_TBLS.png | 256x128 | 64x32 | 4.0 | cotes 37 | ECONOMAT, POSTE, PAVILLON EST - SALLE COMMUNE, LOGE | RF02 | - | aucune | variante RF01 `RFW4TBLS` |
| RFW_TOP | dessus de meuble en bois | src/patches/rf01/RFW_TOP.png | 512x512 | 128x128 | 4.0 | secteurs 19 | REGISTRES, ADMISSIONS, ECONOMAT, PAVILLON EST - SALLE COMMUNE | RF02 | - | aucune | variante RF01 `RFW4TOP` |
| RFPropChair | chaise (modele, atlas commun) | src/models/props/chair.obj | 2048x2048 |  |  | objets 10 | PAVILLON EST - SALLE COMMUNE, ADMISSIONS, LOGE, CHAMBRE | RF02 | MAPINFO, MODELDEF, zscript/rf/world.zs | - | nouvelle peau propre a RF01 `atlas_rf01.png` (memes UV, 2048) |
| RFPropCabinet | armoire (modele, atlas commun) | src/models/props/cabinet.obj | 2048x2048 |  |  | objets 5 | POSTE, LOGE, SALLE D'ATTENTE, ECONOMAT | RF02 | MAPINFO, MODELDEF, zscript/rf/world.zs | - | nouvelle peau propre a RF01 `atlas_rf01.png` (memes UV, 2048) |
| **RFPropRadiator** | radiateur (modele, atlas commun) | src/models/props/radiator.obj | 2048x2048 |  |  | objets 8 | POSTE, CHAMBRE, COULOIR DU PAVILLON OUEST, PAVILLON EST - SALLE COMMUNE | - | MAPINFO, MODELDEF, zscript/rf/world.zs | - | nouvelle peau propre a RF01 `atlas_rf01.png` (memes UV, 2048) |
| RFPropTrolley | chariot (modele, atlas commun) | src/models/props/trolley.obj | 2048x2048 |  |  | objets 6 | LINGERIE, RUE CABANIS / SORTIE, CONSULTATIONS, PAVILLON EST - SALLE COMMUNE | RF02 | MAPINFO, MODELDEF, zscript/rf/world.zs | - | nouvelle peau propre a RF01 `atlas_rf01.png` (memes UV, 2048) |
| RFPropBench | banc (modele, atlas commun) | src/models/props/bench.obj | 2048x2048 |  |  | objets 17 | CHAPELLE VIDE, PORCHE, POSTE, ECONOMAT | RF02 | MAPINFO, MODELDEF, zscript/rf/world.zs | - | nouvelle peau propre a RF01 `atlas_rf01.png` (memes UV, 2048) |
| RFPropLamp | plafonnier de service (modele, atlas commun) | src/models/props/service_ceiling_lamp.obj | 2048x2048 |  |  | objets 1 | PORCHE | - | MAPINFO, MODELDEF, zscript/rf/world.zs | - | nouvelle peau propre a RF01 `atlas_rf01.png` (memes UV, 2048) |
| RFDamp | decalque : tache d'humidite | src/graphics/decals/RFDSTN1.png | 128x128 |  |  | objets 6 |  | - | DECALDEF | alpha progressif | remplacer |
| RFGrime | decalque : crasse | src/graphics/decals/RFDSTN2.png | 128x128 |  |  | objets 5 |  | - | DECALDEF | alpha progressif | remplacer |
| RFStreak | decalque : coulure | src/graphics/decals/RFDSTN3.png | 128x128 |  |  | objets 2 |  | - | DECALDEF | alpha progressif | remplacer |
| RFScuff | decalque : frottement | src/graphics/decals/RFDSTN4.png | 128x128 |  |  | objets 4 |  | - | DECALDEF | alpha progressif | remplacer |
