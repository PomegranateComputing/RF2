# Démarrage et édition — toutes les opérations dans C:\PROJECTS

## A. Extraction

Dans l'Explorateur : clic droit sur le ZIP, **Extraire tout**, destination `C:\PROJECTS`.
Résultat attendu : `C:\PROJECTS\RF2_UZDOOM_MAPS_V1\00_LIRE_MOI.md`.
Si l'outil d'extraction a ajouté un dossier identique imbriqué, déplacer le dossier intérieur directement sous `C:\PROJECTS`.

## B. Premier démarrage

Double-cliquer `JOUER.cmd`. Il appelle `PREPARER.cmd` si les dépendances manquent. La préparation utilise PowerShell fourni par Windows et ne demande ni Python ni un achat Doom. Les archives téléchargées sont conservées dans `downloads` avec contrôle SHA-256.

Pour préparer séparément dans PowerShell :

```powershell
Set-Location 'C:\PROJECTS\RF2_UZDOOM_MAPS_V1'
.\PREPARER.cmd
.\JOUER.cmd
```

Le lanceur ouvre le titre en 1920×1080 fenêtré. Les options natives permettent d'ajuster affichage, audio et touches ; elles sont conservées dans `userdata\rf2.ini`. L'autoload global est désactivé pour éviter qu'un mod installé ailleurs change ce test.

Si le téléchargement échoue, lire le message et relancer `PREPARER.cmd` lorsque l'accès à GitHub fonctionne. Si un ZIP existant échoue au contrôle de hash, renommer **ce seul ZIP** dans `downloads` ; ne supprimer aucun projet. Si une politique d'entreprise interdit PowerShell, utiliser l'installation manuelle ci-dessous, sans modifier cette politique.

## C. Installation manuelle, sans script de téléchargement

1. Télécharger l'archive Windows x64 d'[UZDoom 5.0.1](https://github.com/UZDoom/UZDoom/releases/tag/5.0.1).
2. Extraire tous ses fichiers dans `C:\PROJECTS\RF2_UZDOOM_MAPS_V1\runtime`. `uzdoom.exe` et `uzdoom.pk3` doivent être directement dans ce dossier, avec les DLL et autres ressources de la distribution.
3. Télécharger [Freedoom 0.13.0](https://github.com/freedoom/freedoom/releases/tag/v0.13.0). Placer `freedoom2.wad` et ses notices dans `C:\PROJECTS\RF2_UZDOOM_MAPS_V1\iwads`.
4. Lancer `JOUER.cmd`.

Avec son propre Doom II, copier son `doom2.wad` dans `iwads` et utiliser :

```powershell
Set-Location 'C:\PROJECTS\RF2_UZDOOM_MAPS_V1'
.\runtime\uzdoom.exe -noautoload `
  -iwad '.\iwads\doom2.wad' `
  -file '.\build\RF2_MAPS_V1.pk3' `
  -config '.\userdata\rf2-doom2.ini' `
  -savedir '.\userdata' +map RF01
```

Le chemin avec Freedoom reste le test de référence prévu par `JOUER.cmd`.

## D. Jouer les cartes

Choisir **Nouvelle partie**. Les cartes se succèdent de RF01 à RF23. L'interaction est la commande native **Utiliser** (Espace dans la configuration Doom courante ; consulter Options → Personnaliser les commandes pour le binding effectif).

Le panneau `SORTIE` derrière la porte bleue s'active avec Utiliser. Chercher la carte bleue dans une branche latérale, puis revenir vers la sortie. Les deux alcôves secrètes de chaque carte ont un panneau mural utilisable. Saut et accroupissement sont désactivés par les cartes ; toutes les progressions prévues passent à pied, avec marches de 16 unités.

`CHOISIR_CARTE.cmd` affiche les titres et demande un nombre entre 1 et 23. Ce lancement direct démarre sans l'inventaire accumulé ; des armes et ressources de test sont placées au début de RF01–RF22. RF23 ne comporte aucun ennemi, arme ni stock de munitions placé.

Console de diagnostic : `map RF09` ouvre la piscine ; `map RF18` ouvre Gennevilliers. Ne pas utiliser `noclip` ou donner une clé pour déclarer un parcours validé.

## E. Intégrer au projet vivant RF2_UZDOOM

Le test séparé ci-dessus doit être la première action. Les identifiants **RF01–RF23** évitent d'écraser des cartes `MAPxx` existantes par simple homonymie. Le MAPINFO de ce pack définit volontairement la nouvelle campagne et son entrée RF01.

L'agent de production peut importer `maps`, les textures `RF*` et les définitions RFxx dans `C:\PROJECTS\RF2_UZDOOM`. Il doit fusionner le MAPINFO avec celui du vrai FPS et vérifier l'ordre de chargement. Ne pas charger aveuglément deux systèmes de campagne concurrents.

Le pack utilise des numéros Doom II standards pour la démonstration. Les remplacements RF2 hérités fonctionnent s'ils remplacent ces classes ; sinon, remapper les things vers les numéros réels de RF2. Voir `INTEGRATION_ACTEURS.md`. Les anciens sprites d'armes ne sont ni présents ni remplacés dans cette archive.

La suppression de l'ancien dossier RF2 relève de la migration vérifiée sur le PC. Cette archive de nouvelles maps ne contient pas l'ancien projet et ne fournit aucune commande de suppression fondée sur un chemin supposé.

## F. Éditer dans Ultimate Doom Builder

1. Ouvrir `maps\RF01.wad` (ou une autre carte).
2. Choisir la configuration **GZDoom: Doom 2 (UDMF)**, compatible avec le namespace `zdoom` employé ici.
3. Ajouter `iwads\freedoom2.wad`, puis le dossier `resources` comme ressources d'édition. Ne pas ajouter le PK3 de build : il contient une autre copie des cartes.
4. Configurer UZDoom 5.0.1 comme moteur de test. Paramètres de test : IWAD Freedoom2, ressources du pack, carte courante. Les libellés exacts du dialogue dépendent de la version de l'éditeur.
5. Enregistrer le WAD ; UDB reconstruit ses nœuds avec sa chaîne configurée.
6. Synchroniser les sources et recréer le PK3 avec Python 3.10+ :

```powershell
Set-Location 'C:\PROJECTS\RF2_UZDOOM_MAPS_V1'
py -3 '.\tools\sync_from_wads.py'
py -3 '.\tools\validate_pack.py'
.\JOUER.cmd
```

Si l'édition porte directement sur `src\RFxx\TEXTMAP`, utiliser `tools\repack.py`. Cela crée des WAD sans anciens nœuds périmés ; UZDoom peut les reconstruire au chargement. Pour une livraison, reconstruire aussi les nœuds dans UDB/ZDBSP.

`tools\build_maps.py` est le générateur initial. **Ne pas le relancer après édition manuelle sans vouloir régénérer les 23 cartes** : il remplace TEXTMAP, WAD et plans. Le drapeau explicite `--regenerate` est requis. `layout.json` et l'atlas décrivent cette génération V1 ; après édition UDB, actualiser ces documents si le plan change.

## G. Validation Windows à consigner

- Démarrage du titre, Nouvelle partie, difficulté, chargement RF01.
- Pour chaque carte : départ, carte bleue, porte depuis ses deux faces, deux secrets, panneau de sortie, chargement de la suivante.
- Sauvegarder en milieu de parcours ; quitter, relancer, charger et terminer.
- Vérifier mort/reprise, options persistantes, ressources absentes et collisions.
- Sur RF23 : sortie vers l'écran final, aucun chargement RF24.

Renseigner `evidence\WINDOWS_ACCEPTANCE.csv` avec observations réelles. Le rapport livré ne coche pas ces tests à la place du PC de jeu.
