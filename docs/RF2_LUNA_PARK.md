# RF2 — Luna Park : RF04, RF05, RF06 (production du 30/09)

**Statut : cartes jouables, finition artistique ouverte (ressources provisoires d'Opus marquées), revue du
propriétaire requise.** Mandat du 29/09 (`RF2_OPUS_REPRISE_CAMPAGNE_20260929.md`). Rien ici ne vaut accord du
propriétaire ; aucun son n'a été écouté par une personne.

## Correspondance des identifiants

Décision du propriétaire du 27/09 : troisième niveau narratif = Luna Park, ID technique **RF04** ; RF03 « Batignolles »
reste un blockout pour sa place du roman (l. 2743, après le Jerma). Le « RF03 » du mandat du 29/09 est donc **RF04**,
son « RF04 » est **RF05** ; **RF06** suit. Les titres V1 nomment exactement ces passages (l. 451–731). Chaîne :
RF01 → RF02 → RF04 → RF05 → RF06 → (RF07, Jerma, à produire ; écran titre en attendant).

## Ce que contient chaque carte

| Carte | Texte | Contenu | Rencontres |
|---|---|---|---|
| RF04 « Luna Park - Personnel technique » | l. 451–551 | chemin de service et rails tièdes ; guérite (« Tu es en retard. », carton pointé 06:06, clef SOUS-STATION, barrière du personnel, guérite vide et ERREUR Ø sur la vitre) ; allée, Palais des Singes, décor BROOKLYN BRIDGE et couloir de câbles ; bassin du Niagara (algues sèches, chaussure d'enfant, rambarde) ; montagnes russes (poteaux, voie, quai, voie de gare praticable) ; marquise, tourniquets 617 → 618, salle de danse (miroirs, badge DATABASE ADMINISTRATOR, juke-box muet, trois coups) ; ruelle derrière la piste, porte de la sous-station ; trois cachettes | 6 (E1–E6) : 19 ennemis en facile, 21 en normal, 30 en difficile (hangar compris) |
| RF05 « Les machines continuent » | l. 551–707 | escalier, ampoule ; sous-station (marbre, cadrans, NODE 0, moteur et roue, levier MARCHE / ATTENTE / ARRÊT) ; arrêt ; la jeune femme (paroles, enveloppe de Cochin posée sur l'établi, ERREUR Ø sous sa paume) ; réparation répartie : atelier (chiffons, burette, clé de 17), galeries de câbles (toile, agrafes de cuivre), salle des transformateurs et pompes (fusible 22.12.2022) ; palier, courroie, ligne JERMA (vision de Malte, diodes rouges) ; MARCHE ; le parc s'allume (ampoules une à une, train vide et frein) ; salle de danse : le juke-box joue, les couples dans les miroirs ; porte de service, vagues | 4 (galeries, coude, transformateurs, parc rallumé) : 9 / 11 / 13 ennemis selon la difficulté ; la salle reste sans combat |
| RF06 « La sortie du personnel » | l. 709–731 | le couloir impossible : béton, conduites blanches, pente, sel ; numéros 117 / 404 / 017 barrés ; graffitis de plusieurs écritures sous la peinture qui se soulève ; ERREUR Ø sous cinq formes ; ampoules qui s'allument devant et s'éteignent derrière ; le train devenu ventilation d'hôtel ; voix et lampe ; deux virages impossibles ; l'ouverture sur le jour | aucune (proposition (a) de la fiche, conforme au texte ; à confirmer par le propriétaire) |

Canon, adaptation et invention de liaison sont séparés dans les fiches `docs/production/maps/RF04_FICHE.md`,
`RF05_FICHE.md`, `RF06_FICHE.md` (lignes du roman citées) ; matrice `docs/production/CANON_FIDELITE.md` mise à jour.
Le gardien, la jeune femme, les danseurs, le couple du miroir et les voix du couloir ne sont jamais des cibles.

## Ressources

Provisoires d'Opus (procédurales, noms de la demande LUNA-V01 à Astra) : `scripts/mapkit/materials_rf04.py`
(RF04/RF05), `materials_rf06.py`, `sounds_rf04.py` (sons du parc, du moteur, de la sous-station, du couloir). Le
gardien est une silhouette derrière la vitre ; la jeune femme n'a pas de figure (ses paroles et ses traces seulement) :
figures F04-01, F05-01, F05-02 demandées. Aucune musique : le juke-box qui joue reste un sous-titre.

## Vérifications

Voir `docs/RF2_CUMUL_20260930.md` pour le build exporté, ses empreintes et les parcours. Cartes construites par leurs
générateurs (contrôle statique : sortie atteinte, clef comptée) ; rencontres vérifiées hors vue au moment de leur
apparition ; parcours automatiques A (départ → sortie) et B (sauvegarde, mort, reprise, chargement) ; vues de contrôle
1920×1080 portant le tic montré.

## Limites

- Ressources provisoires : la finition artistique attend Astra ; RF04–RF06 ne sont pas « finis ».
- RF06 sans combat : choix proposé, à confirmer.
- Le pilote automatique prouve le franchissement, pas le plaisir ni l'équilibre.
