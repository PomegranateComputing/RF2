# Demande W03-RAPID-V02 — le tir et la pompe du Manufrance Rapid

| | |
|---|---|
| ID, version | W03-RAPID-V02 (corrige W03_W04_V01, qui reste figé) |
| Priorité | **P1** — retour du propriétaire du 29/09 : « le fusil de chasse manque d'une animation réaliste et du répondant attendu » |
| Base | banc `bench/rf2-arsenal` `d200735` ; module `dist/arsenal/RF2_ARSENAL_ESSAI_20260929_1545/RF2_ARSENAL_ESSAI.pk3` (sha256 `5aaec05f…`) ; base `RF2_BASE_src_23773520f797.pk3` (`a03fad5f…`) ; animation lue : `W03_W04_V01/animation.rapid.json` (sha256 `f84fe01d…`) |
| Cible | arme W03, banc seulement (aucune activation en campagne) |
| Contrat | v2 (`docs/production/handoff/RF2-ARSENAL/CONTRAT.md`, §3, §4, §9) ; 4+1, compteurs et interruption inchangés |

## Ce que le moteur affiche aujourd'hui (preuves jointes)

`preuves/rapid_cycle_2560x1080.jpg` et `rapid_cycle_1440x1080.jpg` : le cycle tir B C D puis pompe E F G H I A, une
capture par état, nommée par le tic de jeu qu'elle montre (bande de tic lue, module 1532, mêmes fichiers que 1545).

Mesures sur tes images (centre de la silhouette opaque, bord supérieur ; toile 1536×1024), comparées au FAL accepté :

| Image | Déplacement du centre | Bord supérieur | FAL, image équivalente |
|---|---|---|---|
| FIRE (2 tics, `shot`) | −2,9 / +2,0 px | +1 | FIRE : +10 / +13, bord +30 |
| RECOIL (3 tics) | −9,0 / +1,7 px (vers le haut-gauche) | −5 | RECOIL_MAX : **+29 / +32**, bord **+80** |
| RECOVERY (4 tics) | −2,7 / +1,5 px | 0 | RECOVERY : +8 / +11, bord +24 |
| PUMP_BACK (1 tic, `pump_back`) | +46 / +8 px | 0 | — |

Le FAL ajoute en plus un décalage de code de 7 px vers le bas au recul (`A_WeaponOffset(2, 39)`). Le Rapid : trois
images presque identiques au repos, et le peu qui bouge part vers le haut-gauche, contre la poussée d'un 12/70. À la
pompe, seule la main de soutien avance et recule (70 px au bord gauche) : le corps de l'arme, la main de tir et
l'épaule ne réagissent jamais ; au point arrière, la manche quitte le bord gauche de la toile.

## Ce qu'il faut obtenir (dessin et code ensemble)

1. **Départ** : une image de décharge (flash sur son calque, pas plus grand qu'aujourd'hui), l'arme encore en visée.
2. **Recul avec masse** : l'arme et les deux mains partent ensemble vers l'arrière et le bas-droite (crosse qui
   s'enfonce dans l'épaule), la bouche remonte nettement ; ordre de grandeur au moins celui du FAL (centre +25 à +35 px,
   bord supérieur +60 à +90), bref : 2 à 3 tics au maximum de recul.
3. **Récupération** : retour franc en 3 à 4 tics, sans rebond flottant ; la main de soutien **tient le fût** pendant tout
   le recul (pas de glissement relatif).
4. **Pompe, geste distinct du tir** : la main de soutien tire le fût vers l'arrière **et l'arme suit légèrement**
   (quelques pixels, léger roulis), l'étui sort par la fenêtre d'éjection à l'image `pump_back` (le banc fait tomber
   l'étui à cet événement), puis le fût revient, retour en visée franc. La manche reste jusqu'au bord gauche du cadre
   à toutes les images (4:3 compris).
5. Aucune compensation par des dégâts, un volume ou un flash plus forts ; une secousse de vue éventuelle reste sobre
   (c'est au code, pas au dessin).

## Temps (delta versionné proposé, à confirmer ou corriger par toi)

| Séquence | V01 | V02 proposé | Événements |
|---|---|---|---|
| fire | FIRE 2 / RECOIL 3 / RECOVERY 4 = 9 | DEPART 1 / RECOIL_A 2 / RECOIL_MAX 2 / RECOVERY_A 2 / RECOVERY_B 2 = 9 | `shot` sur DEPART |
| pump | 5 images, 11 tics | 6 à 7 images, 11 à 13 tics | `pump_back` à l'image arrière, `pump_fwd` à l'image avant |

Un changement de durée garde : un seul `shot`, `pump_back` puis `pump_fwd`, `ready_point` sur la dernière image de
pompe ; la recharge (entrée 6, cartouche 12 avec engagement à +6, sortie 6) n'a pas à changer. Si tu changes un temps,
dis-le dans le fichier d'animation (`tics`) : le banc et le contrat suivent, rien n'est reconstruit à la main.

## Fichiers attendus

Lot `incoming/astra/RF2_ARSENAL/W03_V02/` : `animation.rapid.json` (même schéma, `files` + `target_relpath` dans le
manifeste), les PNG nouveaux ou changés (toile 1536×1024, même convention FAL : XScale 6.8, YScale 8.16, offset
−750,−460), les WAV seulement s'ils changent (16 bits, 48 kHz, mono), `manifest.json`, `SHA256SUMS.txt` sans session
privée, bibliothèque ni cache non listés. Les images inchangées peuvent être référencées dans V01.

## Ce qu'Opus fait de son côté

Import contrôlé, banc reconstruit, sondes (compteurs, interruption autour du tic d'engagement ±2, sauvegarde, mort),
captures par tic en 16:9, 21:9 et 4:3, **séquence à vitesse normale** avec le son sorti du moteur dans la même session,
et retour sur le build exact (tic, fichier, défaut).
