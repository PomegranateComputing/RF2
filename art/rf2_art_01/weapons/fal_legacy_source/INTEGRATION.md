# FAL — contrat de raccordement pour Fable

Ces données sont une proposition. Aucun fichier moteur n'est produit ou modifié.

Les 21 chemins `target_relpath` du manifeste sont relatifs à `src/`.
Les noms longs `RF2_...png` satisfont le contrat ASTRA mais ne constituent pas à
eux seuls des noms de sprites Doom. Fable doit déclarer explicitement les alias
de `animation.json` lors de l'intégration ; une copie des PNG seule est insuffisante.
Les alias RFLV A0..T0 sont proposés, RFMZ A0 pour le flash : vérifier les collisions
avant raccordement aux états du nouvel acteur.

Canvas constant 1536×1024, RGBA8, alpha droit. Transformation des calques en alpha
prémultiplié, conversion en alpha droit à l'export. Le point de référence et le
chunk PNG grAb sont identiques : (-700, -300). Proposition héritée du legacy :
XScale 6, YScale 7.2, dimensions logiques 256×142.222. Ces valeurs ne constituent
pas un test de cadrage dans la baseline RF01 ; vérifier 16:9, 16:10 et HUD agrandi.

Ordre ready A ; tir B, recul C, retour D ; recharge E..T. Durées en tics de 1/35 s
dans `animation.json` : propositions visuelles, aucune règle de gameplay imposée.
La fin T est pixel-identique à A. Une recharge partielle peut sauter les poses
12..14 de manipulation du levier. L'engagement de munitions appartient à Fable.
Select/deselect peuvent utiliser READY avec déplacement vertical du moteur.

FIRE ne contient aucun flash. Superposer RFMZ A0 au même offset pendant les deux
tics proposés de FIRE ; pas de flash sur RECOIL_MAX ou READY. La lumière moteur,
les impacts et les éjections ne sont pas encodés dans les sprites. Les mentions
sonores du legacy sont des références documentaires, pas des sons disponibles
ou des identifiants garantis dans la baseline.

La source locale suffit à reconstruire les PNG. `prepare_sources.py` sert seulement
à retracer la récupération initiale depuis le legacy. Les anciens scripts aux chemins
obsolètes restent archivés comme `.py.txt` et ne doivent pas être exécutés.
Le rig conserve le master, la caméra, la palette et la géométrie entre les frames ;
la réparation de prise du chargeur réutilise la manche du FAL. Les petites fentes
des masques legacy sont également refermées au niveau des calques ; le corps et
le logement reçoivent un chevauchement d'un pixel pour éviter les coutures claires.
Les couleurs de bord proviennent des voisins opaques, jamais d'un fond noir.

Revue restante : fermeture des doigts sur le chargeur, jonction poignet/manche,
contact avec le levier, contours sur murs clairs, continuité en boucle, cadrage et
cohérence de matière face aux candidats ennemis. Le statut reste propriétaire à revoir.
