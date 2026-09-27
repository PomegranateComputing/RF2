# RF02 — demande d'assets à Astra (Opus → Astra)

27/09/2026. Carte : Paris, 14 juin 1940, du boulevard Arago à la porte de service du Luna Park. Fiche et canon :
`docs/production/maps/RF02_FICHE.md` (passage du roman l. 87–457 de l'extraction de `body.xhtml`, lu en entier).
Opus construit la carte avec des matières procédurales et des props de géométrie ; les éléments ci-dessous exigent un
vrai dessin. Même exigence que le contrat RF2-ART-02 (un master par figure, 8 rotations si la figure peut être vue de
côté, pieds au sol, marge dans les clairs, `Scale 0.18`, 5 px/unité, grAb aux pieds).

## 1. Figures du texte (non hostiles) — priorité 1

| ID | Figure (texte) | Pose / états | Lignes |
|---|---|---|---|
| F02-01 | Homme en uniforme brûlant des formulaires dans un seau galvanisé | debout penché, 2–3 frames de geste lent ; seau séparé (prop) | 87 |
| F02-02 | Femme poussant une voiture d'enfant pleine de registres ficelés | marche lente 4 frames × 8 rot., voiture en prop séparé si possible | 87 |
| F02-03 | Trois femmes sous un parapluie fermé (panier, couverture roulée, enfant par la main) | groupe statique face à la porte de la Santé, 8 rot. | 95–111 |
| F02-04 | Vieil homme endormi assis sur la plate-forme arrière du tram, chapeau sur les genoux, mains sur une canne | assis, 1 frame endormi + 1 frame yeux ouverts | 113–125 |
| F02-05 | Garçon de ~15 ans, blouse grise, cheveux collés, tournevis et boîte de lampes, accroupi derrière le comptoir de TSF | accroupi, 2 frames | 217–273 |
| F02-06 | Femme en blouse blanche, plus âgée, petite, cheveux gris sous une coiffe, tenant une enveloppe à deux mains (Cochin) | debout, 8 rot. | 163–197 |
| F02-07 | Jeune femme de Sainte-Anne : robe claire, épingle dans les cheveux, bracelet d'hôpital sans nom, valise brune | debout, 8 rot. ; valise ouverte en prop (F02-P05) | 373–413 |

## 2. Objets — priorité 1

| ID | Objet | Remarque |
|---|---|---|
| F02-P01 | Voiture d'enfant chargée de registres ficelés | 1940, capote, roues fines |
| F02-P02 | Seau galvanisé avec papiers qui brûlent mal | flamme sobre, papier administratif |
| F02-P03 | Cage à deux poules (sur une banquette du tram) | + deux gloussements secs |
| F02-P04 | Sacoche de cuir du receveur pendue au crochet ; ticket poinçonné (cercle incomplet barré par la pince) | le ticket devient un objet gardé |
| F02-P05 | Valise brune ouverte : chaussures de femme enveloppées de papier (escarpins, sandales, bottines, semelles usées) | lien avec CAN-003 : ne pas en faire l'escarpin du Jerma |
| F02-P06 | Poste de TSF des années 30 (Ducretet), plusieurs modèles, cadran allumé / éteint | rangées derrière la grille |
| F02-P07 | **Amiga 1200 en reflet** : boîtier gris plat, clavier intégré, lettres colorées ; écran bleu, pointeur, disquettes dans une boîte à chaussures | apparition dans la vitrine (CAN-002, première occurrence, statut : vision) |
| F02-P08 | Fiche de lecteur humide, tampon 12 décembre 2022, verso : adresse à Malte + « JERMA - ERREUR Ø » au crayon | gros plan lisible (texte composé, pas généré) |
| F02-P09 | Téléphone militaire de campagne sur table pliante ; Ø gravé dessous ; deux casques ; mitrailleuse sous bâche | décor de barricade |
| F02-P10 | Matelas à ressorts rayé, sale, traîné à la corde | apparition anormale : avance seul |
| F02-P11 | Colonne Morris : affiches, bande ANNULÉ, affiche du Luna Park « LA VILLE ENCHANTÉE DE LA PORTE MAILLOT » ; variante JERMA PALACE (photo aérienne, ailes, piscine vide) | deux textures, texte exact composé |
| F02-P12 | Entrée du Luna Park : lettres LUNA PARK (le U pend), panneau FERMETURE DÉFINITIVE (« définitive » barré au charbon) | façade vue de loin et de près |

## 3. Sons — priorité 2

Poste de TSF (souffle, craquements, trois voix lointaines inintelligibles ; pas de musique), sonnerie sèche d'un
téléphone militaire, moteurs lourds venant du nord (colonnes), papier qui brûle, deux poules, tram vide (tôle qui
travaille), pluie qui s'arrête. Pas de marche militaire (musique différée) : la voix allemande reste en sous-titre
tant qu'aucune voix enregistrée n'est fournie avec ses droits.

## 4. Livraison

`incoming/astra/RF2_MAP_02/` dans ton worktree, même manifeste que RF2-ART-02 (cible, SHA-256, dimensions, grAb,
source, crédits, preuve). Opus intègre par classes `RFFigure`/props déjà prévues dans la carte ; tant qu'une figure
manque, sa place reste vide et la carte n'est pas annoncée « complète et fidèle ».
