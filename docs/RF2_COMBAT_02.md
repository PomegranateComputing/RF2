# COMBAT-02 — armes, mêlée, rencontres (en cours)

**Statut : IN_PRODUCTION.** Mandat du 27/09 soir (retouches de combat, mêlée au pied-de-biche, équilibrage par
composition des rencontres). Retouches de ressenti et changements d'équilibre sont séparés ci-dessous. Rien ici ne
vaut accord du propriétaire.

## 1. Relevé des valeurs actuelles (avant COMBAT-02)

| Arme | Emplacement | Dégâts | Dispersion (h / v) | Cycle de tir | Munitions |
|---|---|---|---|---|---|
| Browning Hi-Power | 1 | 18, fixe | 1,0 / 0,6 | 10 tics (≈ 0,29 s) | réserve 9 mm seule, pas de chargeur modélisé |
| FN FAL | 2 | 30, fixe | 1,2 / 0,7 | 7 tics (≈ 0,2 s) | chargeur de 20 + réserve, rechargement partiel ou à vide |

| Ennemi | Santé | Attaque | Vitesse | Douleur |
|---|---|---|---|---|
| Infirmier (orderly) | 60 | mêlée 8–14, portée 44 | 9 | 130 |
| Brancardier | 170 | mêlée 20–28, portée 64 | 5 | 40 |
| Porte-registre | 110 | liasse lancée, 9 | 4 | 90 |

Difficultés (`MAPINFO`) : facile (dégâts reçus × 0,6), normal, difficile (× 1,4) ; certaines apparitions filtrées
par niveau. Coups nécessaires : infirmier 4 balles de Browning ou 2 de FAL ; brancardier 10 ou 6 ; porte-registre 7
ou 4.

## 2. Pied-de-biche (mêlée)

Choix d'adaptation (contrat RF2-MAP-02-REPRISE, §6) : un pied-de-biche d'atelier, pas un objet du roman. Images
d'Astra (lot `RF2_MAP_02_REPRISE`, cinq poses, manche du sweat noir), `TEXTURES.crowbar` tel que proposé (même
toile et mêmes décalages que le FAL).

| Élément | Valeur |
|---|---|
| Emplacement | 3 (touches existantes ; jamais choisi automatiquement avant une arme à feu chargée) |
| Coup | armé 5 tics, frappe 3, impact 2 (le coup porte ici), suivi 4, retour 8 : ≈ 0,63 s |
| Dégâts | 45–55, portée de mêlée du moteur (64) ; infirmier en 2 coups, porte-registre en 2–3, brancardier en 4 |
| Risque | à portée des coups des infirmiers (44) et des brancardiers (64) ; aucune munition |
| Bruit | le geste n'alerte personne (`NOALERT`) ; la victime entend le coup |
| Interruption | pendant le retour, l'arme peut être rangée (pas relancée) |
| Sons | élan (3 variantes), chair, métal, bois (plâtre : coup sourd du bois) : propositions d'Astra converties en 16 bits, **jamais écoutées** ni par Astra ni par Opus |
| HUD | nom « Pied-de-biche », aucun compteur |

**Où** : couché sur le gravier, juste à l'intérieur du porche de Cochin, à côté de la ligne de l'infirmière, visible
depuis le boulevard par la porte ouverte (modèle d'Astra, 24,6 u). Ramassage ordinaire (« Un pied-de-biche. »). Un
départ direct de RF02 ne le donne pas (Viktor le trouve à Cochin, tôt dans le parcours, comme en campagne) ; les
chapitres suivants, lancés seuls, le donnent avec le Browning et le FAL. Écart assumé avec le contrat, qui prévoyait
de le donner au lanceur de revue.

**Essais en jeu** (sonde scriptée dans RF02, joueur invulnérable, cibles : infirmiers rendus amicaux et immobiles,
puis un infirmier hostile qui avance) :

| Cas | Résultat |
|---|---|
| Ramassage, puis toutes munitions retirées | pied-de-biche en main, il frappe sans munitions |
| Coup dans le vide | aucun impact |
| Contre la carrosserie d'une ambulance | un impact (son de bois pour les surfaces minérales, métal pour le métal) |
| Cible à 40 u | 48 dégâts, morte au second coup |
| Cible à 100 u | intacte (hors de portée) |
| Paroi du tram entre le joueur et la cible (42 u) | intacte |
| Changement d'arme demandé pendant le retour | l'arme descend 3 tics après la demande, avant la fin du geste |
| Cible mobile (infirmier hostile qui s'approche) | touché à 51 u, puis tué à 57 u |
| Sauvegarde, relance du moteur, chargement | le pied-de-biche est toujours dans l'inventaire |

Réglage issu des essais : le recul du coup (`Kickback`) passe de 90 à 30 ; à 90, un infirmier était repoussé d'environ
50 u, hors de portée du second coup.

À faire : retouches de ressenti des armes à feu (propositions sonores d'Astra à comparer), reprise des rencontres,
mesures de difficulté par rencontre (parcours normal et parcours avec erreurs). Limite : couché, le pied-de-biche est
discret vu du boulevard (fine ligne sombre sur le gravier) ; à juger en jeu.
