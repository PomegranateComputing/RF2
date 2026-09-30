# Demande W05-W09-V01 — ce que le banc consomme pour le FAMAS et la scie Scorpion

| | |
|---|---|
| ID, version | W05-FAMAS-V01, W09-SCORPION-V01 (premières livraisons animées) |
| Priorité | P2 — retour du propriétaire : « FAMAS et Scorpion demandent une vraie réalisation » |
| Base | banc `d200735` ; formats lus : `bench/arsenal/README.md` (tableau des `kind`), modèles `bench/arsenal/placeholder/W05_famas.json`, `W09_scorpion.json` ; contrat v2 §8 et §9 (corrections communes) |
| Toile, échelle | 1536×1024 RGBA, XScale 6.8, YScale 8.16, offset −750,−460, flash sur son calque, même toile |

## FAMAS (`kind: magazine`, classe `RFBenchFamas`, sprite `RFFM`, flash `FMFX`, emplacement 6)

Modèle et variante de la bible ; le F1 n'est qu'une référence de travail si aucun choix plus récent n'existe.
Prises, chargeur (derrière la poignée) et levier d'armement (sous la poignée de transport) propres au modèle.

| Séquence | Images, événements |
|---|---|
| `ready` | repos (1 image suffit) |
| `fire` | un seul `shot` par cartouche ; recul lisible (pose ou `offset`) ; cadence : dis la tienne (les images d'essai tirent toutes les 3 tics en automatique, soit 700 coups par minute : 10 tirs en 30 tics à la sonde) |
| `dry` | détente à vide, `dry` |
| `reload` | chargeur retiré par la main de soutien (`mag_out`), engagé (`mag_in`), **`seat` = le chargeur est compté** (un seul par recharge) ; sortie de main |
| `reload_empty` (option) | la même + levier d'armement (`bolt`) si la culasse est restée ouverte |
| `mode` (option) | sélecteur : coup par coup / rafale de 3 / automatique (le tir secondaire du banc) |

Le banc éprouve : 1 / 3 / automatique, aucun chargeur engagé après une demande de changement d'arme, tir à vide,
recharge partielle, sauvegarde. Capacité : 25 (dis si la bible dit autre chose).

## Scorpion (`kind: saw`, classe `RFBenchScorpion`, sprite `RFSC`, emplacement 7)

La scie Black & Decker demandée, pas le pistolet-mitrailleur Škorpion. Le cordon vers un bloc porté reste une
**convention visuelle de travail**, réversible, notée comme fiction d'adaptation ; ce n'est ni une décision du
propriétaire ni un modèle à batterie. Au banc, la marche illimitée est un mode de diagnostic : l'autonomie de campagne
reste à décider (besoin d'équilibrage noté à part).

| Séquence | Images, événements |
|---|---|
| `ready` | au repos, les deux mains sur l'outil |
| `start` | doigt sur la gâchette, lame qui démarre : `start` |
| `run` | boucle d'au moins 2 images (lame et moteur qui bougent, l'outil vibre dans les mains) ; son `loop` en boucle sans clic de raccord |
| `stop` | relâchement : `stop` ; la lame ralentit |

Contact : le banc applique `contact.range` / `damage` / `every` dans une fenêtre devant la lame, jamais à travers un
obstacle ; son `contact` en boucle ou par coups. Le son de boucle s'arrête au relâchement, au rangement et à la mort
(déjà éprouvé sur les images d'essai).

## Corrections communes (contrat v2 §9), à appliquer dès ces premières poses

Recul ou vibration lisible ; un geste de main pour chaque changement d'état ; état visible = état du jeu ; sortie de
main entre deux gestes ; manche noire jusqu'au bord en 16:9, 21:9 et 4:3 ; axe de l'arme vers le centre de l'écran (le
master FAMAS de travail pointe nettement vers le haut à gauche) ; un événement sonore par geste.

## Fichiers attendus

`incoming/astra/RF2_ARSENAL/W05_V01/` et `W09_V01/` : fichier d'animation, PNG, WAV (16 bits, 48 kHz, mono), manifeste
avec `target_relpath`, sommes. Le banc remplace alors les images d'essai par tes ressources et le dit dans son HUD.
