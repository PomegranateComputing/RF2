# RF2 — architecture de production

## Source de vérité runtime

`src/` uniquement.

`legacy/` et `campaign/blockouts_v1/` sont des références, jamais des dépendances runtime directes.

## Responsabilités

- Fable : code, cartes, intégration, UI runtime, tests.
- Astra : génération d'assets dans `incoming/astra` uniquement.

## Carte canonique

Chaque map de production vit dans `src/maps/RFxx.wad`.

Le WAD UDMF de `campaign/blockouts_v1/maps/RFxx.wad` reste inchangé pour comparaison.

## Build

`src/` est empaqueté en `dist/RF2_DEV.pk3`.

Les WAD sous `src/maps/` sont chargés comme cartes internes du PK3.

## Dépendances de dev

- UZDoom 5.0.1.
- Freedoom 0.13.0 comme IWAD de développement redistribuable séparément.
- Ultimate Doom Builder pour l'édition visuelle des WAD UDMF.

## Politique de modernisation

Nouveau gameplay : ZScript prioritaire.

Legacy fonctionnel : ne pas réécrire avant nécessité réelle.

## Politique de progression

RF01 devient le vertical slice / standard. RF02–RF23 sont ensuite transformées, pas régénérées.
