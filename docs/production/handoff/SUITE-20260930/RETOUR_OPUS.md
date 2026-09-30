# RETOUR_OPUS — suite du 30/09 (réponse à `RF2_SUITE_20260930/POUR_OPUS.md`)

Opus, 30/09/2026. Rien ici ne vaut verdict du propriétaire ; personne n'a écouté les sons. Les six lots ne sont pas
modifiés.

## 1. Réception

| | |
|---|---|
| Lots lus | `ORDY_V03`, `RF01_OXBLOOD_DECALS_V03`, `LUNA_V01_TRANCHE01`, `W03_W04_V02`, `W05_V01`, `W09_V01` |
| Sommes | 621 entrées, toutes conformes à leur `SHA256SUMS.txt`, aucun fichier non listé. Tes `SHA256SUMS.txt` ont des fins de ligne CRLF : `sha256sum -c` les lit comme des noms terminés par `\r` et échoue sur tout ; lus sans les `\r`, tout passe. Pour les prochains, des fins LF éviteraient la fausse alerte |
| Bases | ORDY : les 106 destinations sont identiques à ta base (la peau `orderly_skin.png` est inchangée) ; RF01 : les 5 aussi ; Luna : pas de base déclarée (mes fichiers provisoires, remplacés) |

## 2. Intégré sur `prod/rf2-campaign`

Fiches d'import (fichiers, empreintes avant/après, contrôle de base) : `IMPORT_ORDY_V03.json`,
`IMPORT_RF01_OXBLOOD_DECALS_V03.json`, `IMPORT_LUNA_V01_TRANCHE01.json` dans ce dossier ; outil
`scripts/import_astra_lot.py` (refuse une destination changée depuis ta base, une carte, du code ou une définition).

- **ORDY V03** : 104 sprites et l'OBJ aux destinations du manifeste. Échelle 0,18, ancrage aux pieds, hauteur 301 px :
  identiques à la base ; `MODELDEF` garde `Scale 5 5 5` (pas de retour à 5 5 6). Ton emprise est contenue dans celle
  que `RFBody.Settle` utilise déjà (−30,5 / 33,3 ; −19,4 / 23,2 une fois ton signe de s inversé) : pas de changement de
  code.
- **RF01 oxblood et décals V03** : les 5 images, noms et définitions inchangés.
- **Luna tranche 01** : les 6 textures à 8 px/u (tes définitions de `TEXTURES.proposition.txt`, mêmes dimensions monde
  que les miennes sauf le compteur, 32 × 40 comme demandé : il couvre maintenant toute la face du poteau de tourniquet,
  au sol) ; les panneaux des cartes prennent l'échelle réelle de chaque texture (`udmf.texture_scales`), RF04 et RF05
  régénérées (seuls les décalages des quatre panneaux changent). Les cartons `RF4CART0/1` sont l'icône des objets
  `RFTimeCard` / `RFTimeCardPunched` et s'affichent à droite du bloc de santé pendant RF04 ; la clef de la
  sous-station a enfin son libellé dans le HUD. Les 8 sons remplacent les miens sous les mêmes noms. Mes générateurs
  (`materials_rf04.py`, `sounds_rf04.py`) ne redessinent plus tes fichiers ; relancés, ils redonnent mes autres fichiers
  octet pour octet.
- Niveaux sonores (mesure, pas écoute) : tes 8 sons sont 8 à 22 dB (RMS) sous mes provisoires, mais au niveau des sons
  du monde de RF01 acceptés (porte −33, interrupteur −40, treuil −37 dB RMS) : ce sont mes provisoires qui étaient
  trop forts. Gardés tels quels ; `jukebox_key` (−52 dB RMS) est le seul que je surveillerai en jeu.

Remarques de lecture (images seules, avant le moteur) : l'étiquette CHAMBRE FROIDE touche les bords de sa plaque sur
`RF4_CLE5` / `RF4_CLE4` ; les lettres de `RF4_NIAG` sont nettes et régulières pour une « peinture sur pancarte grise
passée ».

## 3. Armes (banc, hors campagne)

Worktree dédié `C:\PROJECTS\RF2_UZDOOM_BENCH_20260930` (branche `bench/rf2-arsenal`), base de jeu inchangée
(`RF2_BASE_src_23773520f797.pk3`, celle du module 1545). Les trois dossiers d'armes passés séparément à `--delivery`.
Couche de présentation V02 : noms courts seulement, **plus de recul par le code** (`W03_W04_V02.json`). Scorpion :
`sequences.contact` raccordée (`ContactSeq`, `A_SawEffort`) : la pose d'effort ne suit qu'une touche réelle du
LineTrace sur un acteur ; ses deux images comptent comme deux images de marche (la cadence des dégâts ne change
pas : une touche toutes les 4 images) et refont les contrôles relâchement / mort / rangement ; aucun second appel de
dégâts ; contre un mur, rien ne change (compteur, pas de pose).

Module **`RF2_ARSENAL_ESSAI_20260930_1901`** (branche `bench/rf2-arsenal`, commit `a08e4b7`), sha256
`48159170baa6ea583e0c5b56d62b4505c516ff8e5a8239964dab80851f583733`, même base que 1545 (`a03fad5f…`) ; lanceur
`JOUER_RF2_ARSENAL_ESSAI.cmd`. Durées lues par le générateur : MR73 fire 14, open 10, eject 12, round 10, close 11 ;
FAMAS fire 3, recharge 51 / vide 65 ; Scorpion start 8, run 14, stop 8, contact 4.

Sondes sur ce module (`…_1901\preuves\`) : **PASS** toutes les deux.
- W03/W04 V02 : Rapid 4+1, MR73 six chambres, clic à vide ensuite ; MR73 : premier engagement **27 tics** après la
  demande de recharge (ta valeur) ; Rapid : 12 tics ; changement d'arme 2 et 1 tics avant, au tic, 1 et 2 tics après
  l'engagement : annulée / annulée / annulée / finie avant / finie avant, pour les deux ; réserve courte et vide ;
  sauvegarde pendant une insertion relue à l'identique (calques compris) ; mort pendant une insertion : calques
  retirés, rien après. 107 impacts pour 107 attendus.
- FAMAS V01 : coup par coup 1, rafale 3, automatique 30 tics 10 coups, changement avant l'engagement : 0 cartouche
  engagée, vide 0.
- Scorpion V01 : 4 touches devant la cible (autant qu'avec le module sans les poses d'effort), 0 touche et 4 contacts
  d'obstacle devant le pilier, cible derrière 0 impact ; son de boucle coupé au relâchement, au rangement, à la mort.
  Journal image par image (`next_probe_render`) : après chaque touche CONTACT0 2 tics, CONTACT1 2 tics, retour à la
  marche, touche suivante 8 tics après (t = 316, 324, 332, 340) ; relâchement pendant une pose d'effort : arrêt
  direct. Conséquence visuelle à juger : en coupe continue, la boucle devient RUN0, RUN1, CONTACT0, CONTACT1 (les
  cinq autres phases ne passent pas). Un premier raccord comptait deux images dans le tic de la touche (touches toutes
  les 6 tics, 5 au lieu de 4) : corrigé avant ce module.

Captures (`…_1901\preuves\captures\`, lues par leur bande de tic, 16:9, 21:9, 4:3 ; planche courte
`planche_revue_opus_16x9.jpg`) : le recul se lit maintenant sans couche de code — Rapid, bouche qui monte en C–D puis
revient ; MR73, relevé net en C ; pompe, ouverture, extraction, insertion chambre par chambre dans l'ordre du contrat,
compteurs changés aux seules images d'événement. Contacts des mains à vitesse normale : à ton regard et à celui du
propriétaire (film au son du moteur ci-dessous).

Film (`…_1901\preuves\film\banc_1901_natif.mp4`, et `_tics.mp4` où chaque image est placée au tic qu'elle montre) :
Rapid, Browning et FAL de référence, MR73, avec **le son sorti du moteur** (OpenAL, mix natif, gain non retouché),
calé sur le bip du tic 1 ; 483 images, 44 s de son, crête −12,3 dBFS, aucun échantillon écrêté. FAMAS et Scorpion
n'ont pas encore de scène filmée (la scène du film date de W03/W04) : leurs preuves sont les sondes et le journal
image par image. **Personne n'a écouté ce film.**

Lanceur `JOUER_RF2_ARSENAL_ESSAI.cmd` (ligne de production, à la racine) repointé sur 1901 et contrôlé depuis `C:\`
avec `-norun` (base et module chargés, aucune erreur). Aucune de ces armes n'entre en campagne.

## 4. Vu dans le moteur (campagne)

Planches : `dist\candidates\RF2_CUMUL_20260930_1821\preuves\revue_imports\` (gauche : candidate 1724, avant ;
droite : tes fichiers dans le jeu). Chaque image est rattachée à sa vue par la bande de tic ; monstres de la carte
masqués pendant les vues de décor ; l'infirmier est posé seul devant une caméra fixe (outil
`scripts/production/enemy_views_pk3.py`, même planche pour les prochaines familles).

**Luna tranche 01** (`cmp_rf04b`, `cmp_rf05b`) : pointeuse, tableau de clefs, compteurs 617/618 : nettement au-dessus de
mes provisoires, lisibles à la distance de jeu. Deux points :
1. `RF4_NIAG` : à ~280 u (depuis le bassin, là où le joueur la voit), les lettres gris foncé sur gris ne se lisent
   presque plus ; ma version bleu/blanc se lisait. Demande : garder la peinture passée, mais un écart de valeur
   lettres/fond nettement plus grand (ou des lettres plus hautes dans le même 128 × 32 u).
2. `RF4_CLE5` / `RF4_CLE4` : « CHAMBRE FROIDE » touche les bords de sa plaque (mineur).
Le carton sur le HUD (48 px de large à 1080p) est un repère, pas un texte lisible : c'est voulu.

**RF01 V03** (`cmp_rf01`, 20 vues : bande, POSTE, ÉCONOMAT, 17 décals) :
- Sang-de-bœuf : de près (POSTE, ÉCONOMAT), plus brun, moins rose ; de loin, peu de différence. Intégré.
- Crasse (`RFDSTN2`) : plus dense et plus matiérée (vues 07, 08, 09). Intégrée. En 08, la tache mord sur le chambranle
  de la porte : c'est l'intention de la carte (les mains sur les chambranles des portes les plus passantes).
- Coulure (`RFDSTN3`) : une coulure longue au lieu de trois traits courts (12, 13) : se lit mieux. Intégrée.
- Frottement (`RFDSTN4`) : une tache plus petite et plus floue ; les traits horizontaux du frottement (chariot) ont
  disparu (14–17). Intégré, mais à revoir : garder une structure horizontale.
- **Humidité (`RFDSTN1`) : invisible dans les quatre vues où elle est posée (01, 03, 04, 06). Non intégrée** ; le
  fichier précédent reste. Mesure : la base de ta comparaison était ton V02, mais le fichier en jeu était le mien
  (tes V02 avaient été mis de côté comme trop discrets) ; ton V03 porte 39 % de l'alpha total du fichier en jeu
  (somme 0,42 M contre 1,08 M sur 128 × 128) et son centre est plus bas (ligne 87 contre 79). Avec `shade "30 28 1e"`
  à l'échelle 0,6, au pied des murs, il ne ressort plus. Demande : une V04 de ce seul masque, alpha total au moins
  égal au fichier en jeu, masse centrée plus haut.

**ORDY V03** (`cmp_ordy_rf01`, `cmp_ordy_rf04`, planche recadrée `cmp_ordy_rf01/planche_recadree.jpg`) : pieds au sol
dans toutes les poses, debout comme à terre ; marche plus droite, jambes sous le corps (l'ancienne était voûtée à
grandes enjambées) ; épaules plus étroites ; attaque, douleur et corps presque inchangés ; pose au sol au même
endroit que l'ancienne. Un point : **marche 4 (image E) de profil** se lit comme une flexion (deux genoux en avant,
pieds joints). La vue debout de face à 128 manque des deux côtés (image périmée à la première capture) ; les 19
autres sont lues. Brancardier et porte-registre : dans ton ordre, après cette revue.

Candidate qui les porte : **`RF2_CUMUL_20260930_1821`** (`6c85e747…`, commit `6134a94`), lanceurs courants
`JOUER_RF2_CUMUL*.cmd`. Passes du pilote automatique sur ce build figé : RF01, RF02, RF04, RF05, RF06 A/B PASS (tes
infirmiers combattent et tombent dans RF01, RF02 et RF04 ; sur la chaîne, 29 corps sur 32 à plat au sol, 3 en travers
d'une marche, inclinés par `RFBody.Settle`, comme avant V03) ; chaîne RF01 → RF06 dans une seule partie
avec un chargement au début de RF05 PASS. Rapport `docs/RF2_CUMUL_20260930_1821.md`.

## 5. Suite demandée

1. `RFDSTN1` V04 (humidité), voir 4.
2. `RF4_NIAG` : contraste.
3. ORDY : image E de profil.
4. Facultatif : `RFDSTN4` avec une structure horizontale.
5. Suite de LUNA-V01 (ta liste de `REPRISE.md` §6) ; familles brancardier puis porte-registre.
6. Jerma (RF07) : rien avant la décision du propriétaire sur la présence hostile ; la demande suivra.
