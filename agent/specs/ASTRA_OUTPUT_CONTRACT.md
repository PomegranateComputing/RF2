# Contrat de sortie Codex Astra

## Zone autorisée

Astra écrit uniquement sous :

`incoming/astra/<BATCH_ID>/`

Il ne modifie jamais `src`, `campaign`, `legacy`, `scripts` ni les WAD.

## Structure obligatoire

```text
<BATCH_ID>/
  manifest.json
  README.md
  source/
  runtime/
  evidence/
```

Les dossiers peuvent être vides si non applicables, mais `manifest.json` et `README.md` sont obligatoires.

## Manifest

Chaque fichier runtime comporte :

- `file` : chemin relatif dans le batch ;
- `target_relpath` : destination souhaitée sous `src/` ;
- `kind` ;
- `sha256` ;
- `bytes` ;
- dimensions/format si pertinent ;
- `source_method` ;
- `license_or_origin` ;
- `confidence` ;
- `notes`.

Le statut global doit rester `ASTRA_GENERATED` ou `OWNER_REVIEW_REQUIRED`. Astra ne peut pas s'auto-déclarer « final approved ».

## Formats runtime recommandés

Images : PNG RGBA pour sprites/UI, PNG pour textures de blockout/prod si adapté.

Audio : WAV PCM 48 kHz, 24-bit si l'outil le permet ; mono pour source ponctuelle, stéréo pour ambiance lorsque justifié.

3D source : BLEND/FBX/GLB selon pipeline, mais livrer aussi le rendu runtime réellement exploitable.

## Nommage

Préfixe : `RF2_`.

Pas d'espaces dans les noms runtime.

Exemples :

`RF2_FAL_FIRE_A0.png`
`RF2_ENA_WALK_A1.png`
`RF2_SA_TILE_01.png`
`RF2_FAL_SHOT_CLOSE.wav`

## Interdits

- fichiers runtime sans manifeste ;
- texte illisible baked dans l'art UI ;
- huit images d'un acteur générées indépendamment sans master cohérent ;
- écrasement direct d'un asset existant ;
- téléchargement de packs tiers sans provenance/licence explicite ;
- « final » auto-proclamé.
