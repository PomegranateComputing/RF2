# Banc des familles d'ennemis (hors campagne)

Une salle, six postes, une famille à la fois. Le banc sert à recevoir une famille dessinée (les trois en jeu, puis
les nouvelles) avant toute carte : on y voit ses huit vues, sa marche, ce qu'elle franchit, son attaque, sa douleur,
sa mort et son corps, et le banc mesure ses cadences.

Lancer : `JOUER_RF2_BANC_FAMILLES.cmd` (l'infirmier au départ). En jeu, les trois dalles de bois au sud de la salle
changent de famille : 1 infirmier, 2 brancardier, 3 porte-registre. Le joueur est un observateur : rien ne le vise,
rien ne le blesse.

| Poste | Où | Ce qu'on y voit |
|---|---|---|
| Rotations | deux arcs au nord de la dalle de bois centrale ; se tenir sur la dalle | arc proche : les huit vues debout ; arc lointain : marche, attaque et douleur jouées dans les huit vues |
| Marche | à l'ouest | un spécimen fait l'aller-retour entre deux points à 512 u ; vitesse mesurée |
| Obstacles | à l'est, derrière la rambarde | un pilier, une marche de 24 u, des portes de 96, 64 et 48 u ; le banc dit ce qui est franchi et où le spécimen s'arrête |
| Attaque | au nord-est, dans l'enclos | un spécimen frappe un poteau : poses jouées, tic du coup ou du tir |
| Douleur | au nord-ouest | un spécimen touché toutes les quatre secondes |
| Mort et corps | au nord-ouest | un spécimen tué, son corps laissé six secondes, puis remplacé |

Les mesures s'affichent en haut de l'écran et s'écrivent dans le journal (`RF_BANC …`). Une pose se lit « lettre et
tics » : `F10,G4,H14` = pose F dix tics, G quatre, H quatorze.

## Contrôle à la réception d'une famille

`python bench/familles/test_family_bench.py <dossier du banc>` met chaque famille sur le banc, attend le bilan et
compare les mesures à `contrats.json` (les cadences que le jeu joue aujourd'hui). **De nouvelles images ne doivent rien
y changer** : un écart est un refus, sauf décision du propriétaire reportée dans `contrats.json`.
Résultats et images : `<dossier du banc>/preuves/RESULTATS.md`, `test_familles.json`, `<Classe>_NN_<poste>.png`.

## Une nouvelle famille

Elle arrive comme un module (sprites, classe ZScript) chargé après le banc ; sa classe est nommée au lancement :

```
set RF2_BANC_CLASSE=RFNouvelleFamille
JOUER_RF2_BANC_FAMILLES.cmd -file chemin\du\module.pk3
python bench/familles/test_family_bench.py <dossier du banc> RFNouvelleFamille --module chemin\du\module.pk3
```

Sans ligne dans `contrats.json`, le contrôle vérifie seulement que les six postes donnent une mesure et qu'aucune
erreur de script n'apparaît ; la ligne du contrat est écrite une fois les cadences décidées.

## Construire

```
python bench/familles/materials_famille.py      le poteau (sprite du banc)
python bench/familles/famille_map.py            la carte FAM01
python bench/familles/build_family_bench.py --base <build figé> --root-launcher
```

Le banc ne modifie ni `src/`, ni la campagne, ni les sauvegardes de la partie normale (configuration, sauvegardes et
journaux dans `user\…_banc_familles`).
