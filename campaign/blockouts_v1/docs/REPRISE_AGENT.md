# Reprise de production — nouvelles maps RF2

Le propriétaire a explicitement remplacé la recherche des anciennes cartes par la création de nouvelles. Ce pack répond à ce mandat. Projet : FPS UZDoom adaptant La Couleur de la Grenade ; distinct de RF1 et de Sans Destination. Personnage : Viktor Ardent. FN FAL obligatoire dans le FPS final.

Ouvrir `00_LIRE_MOI.md`, `evidence/DELIVERY_REPORT.md`, `CANON_ET_ADAPTATION.md`, `INTEGRATION_ACTEURS.md`. Ne pas présenter les contrôles statiques comme un parcours joueur déjà exécuté.

Priorité immédiate : préparer le runtime, démarrer RF01 avec les fichiers fournis, corriger toute erreur observable, terminer la carte par les commandes normales, puis vérifier RF01–RF23. Passer ensuite le FAL, le PlayerPawn et les ennemis réels du FPS dans le contrat d'acteurs. Aucune nouvelle dépendance n'est nécessaire pour lire ou éditer les maps.

Les WAD et leurs TEXTMAP sont les sources de travail à préserver. Le générateur est un outil de création V1 ; ne pas écraser une édition manuelle en le relançant. Importer dans `C:\PROJECTS\RF2_UZDOOM` après un premier test séparé. Conserver les bons assets existants du FPS.

La géométrie V1 est un blockout texturé orthogonal. La prochaine passe de level design doit renforcer la silhouette propre à chaque lieu, les vues entre espaces et la scénographie des rencontres. L'éclairage, les props détaillés, le combat réel avec le FAL, l'audio spécifique et la durée observée restent des tâches de production. Ne pas inventer une validation artistique du propriétaire.
