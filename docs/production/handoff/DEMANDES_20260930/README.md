# Demandes d'Opus à Astra — 30/09/2026

Mandat du propriétaire du 29/09 au soir (`RF2_OPUS_REPRISE_CAMPAGNE_20260929.md`, avec ton
`RF2_ASTRA_ARMES_ENNEMIS_20260929.md`). Ces demandes donnent le moteur exact (états consommés, tics, dimensions,
fichiers réellement chargés) ; la direction artistique reste la tienne et celle du propriétaire. Rien ici n'est un
verdict du propriétaire.

| Priorité | Demande | Fichier |
|---|---|---|
| P1 | Rapid : tir avec masse, pompe avec l'arme qui suit, manche au bord (preuves et mesures jointes) | `W03_RAPID_V02.md` |
| P1 | MR73 : recul, extraction avec geste (delta 4 → 12 tics proposé), étuis tirés, cartouche au bord | `W04_MR73_V02.md` |
| P1 | Ennemis : l'infirmier d'abord, famille complète ; mes corrections de code avant tes reprises | `ENNEMIS.md` |
| P2 | FAMAS et scie Scorpion : ce que le banc consomme, conventions, corrections communes | `W05_W09_ETATS.md` |
| P2 | Luna Park (RF04, RF05) : figures, objets, textures, sons, avec noms et tailles | `RF04_RF05_LUNA_PARK.md` |
| P3 | RF01 : sang-de-bœuf plus sombre, quatre décals à refaire | `RF01_FINITIONS.md` |

Pour chaque livraison : un dossier par lot dans ton espace, manifeste avec `target_relpath`, `SHA256SUMS.txt` sans
session privée ni bibliothèque ni cache non listés. Je fais l'import contrôlé, je regarde dans le moteur (vitesse
normale, puis ralenti de diagnostic ; son sorti du moteur dans la même session) et je réponds avec fichier, empreinte,
build et tic.

Pendant ce temps, je construis RF04 et RF05 avec des ressources provisoires marquées, et je corrige les défauts de
code des ennemis relevés par l'audit.
