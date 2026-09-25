# RF01 — son : chaîne, déclencheurs, mesures

Statut : vérification technique dans la sortie réelle du moteur. **Aucune écoute humaine ni écoute par
l'agent** : les niveaux mesurés ne disent rien de la qualité perçue. Jugement final : le propriétaire.

## Chaîne

- Moteur UZDoom 5.0.1, sortie OpenAL Soft (`soft_oal.dll`), EFX actif : la réverbération vient des zones
  `SoundEnvironment` posées par la carte (une par pièce, `scripts/mapkit/udmf.py`). Les fichiers doivent rester
  secs (pas de longue réverbération cuite).
- Routes : `src/SNDINFO`. Variantes par `$random`, niveaux relatifs par `$volume`, lit sonore de la carte
  (`RFAMB01`, déclaré comme musique dans `MAPINFO`) par `$musicvolume`.
- Le son émis par le joueur (armes, pas) est joué sans position ni atténuation ; les ennemis et impacts sont
  positionnés (atténuation normale).

## Déclencheurs (code : `src/zscript/rf/`)

| Événement | Son | Canal, volume | Remarque |
|---|---|---|---|
| Tir Browning | `rf/browning/fire` | `CHAN_WEAPON` + `CHANF_OVERLAP`, 1,0 | frame B, un seul par tir |
| Culasse Browning | `rf/browning/slide` | `CHAN_ITEM`, 0,45 | frame D |
| Tir FAL | `rf/fal/shot` (3 variantes) | `CHAN_WEAPON` + `CHANF_OVERLAP`, 1,0 | frame B |
| Douille FAL | `rf/fal/shell` (2) | `CHAN_ITEM`, 0,5 | frame C |
| Recharge FAL | `rf/fal/cloth, latch, mag_out, mag_in, seat, action` | `CHAN_ITEM` | une par étape, arrêtés au changement d'arme |
| À vide | `rf/browning/dry` (= `fal/dry`), `rf/fal/dry` | `CHAN_ITEM` | |
| Impacts | `rf/impact/{plaster,wood,metal,flesh}` (2 chacun) | `CHAN_BODY` de l'impact, 0,85 | matière reconnue par préfixe de texture |
| Ennemis | vue, douleur, mort, activité, attaque | `CHAN_VOICE`, `$volume` 0,4–0,6 | pas, roues, appui : `CHAN_BODY` |
| Joueur | pas `rf/player/step` | `CHAN_AUTO`, 0,3, hauteur ±8 % | foulée de 112 unités |
| Joueur | douleur, mort | **sons Freedoom par défaut** | à remplacer par la voix de Viktor |
| Monde | portes, interrupteurs, treuil, papier | séquences natives / `CHAN_BODY` | ambiances : boucles `ATTN_STATIC` posées par la carte |

`CHANF_OVERLAP` (25/09) : sans lui, chaque tir coupait la queue du précédent sur `CHAN_WEAPON` (FAL toutes les
0,2 s pour un son de 0,95 s).

## Mesures dans la sortie du moteur

Outil : `devrun.run(..., audio_wav=...)` (enregistreur WAV d'OpenAL Soft, rien sur les haut-parleurs) ;
`scripts/film.py` pour une vidéo avec son d'un vrai parcours (autopilote, temps réel), synchronisée par un bip au
tic 1 exclu du film. Même parcours (réveil, E1 au Browning, E2 au FAL), mêmes réglages de revue
(`snd_mastervolume 0.5`, `snd_musicvolume 1`, `snd_sfxvolume 1`).

| | Base `6e1a31b` | Après réglage du 25/09 |
|---|---|---|
| Lit de fond, RMS médian sur 100 ms | −21,6 dBFS | −32,8 dBFS |
| Tirs du joueur, crête dans le mix | −8 à −10 (Browning), −4 à −5 (FAL) | −6 à −13 |
| Crête globale, échantillons écrêtés | −4,1, 0 | −6,4, 0 |

Constat de la base : le lit `RFAMB01` (−11 dBFS RMS dans le fichier) jouait en continu au-dessus des tirs, et les
voix ennemies (fichiers autour de −9 dBFS RMS) étaient plus fortes que les armes. Réglage : `$musicvolume RFAMB01
0.25`, voix ennemies 0,4–0,6, impacts 0,85. Ces valeurs seront recalées sur les nouveaux fichiers de la passe
artistique (Codex), mesurées de la même façon.

## Limites

- Pas d'écoute : ni l'agent ni le propriétaire n'ont encore jugé le mix.
- Tir Browning très court (0,22 s, sans queue), sans variante ni son à vide propre : matière attendue de Codex.
- Voix de Viktor : Freedoom.
