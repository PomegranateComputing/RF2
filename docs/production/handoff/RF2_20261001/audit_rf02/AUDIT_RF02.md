# Audit de RF02 — 01/10/2026 (build joué 1821)

Opus. RF01 et RF02 conviennent au propriétaire ; RF02 garde des défauts de placement et un ancien reflet de Viktor.
Le parcours et les rencontres réussis ne changent pas.

## Méthode

| Passe | Preuve |
|---|---|
| Traversée complète (pilote automatique, A et B) sur 1821 | `dist\candidates\RF2_CUMUL_20260930_1821\preuves\RF02_E2E_*.json` : PASS |
| Mesure de chaque objet dans le moteur (112 acteurs : hauteur au-dessus du sol réel, sol sous 8 points du pourtour, largeur dessinée, distance au mur) | `mesure_objets_1821.txt` (outil `scripts/production/prop_audit_pk3.py`) |
| Gros plan automatique de chaque objet, de face quand l'espace le permet (56 vues) | `gros_plans_1821_planche_1…5.jpg`, `gros_plans_1821_vues.json` (outil `scripts/production/prop_views_pk3.py`) |
| 48 vues de contrôle (cadrages V01–V10 du propriétaire, tram, landau, valise, figures F02) | `controle_1821_1…4.jpg` |
| Tirs à travers le tram, marche du landau | `tirs_tram_landau_1821.txt`, `tirs_tram_landau_apres.txt` |
| Reflet de Viktor | `../mesures/reflet_rf02.md` |

## Défauts reproduits

| # | Défaut | Preuve | Traitement |
|---|---|---|---|
| 1 | **Lignes de tir :** les flancs de la cabine du tram sont des volumes invisibles et solides ; aucune balle ne passe par les fenêtres (4 tirs à 50, 70, 90, 110 u : arrêtés à 56 u) | `tirs_tram_landau_1821.txt` | **Corrigé (Opus)** : un volume invisible (collision d'un modèle) laisse passer les tirs (`udmf.py`, type de sol 3D 33) ; après : les 4 tirs traversent ; le joueur reste bloqué comme avant |
| 2 | **Échelle :** livres de la librairie à 40–90 u de long (jusqu'à 2,8 m), pile de 44 u | V08, gros plans 42–43 | **Corrigé (Opus)** : dos de 8 à 18 u, 1,5–3 u d'épaisseur, 16 px/u ; pile de 32 u (`materials_rf02.py`, `TEXTURES.rf02`, `rf02.py`) |
| 3 | **Reflet de Viktor :** autre visage, 68 u pour un joueur de 56 u | `../mesures/reflet_rf02.md` | Taille **corrigée (Opus)** : 56 u en attendant les images ; **visage : Codex** (`R2F8`, 311 px) |
| 4 | **Landau figé :** la femme au landau (l. 91) ne marchait pas (« la marche attend le modèle », fiche RF02-C du 28/09) | gros plans 03, 05 | **Corrigé (Opus)** : quand Viktor approche (520 u), elle pousse le landau vers l'ouest sur 300 u, au pas, puis s'arrête ; le registre posé dessus suit ; collision du landau respectée |
| 5 | **Voies du tram :** deux bandes claires au ras des pavés, sans acier ni gorge (un tram parisien a des rails à gorge encastrés : le niveau est juste, la matière non) | contrôle 19 `rails_au_sol`, gros plan 20 | **Codex** : matière et profil des rails à gorge (modèle `models/rf02/track_straight.obj` d'Astra : retouche ciblée) |
| 6 | **Ambulance de Cochin :** bloc à faces peintes (roues dessinées à plat) | gros plans 26, 27, 30 | **Codex** : modèle d'ambulance ; emprise actuelle 128 × 48 × 96 u en (1280–1408, 128–176), à garder |
| 7 | **Borne-fontaine** (l. 425, rue de l'Université) : pilier de marbre de 16 × 16 × 40 u | gros plan 50 | **Codex** : borne-fontaine de fonte, filet d'eau, rouille ; emprise 16 × 16 u en (320–336, 2768–2784) |
| 8 | **Sacs de sable et table du barrage :** blocs lisses | V09, gros plans 45–49 | **Codex** : sacs de sable (matière et volume), table de campagne ; emprises : barrage (1904–2032, −128…−64), (2080–2208, 848–896), chicane de l'Assemblée (`rf02.py` l. 506) |
| 9 | **Matelas :** cinq images posées à plat, neuves, rayées bleu et blanc ; charrette = bloc | gros plans 12–16 | **Codex** : matelas d'exode (portés, ficelés, tachés), charrette à bras ; positions (2400, −80), (2440, 460), (1900, 460), (2300, 420), charrette (2352–2448, 400–448) |
| 10 | **Bocaux de la pharmacie** (vitrine-miroir) : aplats | mesure du reflet | **Codex** : `RF2_PHVI` (64 × 40 u, masqué) |
| 11 | **Entrée du Luna Park en fin de RF02** : façade sombre et carrés colorés | V10 | **Codex**, avec la façade publique de RF04 (même lieu, mêmes masters) |
| 12 | Plafond intérieur du tram bruité (modèle d'Astra) | V04, contrôle 17 | **Codex** : retouche ciblée de la texture, rien d'autre sur le tram |
| 13 | Pile de livres corrigée encore procédurale | `avant_apres_rf02.jpg` | **Codex** : vraie pile (titres du roman : HISTOIRE DE FRANCE, ANNUAIRE DES CHEMINS DE FER, TRAITÉ DE PATHOLOGIE MENTALE, ATLAS DES COLONIES) |

Faux positifs vérifiés : chaises du café (éparpillées, ne se pénètrent pas), garçon de la TSF (bien derrière le
comptoir ; la caméra automatique s'était placée derrière lui), objets à cheval sur une bordure (centre au sol),
infirmière de Cochin fixe (le texte, l. 167, la décrit immobile qui fait signe avec une enveloppe).

## Représentations de Viktor recensées (RF02–RF06)

| Lieu | Acteur / ressource | État |
|---|---|---|
| RF02, vitrine latérale de la pharmacie (miroir) | `RFViktorMirror` → `R2F8` | ancien visage ; taille corrigée ; Codex |
| RF02, matelas visible seulement en reflet | `RFMirrorMattress` | anomalie voulue, gardée |
| RF02, vitrine de la TSF (l. 213), Amiga qui apparaît puis disparaît | texture `RF2_AMIG` (scène `S_TSF_WINDOW`) | anomalie voulue, gardée ; pas de visage |
| RF02, vitre d'une automobile (l. 425 : l'ombre sous la mâchoire) | texte de la scène de la borne-fontaine | aucun visage dessiné |
| RF04, salle de danse (miroirs) | `RFViktorMirror` → `R2F8` ; trois tenues décrites en texte seulement | Codex : `R2F8` (tenue noire), `R4V2` (blouse grise), `R4V3` (chemise claire, badge) ; Opus les branche |
| RF05, salle de danse (miroirs) | `RFViktorMirror` → `R2F8` ; couples seulement en texte | idem |
| RF06 | aucun reflet | — |
| HUD, menus | `graphics/hud/viktor/*` | master |

## Avant / après

`avant_apres_rf02.jpg` (mêmes caméras, build 1821 / build de développement après correctifs) : librairie, landau (en
marche), vitrine-miroir à 30, 70 et 130 u. RF02 rejouée A et B après correctifs : PASS
(`build/dev/e2e/RF02_E2E_20261001_122620.json`).
